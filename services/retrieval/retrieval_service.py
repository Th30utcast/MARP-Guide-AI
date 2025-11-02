# services/retrieval/retrieval_service.py
from typing import List, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

def load_model(model_name: str) -> SentenceTransformer:
    """Load the SentenceTransformer model once at startup."""
    return SentenceTransformer(model_name)

def get_qdrant(url: str) -> QdrantClient:
    """Create a Qdrant client (use 'http://qdrant:6333' inside Docker)."""
    return QdrantClient(url=url)

def embed(model: SentenceTransformer, text: str) -> List[float]:
    """Encode a query string to a vector (as a Python list)."""
    return model.encode(text).tolist()

def vector_search(client: QdrantClient, collection: str, vector: List[float], top_k: int) -> List[Any]:
    """Cosine similarity search in Qdrant; returns raw hits with .payload and .score."""
    return client.search(
        collection_name=collection,
        query_vector=vector,
        limit=top_k,
    )
