"""
Tests for Retrieval Service.

What this tests:
- FastAPI endpoints work correctly
- Query embedding generation
- Qdrant search functionality
- Response formatting with metadata
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services" / "retrieval"))


class TestRetrievalUtils:
    """Test retrieval utility functions."""

    @patch('retrieval_utils.SentenceTransformer')
    def test_load_embedding_model(self, mock_model):
        """Test loading embedding model."""
        from retrieval_utils import load_embedding_model

        model = load_embedding_model("all-MiniLM-L6-v2")

        mock_model.assert_called_once_with("all-MiniLM-L6-v2")

    @patch('retrieval_utils.QdrantClient')
    def test_create_qdrant_client(self, mock_client):
        """Test creating Qdrant client."""
        from retrieval_utils import create_qdrant_client

        client = create_qdrant_client("http://qdrant:6333")

        mock_client.assert_called_once_with(url="http://qdrant:6333")

    @patch('retrieval_utils.SentenceTransformer')
    def test_generate_query_embedding(self, mock_model):
        """Test query embedding generation."""
        from retrieval_utils import generate_query_embedding

        # Mock embedding output
        mock_model_instance = Mock()
        mock_model_instance.encode.return_value = Mock()
        mock_model_instance.encode.return_value.tolist.return_value = [0.1] * 384

        embedding = generate_query_embedding(mock_model_instance, "What is MARP?")

        mock_model_instance.encode.assert_called_once_with("What is MARP?")
        assert len(embedding) == 384


class TestRetrievalAPI:
    """Test FastAPI endpoints."""

    @patch('retrieval_service.qdrant')
    @patch('retrieval_service.model')
    @patch('retrieval_service._broker')
    def test_health_endpoint(self, mock_broker, mock_model, mock_qdrant):
        """Test /health endpoint."""
        # Mock Qdrant collection response
        mock_qdrant.get_collection.return_value = Mock()

        from retrieval_service import app
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "model" in data
        assert "collection" in data

    @patch('retrieval_service.qdrant')
    @patch('retrieval_service.model')
    @patch('retrieval_service._broker')
    def test_search_endpoint_success(self, mock_broker, mock_model, mock_qdrant):
        """Test /search endpoint with successful search."""
        # Mock model encoding
        mock_model.encode.return_value = Mock()
        mock_model.encode.return_value.tolist.return_value = [0.1] * 384

        # Mock Qdrant search results
        mock_hit1 = Mock()
        mock_hit1.payload = {
            "text": "MARP is the Manual of Academic Regulations and Procedures.",
            "document_id": "Intro-to-MARP",
            "chunk_index": 0,
            "title": "Introduction to MARP",
            "page": 1,
            "url": "https://example.com/intro.pdf"
        }
        mock_hit1.score = 0.95

        mock_hit2 = Mock()
        mock_hit2.payload = {
            "text": "The MARP provides guidelines for academic standards.",
            "document_id": "Intro-to-MARP",
            "chunk_index": 1,
            "title": "Introduction to MARP",
            "page": 2,
            "url": "https://example.com/intro.pdf"
        }
        mock_hit2.score = 0.87

        mock_result = Mock()
        mock_result.points = [mock_hit1, mock_hit2]
        mock_qdrant.query_points.return_value = mock_result

        from retrieval_service import app
        client = TestClient(app)

        response = client.post(
            "/search",
            json={"query": "What is MARP?", "top_k": 5}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == "What is MARP?"
        assert len(data["results"]) == 2
        assert data["results"][0]["text"] == "MARP is the Manual of Academic Regulations and Procedures."
        assert data["results"][0]["document_id"] == "Intro-to-MARP"
        assert data["results"][0]["score"] == 0.95

    @patch('retrieval_service.qdrant')
    @patch('retrieval_service.model')
    @patch('retrieval_service._broker')
    def test_search_endpoint_deduplication(self, mock_broker, mock_model, mock_qdrant):
        """Test that search deduplicates identical results."""
        # Mock model encoding
        mock_model.encode.return_value = Mock()
        mock_model.encode.return_value.tolist.return_value = [0.1] * 384

        # Mock duplicate results
        mock_hit1 = Mock()
        mock_hit1.payload = {
            "text": "Same text",
            "document_id": "doc1",
            "chunk_index": 0,
            "title": "Doc 1",
            "page": 1,
            "url": "https://example.com/doc1.pdf"
        }
        mock_hit1.score = 0.95

        mock_hit2 = Mock()
        mock_hit2.payload = {
            "text": "Same text",  # Duplicate!
            "document_id": "doc1",
            "chunk_index": 1,
            "title": "Doc 1",
            "page": 2,
            "url": "https://example.com/doc1.pdf"
        }
        mock_hit2.score = 0.90

        mock_result = Mock()
        mock_result.points = [mock_hit1, mock_hit2]
        mock_qdrant.query_points.return_value = mock_result

        from retrieval_service import app
        client = TestClient(app)

        response = client.post(
            "/search",
            json={"query": "test query", "top_k": 5}
        )

        assert response.status_code == 200
        data = response.json()

        # Should only return 1 result (deduplicated)
        assert len(data["results"]) == 1

    @patch('retrieval_service.qdrant')
    @patch('retrieval_service.model')
    @patch('retrieval_service._broker')
    def test_search_endpoint_long_text_truncation(self, mock_broker, mock_model, mock_qdrant):
        """Test that very long texts are truncated."""
        # Mock model encoding
        mock_model.encode.return_value = Mock()
        mock_model.encode.return_value.tolist.return_value = [0.1] * 384

        # Mock result with very long text (longer than 1700 chars)
        mock_hit = Mock()
        long_text = "A" * 2000  # 2000 characters (exceeds 1700 limit)
        mock_hit.payload = {
            "text": long_text,
            "document_id": "doc1",
            "chunk_index": 0,
            "title": "Doc 1",
            "page": 1,
            "url": "https://example.com/doc1.pdf"
        }
        mock_hit.score = 0.95

        mock_result = Mock()
        mock_result.points = [mock_hit]
        mock_qdrant.query_points.return_value = mock_result

        from retrieval_service import app
        client = TestClient(app)

        response = client.post(
            "/search",
            json={"query": "test", "top_k": 1}
        )

        assert response.status_code == 200
        data = response.json()

        # Text should be truncated to 1700 chars + "…" = 1701 total
        assert len(data["results"][0]["text"]) == 1701
        assert data["results"][0]["text"].endswith("…")

    @patch('retrieval_service.qdrant')
    @patch('retrieval_service.model')
    @patch('retrieval_service._broker')
    def test_search_endpoint_validation(self, mock_broker, mock_model, mock_qdrant):
        """Test input validation on search endpoint."""
        from retrieval_service import app
        client = TestClient(app)

        # Test missing query
        response = client.post("/search", json={"top_k": 5})
        assert response.status_code == 422  # Validation error

        # Test invalid top_k (too high)
        response = client.post(
            "/search",
            json={"query": "test", "top_k": 100}
        )
        assert response.status_code == 422  # Should fail (max is 20)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
