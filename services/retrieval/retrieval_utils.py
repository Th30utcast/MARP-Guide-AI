# services/retrieval/retrieval_utils.py
from typing import List, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

def load_embedding_model(model_name: str) -> SentenceTransformer:
    """Load the SentenceTransformer model once at startup."""
    return SentenceTransformer(model_name)

def create_qdrant_client(url: str) -> QdrantClient:
    """Create a Qdrant client (use 'http://qdrant:6333' inside Docker)."""
    return QdrantClient(url=url)

def generate_query_embedding(model: SentenceTransformer, text: str) -> List[float]:
    """Encode a query string to a vector (as a Python list)."""
    return model.encode(text).tolist()

def search_similar_chunks(client: QdrantClient, collection: str, vector: List[float], top_k: int) -> List[Any]:
    """Cosine similarity search in Qdrant; returns raw hits with .payload and .score."""
    return client.search(
        collection_name=collection,
        query_vector=vector,
        limit=top_k,
    )
