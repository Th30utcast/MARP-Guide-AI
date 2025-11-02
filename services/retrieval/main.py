# services/retrieval/main.py
import os, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from retrieval_service import load_model, get_qdrant, embed, vector_search

# --- Config (env with sensible defaults) ---
EMBEDDING_MODEL   = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
QDRANT_URL        = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "marp-documents")

# --- FastAPI setup ---
app = FastAPI(title="Retrieval Service", version="1.0.0")

# --- Schemas ---
class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")

class SearchResult(BaseModel):
    text: str
    title: str
    page: int
    url: str
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]

# --- Singletons (load once) ---
model = load_model(EMBEDDING_MODEL)
qdrant = get_qdrant(QDRANT_URL)

# --- Health ---
@app.get("/health")
def health():
    try:
        # Will raise if collection missing / Qdrant not reachable
        qdrant.get_collection(QDRANT_COLLECTION)
        return {"status": "ok", "model": EMBEDDING_MODEL, "collection": QDRANT_COLLECTION}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

# --- Search ---
@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    t0 = time.time()
    try:
        qvec = embed(model, req.query)
        hits = vector_search(qdrant, QDRANT_COLLECTION, qvec, req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

    results: List[SearchResult] = []
    for h in hits:
        payload = h.payload or {}
        results.append(SearchResult(
            text = payload.get("text", ""),
            title= payload.get("title", ""),
            page = int(payload.get("page", 0)),
            url  = payload.get("url", ""),
            score= float(h.score),
        ))

    # (Optional later) log latency, top score, etc.
    _latency_ms = int((time.time() - t0) * 1000)
    return SearchResponse(query=req.query, results=results)
