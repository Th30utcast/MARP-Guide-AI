# Imports FastAPI, Pydantic, logging, and custom utilities for embeddings, Qdrant, and RabbitMQ events.
import json
import logging
import os
import time
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from retrieval_utils import create_qdrant_client, generate_query_embedding, load_embedding_model, search_similar_chunks

from common.events import ROUTING_KEY_RETRIEVAL_COMPLETED, create_retrieval_completed_event
from common.mq import RabbitMQEventBroker

# Logging setup:Sets up logging to print INFO-level messages.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration: Reads configuration from environment variables
# (embedding model, Qdrant URL, RabbitMQ settings) with defaults.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "marp-documents")

# RabbitMQ configuration (optional; if not reachable, events won't be published)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

# FastAPI setup: Creates the FastAPI application instance
app = FastAPI(title="Retrieval Service", version="1.1.1")


# Schemas: Defines Pydantic models for request/response validation (SearchRequest, SearchResult, SearchResponse)
class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")


class SearchResult(BaseModel):
    text: str
    document_id: str
    chunk_index: int
    title: str
    page: int
    url: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]


# Load model and client once: Loads the embedding model and connects to Qdrant at startup
model = load_embedding_model(EMBEDDING_MODEL)
qdrant = create_qdrant_client(QDRANT_URL)

# RabbitMQ broker setup: Connects to RabbitMQ and sets up queues/exchanges; continues if connection fails_broker = None
try:
    _broker = RabbitMQEventBroker(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        username=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD,
    )
    logger.info("✅ RabbitMQ broker connected successfully")

    # Auto-declare exchange, queue, and binding for retrieval.completed (best-effort)
    try:
        if _broker.channel:
            _broker.channel.exchange_declare(exchange="events", exchange_type="topic", durable=True)
            _broker.channel.queue_declare(queue="retrieval.completed", durable=True)
            _broker.channel.queue_bind(
                exchange="events", queue="retrieval.completed", routing_key=ROUTING_KEY_RETRIEVAL_COMPLETED
            )
            logger.info("✅ Declared queue 'retrieval.completed' and bound to exchange 'events'")
    except Exception as e:
        logger.warning(f"⚠️ Failed to auto-declare retrieval queue/binding: {e}")
except Exception as e:
    logger.warning(f"⚠️ RabbitMQ broker not available: {e}. Events will not be published.")
    _broker = None


# Health check: GET /health checks if Qdrant is reachable and returns service status
@app.get("/health")
def health():
    try:
        qdrant.get_collection(QDRANT_COLLECTION)
        return {"status": "ok", "model": EMBEDDING_MODEL, "collection": QDRANT_COLLECTION}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


# Search endpoint: POST /search converts the query to an embedding, searches Qdrant for similar chunks,
# deduplicates and formats results, measures latency, optionally publishes an event, and returns the results.
@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    start = time.time()

    try:
        query_vec = generate_query_embedding(model, req.query)
        hits = search_similar_chunks(qdrant, QDRANT_COLLECTION, query_vec, req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

    results = []
    seen_texts = set()
    for hit in hits:
        payload = hit.payload or {}
        text = payload.get("text", "").strip()

        # Avoid duplicates
        if text in seen_texts:
            continue
        seen_texts.add(text)

        # Trim very long texts
        if len(text) > 1700:
            text = text[:1700] + "…"

        results.append(
            SearchResult(
                text=text,
                document_id=str(payload.get("document_id", "")),
                chunk_index=int(payload.get("chunk_index", 0)),
                title=payload.get("title", ""),
                page=int(payload.get("page", 0)),
                url=payload.get("url", ""),
                score=float(hit.score),
            )
        )

        if len(results) >= req.top_k:
            break

    latency = round((time.time() - start) * 1000, 2)
    logger.info(f"🔍 Retrieved {len(results)} results | latency: {latency}ms")

    # Publish RetrievalCompleted (best-effort; ignore failures)
    if _broker is not None:
        try:
            summary = [
                {
                    "documentId": r.document_id,
                    "chunkIndex": r.chunk_index,
                    "score": r.score,
                }
                for r in results
            ]
            event = create_retrieval_completed_event(
                query=req.query,
                top_k=req.top_k,
                result_count=len(results),
                latency_ms=latency,
                results_summary=summary,
            )
            _broker.publish(
                routing_key=ROUTING_KEY_RETRIEVAL_COMPLETED,
                message=json.dumps(event),
                exchange="events",
            )
            logger.info(f"✅ Published RetrievalCompleted event for query: {req.query[:50]}...")
        except Exception as e:
            logger.warning(f"⚠️ Failed to publish RetrievalCompleted event: {e}")

    return SearchResponse(query=req.query, results=results)
