import os, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from retrieval_service import load_model, get_qdrant, embed, vector_search

# Environment configuration
EMBEDDING_MODEL   = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
QDRANT_URL        = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "marp-documents")

# FastAPI setup
app = FastAPI(title="Retrieval Service", version="1.1.1")

# Schemas
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


# Load model and client once
model = load_model(EMBEDDING_MODEL)
qdrant = get_qdrant(QDRANT_URL)

# Health check
@app.get("/health")
def health():
    try:
        qdrant.get_collection(QDRANT_COLLECTION)
        return {
            "status": "ok",
            "model": EMBEDDING_MODEL,
            "collection": QDRANT_COLLECTION
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

# Search endpoint
@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    start = time.time()

    try:
        query_vec = embed(model, req.query)
        hits = vector_search(qdrant, QDRANT_COLLECTION, query_vec, req.top_k)
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
        if len(text) > 800:
            text = text[:800] + "…"

        results.append(SearchResult(
            text=text,
            document_id=str(payload.get("document_id", "")),
            chunk_index=int(payload.get("chunk_index", 0)),
            title=payload.get("title", ""),
            page=int(payload.get("page", 0)),
            url=payload.get("url", ""),
            score=float(hit.score)
        ))

        if len(results) >= req.top_k:
            break

    latency = round((time.time() - start) * 1000, 2)
    print(f"[Retrieval] {len(results)} results | latency: {latency}ms")

    return SearchResponse(query=req.query, results=results)
