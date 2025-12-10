# File Path: services/retrieval/retrieval_utils.py

# imports type hints (List, Any), SentenceTransformer for converting text to vectors, and QdrantClient for connecting to the vector database.
from typing import Any, List

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


# Loads a text-to-vector model and returns a ready-to-use SentenceTransformer object.
def load_embedding_model(model_name: str) -> SentenceTransformer:
    """Load the SentenceTransformer model once at startup."""
    return SentenceTransformer(model_name)


# Creates and returns a Qdrant client connection using the provided URL (e.g., "http://qdrant:6333").
def create_qdrant_client(url: str) -> QdrantClient:
    """Create a Qdrant client (use 'http://qdrant:6333' inside Docker)."""
    return QdrantClient(url=url)


# Converts a query string into a list of numbers (an embedding vector) using the loaded model.
def generate_query_embedding(model: SentenceTransformer, text: str) -> List[float]:
    """Encode a query string to a vector (as a Python list)."""
    return model.encode(text).tolist()


# Searches Qdrant for the top-k most similar document chunks to the query vector and returns results with scores and metadata.
def search_similar_chunks(client: QdrantClient, collection: str, vector: List[float], top_k: int) -> List[Any]:
    """Cosine similarity search in Qdrant; returns raw hits with .payload and .score."""
    return client.query_points(
        collection_name=collection,
        query=vector,
        limit=top_k,
    ).points
