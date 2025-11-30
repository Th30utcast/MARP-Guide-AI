"""
Tests for Indexing Service.

What this tests:
- Document chunking logic (token-based)
- Embedding generation
- Qdrant storage operations
- Event handling
"""

import pytest
import json
import numpy as np
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services" / "indexing"))

from indexing_service import IndexingService


class TestChunking:
    """Test document chunking functionality."""

    @patch('indexing_service.QdrantClient')
    @patch('indexing_service.SentenceTransformer')
    @patch('indexing_service.RabbitMQEventBroker')
    def test_chunk_document(self, mock_broker, mock_model, mock_qdrant):
        """Test token-based document chunking."""
        # Mock tokenizer
        mock_tokenizer = Mock()
        # Simulate encoding text to tokens
        mock_tokenizer.encode.return_value = list(range(500))  # 500 tokens
        mock_tokenizer.decode.side_effect = lambda tokens, **kwargs: f"Chunk with {len(tokens)} tokens"

        mock_model.return_value.tokenizer = mock_tokenizer

        service = IndexingService()

        text = "This is a long text " * 100  # Long text
        metadata = {"title": "Test", "page": 1, "url": "http://example.com"}

        chunks = service.chunk_document(text, metadata, max_tokens=200, overlap_tokens=50)

        # Should create multiple chunks
        assert len(chunks) > 1
        # Each chunk should have text and metadata
        for chunk in chunks:
            assert "text" in chunk
            assert "metadata" in chunk
            assert chunk["metadata"]["title"] == "Test"

    @patch('indexing_service.QdrantClient')
    @patch('indexing_service.SentenceTransformer')
    @patch('indexing_service.RabbitMQEventBroker')
    def test_chunk_document_overlap(self, mock_broker, mock_model, mock_qdrant):
        """Test that chunks have proper overlap."""
        mock_tokenizer = Mock()
        # 250 tokens total
        mock_tokenizer.encode.return_value = list(range(250))
        mock_tokenizer.decode.side_effect = lambda tokens, **kwargs: f"Chunk_{len(tokens)}"

        mock_model.return_value.tokenizer = mock_tokenizer

        service = IndexingService()

        text = "Test text"
        metadata = {"title": "Test", "page": 1}

        # max_tokens=200, overlap=50
        # Should create 2 chunks: 0-200, 150-250
        chunks = service.chunk_document(text, metadata, max_tokens=200, overlap_tokens=50)

        # Should have at least 2 chunks due to overlap
        assert len(chunks) >= 2


class TestEmbeddings:
    """Test embedding generation."""

    @patch('indexing_service.QdrantClient')
    @patch('indexing_service.SentenceTransformer')
    @patch('indexing_service.RabbitMQEventBroker')
    def test_generate_embeddings(self, mock_broker, mock_model, mock_qdrant):
        """Test embedding generation for chunks."""
        # Mock embeddings (384 dimensions)
        mock_embeddings = np.random.rand(5, 384)
        mock_model.return_value.encode.return_value = mock_embeddings

        service = IndexingService()

        texts = ["Chunk 1", "Chunk 2", "Chunk 3", "Chunk 4", "Chunk 5"]
        embeddings = service.generate_embeddings(texts)

        # Should return correct shape
        assert embeddings.shape == (5, 384)
        # Should call model.encode
        mock_model.return_value.encode.assert_called_once()

class TestQdrantStorage:
    """Test Qdrant vector storage."""

    @patch('indexing_service.QdrantClient')
    @patch('indexing_service.SentenceTransformer')
    @patch('indexing_service.RabbitMQEventBroker')
    def test_store_chunks_in_qdrant(self, mock_broker, mock_model, mock_qdrant):
        """Test storing chunks in Qdrant."""
        service = IndexingService()

        chunks = [
            {
                "text": "Chunk 1 text",
                "metadata": {
                    "title": "Test Doc",
                    "page": 1,
                    "url": "https://example.com/test.pdf",
                    "document_id": "test-doc"
                }
            },
            {
                "text": "Chunk 2 text",
                "metadata": {
                    "title": "Test Doc",
                    "page": 2,
                    "url": "https://example.com/test.pdf",
                    "document_id": "test-doc"
                }
            }
        ]

        embeddings = np.random.rand(2, 384)

        service.store_chunks_in_qdrant(chunks, embeddings, "test-doc")

        # Should call qdrant.upsert
        service.qdrant.upsert.assert_called_once()

        # Check the points structure
        call_args = service.qdrant.upsert.call_args
        points = call_args[1]['points']

        assert len(points) == 2
        assert points[0].payload['text'] == "Chunk 1 text"
        assert points[0].payload['document_id'] == "test-doc"
        assert points[0].payload['title'] == "Test Doc"
        assert points[0].payload['page'] == 1


class TestEventHandling:
    """Test event processing."""

    @patch('indexing_service.IndexingService._read_pages')
    @patch('indexing_service.IndexingService.chunk_document')
    @patch('indexing_service.IndexingService.generate_embeddings')
    @patch('indexing_service.IndexingService.store_chunks_in_qdrant')
    @patch('indexing_service.IndexingService._save_chunks')
    @patch('indexing_service.IndexingService.publish_chunks_indexed_event')
    @patch('indexing_service.QdrantClient')
    @patch('indexing_service.SentenceTransformer')
    @patch('indexing_service.RabbitMQEventBroker')
    def test_handle_document_extracted_event(
        self, mock_broker, mock_model, mock_qdrant,
        mock_publish, mock_save_chunks, mock_store,
        mock_embeddings, mock_chunk, mock_read_pages
    ):
        """Test handling DocumentExtracted event."""
        # Mock pages from storage
        mock_read_pages.return_value = [
            {"page": 1, "text": "Page 1 content"},
            {"page": 2, "text": "Page 2 content"}
        ]

        # Mock chunking (2 pages, 3 chunks each)
        mock_chunk.side_effect = [
            [{"text": "Chunk 1", "metadata": {}}] * 3,  # Page 1
            [{"text": "Chunk 2", "metadata": {}}] * 3   # Page 2
        ]

        # Mock embeddings
        mock_embeddings.return_value = np.random.rand(6, 384)

        service = IndexingService()

        event = {
            "correlationId": "corr-123",
            "payload": {
                "documentId": "test-doc",
                "metadata": {
                    "title": "Test Document",
                    "author": "Test Author"
                },
                "url": "https://example.com/test.pdf"
            }
        }

        service.handle_document_extracted_event(event)

        # Should process pages
        mock_read_pages.assert_called_once_with("test-doc")
        # Should chunk each page
        assert mock_chunk.call_count == 2
        # Should generate embeddings for all chunks
        mock_embeddings.assert_called_once()
        # Should store in Qdrant
        mock_store.assert_called_once()
        # Should publish success event
        mock_publish.assert_called_once_with("test-doc", "corr-123", 6)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
