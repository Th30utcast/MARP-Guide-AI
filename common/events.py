"""
Event schemas and utilities for MARP Guide AI.
All events follow the standard schema with past-tense naming.

This module provides helper functions to create properly formatted events
for the entire pipeline: Ingestion → Extraction → Indexing
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional


def generate_event_id() -> str:
    """Generate a unique event ID."""
    return str(uuid.uuid4())


def get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_document_discovered_event(
    document_id: str,
    title: str,
    url: str,
    file_size: int,
    correlation_id: Optional[str] = None,
    original_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a DocumentDiscovered event.

    Published by: Ingestion Service
    Consumed by: Extraction Service

    Args:
        document_id: Unique document identifier
        title: Document title
        url: URL or path to the PDF (local file path)
        file_size: Size of the PDF in bytes
        correlation_id: Optional correlation ID (generated if not provided)
        original_url: Optional original web URL (if url is a local path)

    Returns:
        DocumentDiscovered event dictionary
    """
    payload = {
        "documentId": document_id,
        "title": title,
        "url": url,
        "discoveredAt": get_utc_timestamp(),
        "fileSize": file_size
    }

    # Add originalUrl if provided
    if original_url:
        payload["originalUrl"] = original_url

    return {
        "eventType": "DocumentDiscovered",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id or generate_event_id(),
        "source": "ingestion-service",
        "version": "1.0",
        "payload": payload
    }


def create_document_extracted_event(
    document_id: str,
    correlation_id: str,
    page_count: int,
    text_extracted: bool,
    pdf_metadata: Dict[str, Any],
    extraction_method: str = "pdfplumber",
    url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a DocumentExtracted event.

    Published by: Extraction Service
    Consumed by: Indexing Service

    Args:
        document_id: Document identifier
        correlation_id: Correlation ID from DocumentDiscovered event
        page_count: Number of pages in document
        text_extracted: Whether text was successfully extracted
        pdf_metadata: PDF's internal metadata (title, author, year, subject, etc.)
        extraction_method: Method used for extraction (default: pdfplumber)
        url: Optional original URL to the source document

    Returns:
        DocumentExtracted event dictionary
    """
    payload = {
        "documentId": document_id,
        "textExtracted": text_extracted,
        "pageCount": page_count,
        "metadata": pdf_metadata,  # PDF's internal metadata
        "extractedAt": get_utc_timestamp(),
        "extractionMethod": extraction_method
    }

    # Add URL if provided
    if url:
        payload["url"] = url

    return {
        "eventType": "DocumentExtracted",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id,
        "source": "extraction-service",
        "version": "1.0",
        "payload": payload
    }


def create_chunks_indexed_event(
    document_id: str,
    correlation_id: str,
    chunk_count: int,
    embedding_model: str,
    vector_dim: int,
    index_name: Optional[str] = "marp-documents"
) -> Dict[str, Any]:
    """
    Create a ChunksIndexed event.
    
    Published by: Indexing Service
    Consumed by: (Optional) Monitoring/Analytics services
    
    Args:
        document_id: Document identifier
        correlation_id: Correlation ID from previous events
        chunk_count: Number of chunks created and indexed
        embedding_model: Model used for embeddings (e.g., "all-MiniLM-L6-v2")
        vector_dim: Dimensionality of vectors (e.g., 384, 768)
        index_name: Name of the vector database index
    
    Returns:
        ChunksIndexed event dictionary
    """
    return {
        "eventType": "ChunksIndexed",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id,
        "source": "indexing-service",
        "version": "1.0",
        "payload": {
            "documentId": document_id,
            "chunkCount": chunk_count,
            "embeddingModel": embedding_model,
            "vectorDim": vector_dim,
            "indexName": index_name,
            "indexedAt": get_utc_timestamp()
        }
    }


def create_extraction_failed_event(
    document_id: str,
    correlation_id: str,
    error_message: str,
    error_type: str = "ExtractionError"
) -> Dict[str, Any]:
    """
    Create an ExtractionFailed event (for error handling).
    
    Published by: Extraction Service (when extraction fails)
    Consumed by: Monitoring/Alerting services
    
    Args:
        document_id: Document identifier
        correlation_id: Correlation ID from DocumentDiscovered
        error_message: Description of the error
        error_type: Type of error (ExtractionError, FileNotFound, etc.)
    
    Returns:
        ExtractionFailed event dictionary
    """
    return {
        "eventType": "ExtractionFailed",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id,
        "source": "extraction-service",
        "version": "1.0",
        "payload": {
            "documentId": document_id,
            "errorType": error_type,
            "errorMessage": error_message,
            "failedAt": get_utc_timestamp()
        }
    }


def create_indexing_failed_event(
    document_id: str,
    correlation_id: str,
    error_message: str,
    error_type: str = "IndexingError"
) -> Dict[str, Any]:
    """
    Create an IndexingFailed event (for error handling).
    
    Published by: Indexing Service (when indexing fails)
    Consumed by: Monitoring/Alerting services
    
    Args:
        document_id: Document identifier
        correlation_id: Correlation ID from previous events
        error_message: Description of the error
        error_type: Type of error (IndexingError, VectorDBError, etc.)
    
    Returns:
        IndexingFailed event dictionary
    """
    return {
        "eventType": "IndexingFailed",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id,
        "source": "indexing-service",
        "version": "1.0",
        "payload": {
            "documentId": document_id,
            "errorType": error_type,
            "errorMessage": error_message,
            "failedAt": get_utc_timestamp()
        }
    }


# ============================================================================
# Event Type Constants (for consistency)
# ============================================================================

EVENT_DOCUMENT_DISCOVERED = "DocumentDiscovered"
EVENT_DOCUMENT_EXTRACTED = "DocumentExtracted"
EVENT_CHUNKS_INDEXED = "ChunksIndexed"
EVENT_EXTRACTION_FAILED = "ExtractionFailed"
EVENT_INDEXING_FAILED = "IndexingFailed"


# ============================================================================
# RabbitMQ Routing Keys (for consistency)
# ============================================================================

ROUTING_KEY_DISCOVERED = "documents.discovered"
ROUTING_KEY_EXTRACTED = "documents.extracted"
ROUTING_KEY_INDEXED = "documents.indexed"
ROUTING_KEY_EXTRACTION_FAILED = "documents.extraction.failed"
ROUTING_KEY_INDEXING_FAILED = "documents.indexing.failed"


# ============================================================================
# Validation Functions
# ============================================================================

def validate_event_structure(event: Dict[str, Any]) -> bool:
    """
    Validate that an event has the required structure.
    
    Args:
        event: Event dictionary to validate
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["eventType", "eventId", "timestamp", "correlationId", "source", "version", "payload"]
    
    for field in required_fields:
        if field not in event:
            return False
    
    # Check that IDs are UUIDs (basic check)
    if not isinstance(event["eventId"], str) or len(event["eventId"]) < 32:
        return False
    
    return True


def extract_correlation_id(event: Dict[str, Any]) -> Optional[str]:
    """
    Safely extract correlation ID from an event.
    
    Args:
        event: Event dictionary
    
    Returns:
        Correlation ID if found, None otherwise
    """
    return event.get("correlationId")


def extract_document_id(event: Dict[str, Any]) -> Optional[str]:
    """
    Safely extract document ID from an event's payload.
    
    Args:
        event: Event dictionary
    
    Returns:
        Document ID if found, None otherwise
    """
    payload = event.get("payload", {})
    return payload.get("documentId")