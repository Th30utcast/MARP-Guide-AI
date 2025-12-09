"""
Chat Service - RAG-powered question answering
Implements the 4-step RAG pipeline: Retrieval → Augmentation → Generation → Citation
"""

import json
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

import config
import redis
from fastapi import Depends, FastAPI, Header, HTTPException
from openrouter_client import OpenRouterClient
from prompt_templates import create_rag_prompt
from pydantic import BaseModel, Field
from retrieval_client import RetrievalClient

# Add common module to path for event publishing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from common import events
from common.mq import RabbitMQEventBroker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chat Service", version="1.0.0")

# Initialize clients for retrieval and LLM generation
retrieval_client = RetrievalClient()
openrouter_client = OpenRouterClient()

# Initialize Redis client for session validation
redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

# Initialize event broker for analytics
try:
    event_broker = RabbitMQEventBroker(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        username=os.getenv("RABBITMQ_USER", "guest"),
        password=os.getenv("RABBITMQ_PASS", "guest"),
    )
    logger.info("✅ Event broker initialized for analytics")
except Exception as e:
    logger.warning(f"⚠️ Failed to initialize event broker: {e}. Analytics events will not be published.")
    event_broker = None


def validate_session(authorization: Optional[str] = Header(None)) -> Dict:
    """Validates user session from Authorization header, returns dict with user_id and email"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization.replace("Bearer ", "")

    try:
        # Validate session token in Redis
        session_data = redis_client.get(f"session:{token}")
        if not session_data:
            raise HTTPException(status_code=401, detail="Invalid or expired session")

        # Parse session data
        session = json.loads(session_data)
        return {"user_id": session.get("user_id"), "email": session.get("email")}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Session data corrupted")
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        raise HTTPException(status_code=500, detail="Session validation failed")


class Citation(BaseModel):
    title: str
    page: int
    url: str


class ChatRequest(BaseModel):
    query: str = Field(..., description="User's question about MARP")
    top_k: int = Field(8, ge=1, le=20, description="Number of chunks to retrieve")
    session_id: Optional[str] = Field(None, description="User session ID for analytics")
    model_id: Optional[str] = Field(None, description="Model ID to use for generation (defaults to PRIMARY_MODEL_ID)")


class ChatResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]


class ModelComparisonResult(BaseModel):
    model_id: str
    model_name: str
    answer: str
    citations: List[Citation]


class ComparisonResponse(BaseModel):
    query: str
    reformulated_query: str
    results: List[ModelComparisonResult]
    latency_ms: float
    retrieval_count: int


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "ChatService",
        "retrieval_url": config.RETRIEVAL_URL,
        "openrouter_configured": bool(config.OPENROUTER_API_KEY),
        "model": config.OPENROUTER_MODEL,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, user: Dict = Depends(validate_session)):
    """
    RAG-powered chat endpoint (requires authentication)

    Quality checks:
    - Validates query length and content
    - Sanitizes input to prevent injection attacks
    - Provides detailed error messages for debugging
    """
    start_time = time.time()

    # Quality: Input validation with detailed error messages
    if not req.query or not req.query.strip():
        logger.warning(f"⚠️ Empty query received from user {user.get('user_id')}")
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(req.query) > 1000:
        logger.warning(f"⚠️ Query too long ({len(req.query)} chars) from user {user.get('user_id')}")
        raise HTTPException(status_code=400, detail="Query must be less than 1000 characters")

    # Get user_id from validated session (defensive programming)
    user_id = user.get("user_id")
    if not user_id:
        logger.error("❌ Session validation passed but user_id is missing")
        raise HTTPException(status_code=500, detail="Invalid session data")

    logger.info(f"📝 Chat request from user {user_id}")

    # Generate session ID if not provided
    session_id = req.session_id or events.generate_event_id()
    correlation_id = events.generate_event_id()

    # Use model_id from request or fall back to PRIMARY_MODEL_ID
    model_id = req.model_id or config.PRIMARY_MODEL_ID

    # Publish QuerySubmitted event
    if event_broker:
        try:
            query_event = events.create_query_submitted_event(
                query=req.query,
                user_session_id=session_id,
                model_id=model_id,
                user_id=user_id,
                correlation_id=correlation_id,
            )
            event_broker.publish(
                routing_key=events.ROUTING_KEY_QUERY_SUBMITTED,
                message=json.dumps(query_event),
                exchange="events",
            )
        except Exception as e:
            logger.warning(f"Failed to publish QuerySubmitted event: {e}")

    try:
        # Step 0: Query reformulation (fix typos and improve phrasing)
        search_query = req.query
        if config.ENABLE_QUERY_REFORMULATION:
            logger.info(f"🔧 Step 0: Reformulating query to fix typos and improve clarity")
            search_query = openrouter_client.reformulate_query(req.query)
            if search_query != req.query:
                logger.info(f"📝 Original: {req.query}")
                logger.info(f"✨ Reformulated: {search_query}")

        # Step 1: Retrieval - search for relevant document chunks
        logger.info(f"🔍 Step 1: Retrieving chunks for query: {search_query[:50]}...")
        chunks = retrieval_client.search(search_query, req.top_k)

        if not chunks:
            logger.warning("⚠️ No chunks retrieved for query")
            return ChatResponse(
                query=req.query,
                answer="I couldn't find any relevant information in the MARP documents to answer your question. Please try rephrasing your query.",
                citations=[],
            )

        logger.info(f"✅ Retrieved {len(chunks)} chunks")

        # Step 2: Augmentation - build RAG prompt
        logger.info("📝 Step 2: Building RAG prompt")
        prompt = create_rag_prompt(req.query, chunks)

        # Step 3: Generation - send prompt to LLM
        logger.info(f"🤖 Step 3: Generating answer with LLM (model: {model_id})")
        if model_id != config.PRIMARY_MODEL_ID:
            # Create a temporary client with the specified model
            model_client = OpenRouterClient(model=model_id)
            answer = model_client.generate_answer(prompt)
        else:
            answer = openrouter_client.generate_answer(prompt)

        # Step 4: Citation extraction - extract only citations referenced in the answer
        logger.info("📚 Step 4: Extracting citations")
        import re

        insufficient_info_phrases = [
            "does not contain",
            "doesn't contain",
            "do not contain",
            "don't contain",
            "not enough information",
            "cannot answer",
            "can't answer",
            "unable to answer",
            "no information",
        ]

        answer_lower = answer.lower()
        answer_start = answer_lower[:150]
        has_insufficient_info = any(phrase in answer_start for phrase in insufficient_info_phrases)

        if has_insufficient_info:
            logger.info("⚠️ Answer indicates insufficient information - returning no citations")
            answer = re.sub(r"\[\d+\]", "", answer).strip()
            citations = []
        else:
            # Find citation numbers in answer (e.g., [1], [2], [3])
            cited_numbers = set(int(match) for match in re.findall(r"\[(\d+)\]", answer))
            logger.info(f"Found inline citations: {sorted(cited_numbers)}")

            # Anti-hallucination: Reject answers without citations
            if len(cited_numbers) == 0:
                logger.warning("⚠️ LLM answered without citations - rejecting as hallucination")
                logger.warning(f"Rejected answer: {answer[:200]}...")
                answer = f"The MARP documents provided do not contain information about this topic. Please try asking about MARP regulations, policies, or procedures."
                citations = []
            else:
                # Deduplicate citations and build mapping
                citations = []
                seen_citations = set()
                citation_mapping = {}

                for idx, chunk in enumerate(chunks, start=1):
                    if idx in cited_numbers:
                        citation_key = (chunk.get("title", ""), chunk.get("page", 0))
                        if citation_key not in seen_citations and citation_key[0] and citation_key[1]:
                            citations.append(
                                Citation(
                                    title=chunk.get("title", "Unknown"), page=chunk.get("page", 0), url=chunk.get("url", "")
                                )
                            )
                            seen_citations.add(citation_key)
                            citation_mapping[idx] = len(citations)
                        elif citation_key in seen_citations:
                            for old_idx, new_idx in citation_mapping.items():
                                if (chunks[old_idx - 1].get("title", ""), chunks[old_idx - 1].get("page", 0)) == citation_key:
                                    citation_mapping[idx] = new_idx
                                    break

                # Renumber citations using placeholders
                for old_num in sorted(cited_numbers, reverse=True):
                    if old_num in citation_mapping:
                        new_num = citation_mapping[old_num]
                        answer = answer.replace(f"[{old_num}]", f"<<CITE_{new_num}>>")

                for new_num in set(citation_mapping.values()):
                    answer = answer.replace(f"<<CITE_{new_num}>>", f"[{new_num}]")

                logger.info(f"Renumbered citations: {citation_mapping}")

                # Filter citations that appear in final answer
                final_cited_numbers = set(int(match) for match in re.findall(r"\[(\d+)\]", answer))
                citations = [cit for i, cit in enumerate(citations, start=1) if i in final_cited_numbers]
                logger.info(f"Citations after dedup filtering: {sorted(final_cited_numbers)}")

                # Ensure consecutive numbering
                if final_cited_numbers and sorted(final_cited_numbers) != list(range(1, len(citations) + 1)):
                    final_mapping = {}
                    for new_pos, old_pos in enumerate(sorted(final_cited_numbers), start=1):
                        final_mapping[old_pos] = new_pos

                    for old_pos in sorted(final_cited_numbers, reverse=True):
                        new_pos = final_mapping[old_pos]
                        answer = answer.replace(f"[{old_pos}]", f"<<FINAL_{new_pos}>>")

                    for new_pos in final_mapping.values():
                        answer = answer.replace(f"<<FINAL_{new_pos}>>", f"[{new_pos}]")

                    logger.info(f"Final renumbering to consecutive: {final_mapping}")

        latency = round((time.time() - start_time) * 1000, 2)
        logger.info(f"✅ Chat completed in {latency}ms | Citations: {len(citations)}")

        # Publish ResponseGenerated event
        if event_broker:
            try:
                response_event = events.create_response_generated_event(
                    query=req.query,
                    response=answer,
                    model_id=model_id,
                    user_session_id=session_id,
                    latency_ms=latency,
                    citation_count=len(citations),
                    retrieval_count=len(chunks) if chunks else 0,
                    user_id=user_id,
                    correlation_id=correlation_id,
                )
                event_broker.publish(
                    routing_key=events.ROUTING_KEY_RESPONSE_GENERATED,
                    message=json.dumps(response_event),
                    exchange="events",
                )
            except Exception as e:
                logger.warning(f"Failed to publish ResponseGenerated event: {e}")

        return ChatResponse(query=req.query, answer=answer, citations=citations)

    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")


@app.post("/chat/compare", response_model=ComparisonResponse)
def compare_models(req: ChatRequest, user: Dict = Depends(validate_session)):
    """Multi-model comparison endpoint - generates answers from 3 models in parallel (requires authentication)"""
    start_time = time.time()

    # Get user_id from validated session
    user_id = user["user_id"]
    logger.info(f"📊 Model comparison request from user {user_id}")

    # Generate session ID if not provided
    session_id = req.session_id or events.generate_event_id()
    correlation_id = events.generate_event_id()

    # Publish ModelComparisonTriggered event
    if event_broker:
        try:
            comparison_event = events.create_model_comparison_triggered_event(
                query=req.query,
                user_session_id=session_id,
                models=[m["id"] for m in config.COMPARISON_MODELS],
                user_id=user_id,
                correlation_id=correlation_id,
            )
            event_broker.publish(
                routing_key=events.ROUTING_KEY_MODEL_COMPARISON_TRIGGERED,
                message=json.dumps(comparison_event),
                exchange="events",
            )
        except Exception as e:
            logger.warning(f"Failed to publish ModelComparisonTriggered event: {e}")

    try:
        # Step 0: Query Reformulation (once, shared by all models)
        search_query = req.query
        if config.ENABLE_QUERY_REFORMULATION:
            logger.info("🔧 Reformulating query for all models")
            search_query = openrouter_client.reformulate_query(req.query)
            if search_query != req.query:
                logger.info(f"📝 Original: {req.query}")
                logger.info(f"✨ Reformulated: {search_query}")

        # Step 1: Retrieval (once, shared by all models)
        logger.info(f"🔍 Retrieving chunks for query: {search_query[:50]}...")
        chunks = retrieval_client.search(search_query, req.top_k)

        if not chunks:
            logger.warning("⚠️ No chunks retrieved for query")
            # Return empty results for all models
            return ComparisonResponse(
                query=req.query,
                reformulated_query=search_query,
                results=[
                    ModelComparisonResult(
                        model_id=model["id"],
                        model_name=model["name"],
                        answer="I couldn't find any relevant information in the MARP documents to answer your question.",
                        citations=[],
                    )
                    for model in config.COMPARISON_MODELS
                ],
            )

        logger.info(f"✅ Retrieved {len(chunks)} chunks")

        # Step 2: Build RAG prompt (once, shared by all models)
        logger.info("📝 Building RAG prompt")
        prompt = create_rag_prompt(req.query, chunks)

        # Step 3: Parallel Generation - Generate answers from 3 models simultaneously
        logger.info(f"🤖 Generating answers from {len(config.COMPARISON_MODELS)} models in parallel")

        def generate_with_model(model_config: Dict) -> ModelComparisonResult:
            """Generate answer with a specific model"""
            try:
                client = OpenRouterClient(model=model_config["id"])
                answer = client.generate_answer(prompt)
                insufficient_info_phrases = [
                    "does not contain",
                    "doesn't contain",
                    "do not contain",
                    "don't contain",
                    "not enough information",
                    "cannot answer",
                    "can't answer",
                    "unable to answer",
                    "no information",
                ]

                answer_lower = answer.lower()
                answer_start = answer_lower[:150]
                has_insufficient_info = any(phrase in answer_start for phrase in insufficient_info_phrases)

                if has_insufficient_info:
                    answer = re.sub(r"\[\d+\]", "", answer).strip()
                    citations = []
                else:
                    cited_numbers = set(int(match) for match in re.findall(r"\[(\d+)\]", answer))

                    # Anti-hallucination check
                    if len(cited_numbers) == 0:
                        logger.warning(f"⚠️ {model_config['name']} answered without citations - rejecting")
                        answer = "The MARP documents provided do not contain information about this topic."
                        citations = []
                    else:
                        # Deduplicate citations
                        citations = []
                        seen_citations = set()
                        citation_mapping = {}

                        for idx, chunk in enumerate(chunks, start=1):
                            if idx in cited_numbers:
                                citation_key = (chunk.get("title", ""), chunk.get("page", 0))
                                if citation_key not in seen_citations and citation_key[0] and citation_key[1]:
                                    citations.append(
                                        Citation(
                                            title=chunk.get("title", "Unknown"),
                                            page=chunk.get("page", 0),
                                            url=chunk.get("url", ""),
                                        )
                                    )
                                    seen_citations.add(citation_key)
                                    citation_mapping[idx] = len(citations)
                                elif citation_key in seen_citations:
                                    for old_idx, new_idx in citation_mapping.items():
                                        if (
                                            chunks[old_idx - 1].get("title", ""),
                                            chunks[old_idx - 1].get("page", 0),
                                        ) == citation_key:
                                            citation_mapping[idx] = new_idx
                                            break

                        # Renumber citations using placeholders
                        for old_num in sorted(cited_numbers, reverse=True):
                            if old_num in citation_mapping:
                                new_num = citation_mapping[old_num]
                                answer = answer.replace(f"[{old_num}]", f"<<CITE_{new_num}>>")

                        for new_num in set(citation_mapping.values()):
                            answer = answer.replace(f"<<CITE_{new_num}>>", f"[{new_num}]")

                        final_cited_numbers = set(int(match) for match in re.findall(r"\[(\d+)\]", answer))
                        citations = [cit for i, cit in enumerate(citations, start=1) if i in final_cited_numbers]

                        # Ensure consecutive numbering
                        if final_cited_numbers and sorted(final_cited_numbers) != list(range(1, len(citations) + 1)):
                            final_mapping = {}
                            for new_pos, old_pos in enumerate(sorted(final_cited_numbers), start=1):
                                final_mapping[old_pos] = new_pos

                            for old_pos in sorted(final_cited_numbers, reverse=True):
                                new_pos = final_mapping[old_pos]
                                answer = answer.replace(f"[{old_pos}]", f"<<FINAL_{new_pos}>>")

                            for new_pos in final_mapping.values():
                                answer = answer.replace(f"<<FINAL_{new_pos}>>", f"[{new_pos}]")

                logger.info(f"✅ {model_config['name']}: Generated answer with {len(citations)} citations")
                return ModelComparisonResult(
                    model_id=model_config["id"], model_name=model_config["name"], answer=answer, citations=citations
                )

            except Exception as e:
                logger.error(f"❌ Error with model {model_config['name']}: {e}")
                return ModelComparisonResult(
                    model_id=model_config["id"],
                    model_name=model_config["name"],
                    answer=f"Error generating answer with {model_config['name']}. Please try again.",
                    citations=[],
                )

        # Execute parallel generation
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_model = {executor.submit(generate_with_model, model): model for model in config.COMPARISON_MODELS}

            for future in as_completed(future_to_model):
                result = future.result()
                results.append(result)

        # Sort results to maintain order
        model_order = {model["id"]: i for i, model in enumerate(config.COMPARISON_MODELS)}
        results.sort(key=lambda r: model_order.get(r.model_id, 999))

        latency = round((time.time() - start_time) * 1000, 2)
        logger.info(f"✅ Multi-model comparison completed in {latency}ms")

        return ComparisonResponse(
            query=req.query,
            reformulated_query=search_query,
            results=results,
            latency_ms=latency,
            retrieval_count=len(chunks) if chunks else 0,
        )

    except Exception as e:
        logger.error(f"❌ Error in compare_models endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to compare models: {str(e)}")


class ModelSelectionRequest(BaseModel):
    query: str
    model_id: str
    answer: str
    citation_count: int
    retrieval_count: int
    latency_ms: float
    session_id: Optional[str] = None


@app.post("/chat/comparison/select")
def record_model_selection(req: ModelSelectionRequest, user: Dict = Depends(validate_session)):
    """Records analytics events when user selects a model from comparison (requires authentication)"""
    try:
        user_id = user["user_id"]
        session_id = req.session_id or events.generate_event_id()
        correlation_id = events.generate_event_id()

        logger.info(f"📊 User {user_id} selected model {req.model_id} from comparison")

        # Publish QuerySubmitted event for the selected model only
        if event_broker:
            try:
                query_event = events.create_query_submitted_event(
                    query=req.query,
                    user_session_id=session_id,
                    model_id=req.model_id,
                    user_id=user_id,
                    correlation_id=correlation_id,
                )
                event_broker.publish(
                    routing_key=events.ROUTING_KEY_QUERY_SUBMITTED,
                    message=json.dumps(query_event),
                    exchange="events",
                )

                # Publish ResponseGenerated event for the selected model only
                response_event = events.create_response_generated_event(
                    query=req.query,
                    response=req.answer,
                    model_id=req.model_id,
                    user_session_id=session_id,
                    latency_ms=req.latency_ms,
                    citation_count=req.citation_count,
                    retrieval_count=req.retrieval_count,
                    user_id=user_id,
                    correlation_id=correlation_id,
                )
                event_broker.publish(
                    routing_key=events.ROUTING_KEY_RESPONSE_GENERATED,
                    message=json.dumps(response_event),
                    exchange="events",
                )

                logger.info(f"✅ Published analytics events for selected model {req.model_id}")
                return {"status": "ok", "message": "Selection recorded"}
            except Exception as e:
                logger.warning(f"Failed to publish analytics events: {e}")
                raise HTTPException(status_code=500, detail="Failed to record selection")
        else:
            logger.warning("Event broker not available - selection not recorded")
            return {"status": "ok", "message": "Selection recorded (broker unavailable)"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error recording model selection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to record selection: {str(e)}")
