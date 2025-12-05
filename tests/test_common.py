"""
Tests for common modules (config, events, mq, health, logging).

What this tests:
- Event creation functions work correctly
- Event schemas have all required fields
- Configuration loading works
- RabbitMQ broker can be mocked
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common import events
from common.config import get_rabbitmq_broker


class TestEventCreation:
    """Test that event creation functions work correctly."""

    def test_document_discovered_event(self):
        """Test DocumentDiscovered event creation."""
        event = events.create_document_discovered_event(
            document_id="test-doc",
            title="Test Document",
            url="/app/pdfs/test.pdf",
            file_size=1024,
            original_url="https://example.com/test.pdf",
        )

        # Check structure
        assert event["eventType"] == "DocumentDiscovered"
        assert "eventId" in event
        assert "timestamp" in event
        assert "correlationId" in event
        assert event["source"] == "ingestion-service"
        assert event["version"] == "1.0"

        # Check payload
        payload = event["payload"]
        assert payload["documentId"] == "test-doc"
        assert payload["title"] == "Test Document"
        assert payload["url"] == "/app/pdfs/test.pdf"
        assert payload["fileSize"] == 1024
        assert payload["originalUrl"] == "https://example.com/test.pdf"

    def test_document_extracted_event(self):
        """Test DocumentExtracted event creation."""
        event = events.create_document_extracted_event(
            document_id="test-doc",
            correlation_id="corr-123",
            page_count=10,
            text_extracted=True,
            pdf_metadata={"title": "Test", "author": "Author"},
            extraction_method="pdfplumber",
            url="https://example.com/test.pdf",
        )

        assert event["eventType"] == "DocumentExtracted"
        assert event["correlationId"] == "corr-123"
        assert event["source"] == "extraction-service"

        payload = event["payload"]
        assert payload["documentId"] == "test-doc"
        assert payload["pageCount"] == 10
        assert payload["textExtracted"] is True
        assert payload["extractionMethod"] == "pdfplumber"

    def test_chunks_indexed_event(self):
        """Test ChunksIndexed event creation."""
        event = events.create_chunks_indexed_event(
            document_id="test-doc",
            correlation_id="corr-123",
            chunk_count=50,
            embedding_model="all-MiniLM-L6-v2",
            vector_dim=384,
            index_name="marp-documents",
        )

        assert event["eventType"] == "ChunksIndexed"
        assert event["source"] == "indexing-service"

        payload = event["payload"]
        assert payload["documentId"] == "test-doc"
        assert payload["chunkCount"] == 50
        assert payload["embeddingModel"] == "all-MiniLM-L6-v2"
        assert payload["vectorDim"] == 384

    def test_retrieval_completed_event(self):
        """Test RetrievalCompleted event creation."""
        event = events.create_retrieval_completed_event(
            query="What is MARP?",
            top_k=5,
            result_count=5,
            latency_ms=42.5,
            results_summary=[{"documentId": "test", "chunkIndex": 0, "score": 0.9}],
        )

        assert event["eventType"] == "RetrievalCompleted"
        assert event["source"] == "retrieval-service"

        payload = event["payload"]
        assert payload["query"] == "What is MARP?"
        assert payload["topK"] == 5
        assert payload["resultCount"] == 5
        assert payload["latencyMs"] == 42.5

    def test_extraction_failed_event(self):
        """Test ExtractionFailed event creation."""
        event = events.create_extraction_failed_event(
            document_id="test-doc", correlation_id="corr-123", error_message="PDF file corrupted", error_type="FileError"
        )

        assert event["eventType"] == "ExtractionFailed"
        assert event["source"] == "extraction-service"

        payload = event["payload"]
        assert payload["documentId"] == "test-doc"
        assert payload["errorType"] == "FileError"
        assert payload["errorMessage"] == "PDF file corrupted"


class TestEventHelpers:
    """Test helper functions."""

    def test_generate_event_id(self):
        """Test event ID generation."""
        id1 = events.generate_event_id()
        id2 = events.generate_event_id()

        # Should be unique
        assert id1 != id2
        # Should be valid UUIDs (36 characters with dashes)
        assert len(id1) == 36
        assert len(id2) == 36

    def test_get_utc_timestamp(self):
        """Test UTC timestamp generation."""
        timestamp = events.get_utc_timestamp()

        # Should be ISO 8601 format ending in Z
        assert timestamp.endswith("Z")
        # Should be parseable
        assert "T" in timestamp


class TestRoutingKeys:
    """Test that routing keys are defined correctly."""

    def test_routing_keys_exist(self):
        """Test all routing keys are defined."""
        assert hasattr(events, "ROUTING_KEY_DISCOVERED")
        assert hasattr(events, "ROUTING_KEY_EXTRACTED")
        assert hasattr(events, "ROUTING_KEY_INDEXED")
        assert hasattr(events, "ROUTING_KEY_INGESTION_FAILED")
        assert hasattr(events, "ROUTING_KEY_EXTRACTION_FAILED")
        assert hasattr(events, "ROUTING_KEY_INDEXING_FAILED")
        assert hasattr(events, "ROUTING_KEY_RETRIEVAL_COMPLETED")

    def test_routing_key_format(self):
        """Test routing keys follow correct format."""
        assert events.ROUTING_KEY_DISCOVERED == "documents.discovered"
        assert events.ROUTING_KEY_EXTRACTED == "documents.extracted"
        assert events.ROUTING_KEY_INDEXED == "documents.indexed"


class TestConfiguration:
    """Test configuration module."""

    def test_environment_variables_loaded(self):
        """Test that configuration reads from environment variables."""
        import common.config as config

        # These should have default values
        assert config.RABBITMQ_HOST is not None
        assert config.RABBITMQ_PORT is not None
        assert config.STORAGE_PATH is not None
        assert config.PDF_OUTPUT_DIR is not None
        assert config.QDRANT_COLLECTION is not None
        assert config.EMBEDDING_MODEL is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
