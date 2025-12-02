# Module docstring describing a RAG-powered chat service with a 4-step pipeline.
"""
Chat Service - RAG-powered question answering
Implements the 4-step RAG pipeline: Retrieval → Augmentation → Generation → Citation
"""

import json
import logging

# Imports standard libraries and project modules: FastAPI for the web API, Pydantic for data validation,
# logging, and custom clients for retrieval and LLM calls.
import os
import time
from typing import List, Optional

import config
from fastapi import FastAPI, HTTPException
from openrouter_client import OpenRouterClient
from prompt_templates import create_rag_prompt
from pydantic import BaseModel, Field
from retrieval_client import RetrievalClient

# Sets logging to INFO and creates a logger for this module.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI setup: Creates the FastAPI application instance with a title and version.
app = FastAPI(title="Chat Service", version="1.0.0")

# Initialize clients: Creates instances of RetrievalClient and OpenRouterClient for later use.
retrieval_client = RetrievalClient()
openrouter_client = OpenRouterClient()

# Schemas:


# Defines a Pydantic model for citations with title, page, and URL.
class Citation(BaseModel):
    title: str
    page: int
    url: str


# Defines the request model: required query string and optional top_k (1-20, default 8).
class ChatRequest(BaseModel):
    query: str = Field(..., description="User's question about MARP")
    top_k: int = Field(8, ge=1, le=20, description="Number of chunks to retrieve")


# Defines the response model: query, answer, and a list of citations.
class ChatResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]


# Health check
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


# Chat endpoint: POST endpoint that accepts ChatRequest, records start time, and begins the RAG pipeline.
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    RAG-powered chat endpoint
    Steps: 1. Retrieval → 2. Augmentation → 3. Generation → 4. Citation
    """
    start_time = time.time()

    try:
        # (Step 1 - Retrieval): Logs and searches for relevant document chunks using the retrieval client.
        logger.info(f"🔍 Step 1: Retrieving chunks for query: {req.query[:50]}...")
        chunks = retrieval_client.search(req.query, req.top_k)

        # (No chunks handling): If no chunks are found, returns an error message with empty citations.
        if not chunks:
            logger.warning("⚠️ No chunks retrieved for query")
            return ChatResponse(
                query=req.query,
                answer="I couldn't find any relevant information in the MARP documents to answer your question. Please try rephrasing your query.",
                citations=[],
            )

        logger.info(f"✅ Retrieved {len(chunks)} chunks")

        # (Step 2 - Augmentation): Builds a RAG prompt by combining the user query with retrieved chunks.
        logger.info("📝 Step 2: Building RAG prompt")
        prompt = create_rag_prompt(req.query, chunks)

        # (Step 3 - Generation): Sends the prompt to the LLM via OpenRouter to generate the answer.
        logger.info("🤖 Step 3: Generating answer with LLM")
        answer = openrouter_client.generate_answer(prompt)

        # (Step 4 - Citation extraction): Extracts only citations that were actually referenced
        # in the answer by looking for inline citation markers like [1], [2], etc.
        logger.info("📚 Step 4: Extracting citations")
        import re

        # Check if the answer indicates insufficient information
        # Only treat as "no info" if the answer is primarily about lack of information
        # (i.e., the insufficient info phrase appears in the first 100 characters)
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
        # Check if insufficient info phrase appears early in the answer (first 150 chars)
        answer_start = answer_lower[:150]
        has_insufficient_info = any(phrase in answer_start for phrase in insufficient_info_phrases)

        if has_insufficient_info:
            logger.info("⚠️ Answer indicates insufficient information - returning no citations")
            # Remove any citation markers from the "no info" response
            answer = re.sub(r"\[\d+\]", "", answer).strip()
            citations = []
        else:
            # Find all citation numbers in the answer (e.g., [1], [2], [3])
            cited_numbers = set(int(match) for match in re.findall(r"\[(\d+)\]", answer))
            logger.info(f"Found inline citations: {sorted(cited_numbers)}")

            # VALIDATION: If answer has 0 citations, it means LLM is hallucinating
            # Reject the answer and force "no information" response
            if len(cited_numbers) == 0:
                logger.warning("⚠️ LLM answered without citations - rejecting as hallucination")
                logger.warning(f"Rejected answer: {answer[:200]}...")
                answer = f"The MARP documents provided do not contain information about this topic. Please try asking about MARP regulations, policies, or procedures."
                citations = []
            else:
                # Only include chunks that were actually cited
                citations = []
                seen_citations = set()
                citation_mapping = {}  # Maps old citation numbers to new numbers

                for idx, chunk in enumerate(chunks, start=1):
                    if idx in cited_numbers:
                        citation_key = (chunk.get("title", ""), chunk.get("page", 0))
                        if citation_key not in seen_citations and citation_key[0] and citation_key[1]:
                            # Add to citations list
                            citations.append(
                                Citation(
                                    title=chunk.get("title", "Unknown"), page=chunk.get("page", 0), url=chunk.get("url", "")
                                )
                            )
                            seen_citations.add(citation_key)
                            # Map old citation number to new position in deduplicated list
                            citation_mapping[idx] = len(citations)
                        elif citation_key in seen_citations:
                            # This is a duplicate - map it to the existing citation number
                            # Find which number this citation_key was mapped to
                            for old_idx, new_idx in citation_mapping.items():
                                if (chunks[old_idx - 1].get("title", ""), chunks[old_idx - 1].get("page", 0)) == citation_key:
                                    citation_mapping[idx] = new_idx
                                    break

                # Renumber citations in the answer to match deduplicated list
                # Sort by citation number in descending order to avoid replacement conflicts
                # (e.g., replacing [1] before [10] would corrupt [10])
                for old_num in sorted(cited_numbers, reverse=True):
                    if old_num in citation_mapping:
                        new_num = citation_mapping[old_num]
                        # Replace all occurrences of [old_num] with [new_num]
                        answer = answer.replace(f"[{old_num}]", f"[{new_num}]")

                logger.info(f"Renumbered citations: {citation_mapping}")

                # After renumbering, only keep citations that actually appear in the final answer
                final_cited_numbers = set(int(match) for match in re.findall(r"\[(\d+)\]", answer))
                citations = [cit for i, cit in enumerate(citations, start=1) if i in final_cited_numbers]
                logger.info(f"Citations after dedup filtering: {sorted(final_cited_numbers)}")

                # If citations are not consecutive (e.g., [1, 3]), renumber them to be consecutive (e.g., [1, 2])
                if final_cited_numbers and sorted(final_cited_numbers) != list(range(1, len(citations) + 1)):
                    final_mapping = {}
                    for new_pos, old_pos in enumerate(sorted(final_cited_numbers), start=1):
                        final_mapping[old_pos] = new_pos

                    # Replace citation numbers in descending order to avoid conflicts
                    for old_pos in sorted(final_cited_numbers, reverse=True):
                        new_pos = final_mapping[old_pos]
                        answer = answer.replace(f"[{old_pos}]", f"[{new_pos}]")

                    logger.info(f"Final renumbering to consecutive: {final_mapping}")

        # (Latency logging): Calculates and logs how long the request took in milliseconds.
        latency = round((time.time() - start_time) * 1000, 2)
        logger.info(f"✅ Chat completed in {latency}ms | Citations: {len(citations)}")

        # (Success response): Returns the ChatResponse with the query, generated answer, and citations.
        return ChatResponse(query=req.query, answer=answer, citations=citations)

        # (Error handling): Catches exceptions, logs errors, and returns a 500 HTTP error with details.
    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")
