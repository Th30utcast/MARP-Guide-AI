import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional


def generate_event_id() -> str:
    # Generate a unique event ID
    return str(uuid.uuid4())


def get_utc_timestamp() -> str:
    # Get current UTC timestamp in ISO 8601 format
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_document_discovered_event(
    document_id: str,
    title: str,
    url: str,
    file_size: int,
    correlation_id: Optional[str] = None,
    original_url: Optional[str] = None
) -> Dict[str, Any]:
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
    url: Optional[str] = None,
    pages_ref: Optional[str] = None
) -> Dict[str, Any]:
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

    # Add pagesRef if provided
    if pages_ref:
        payload["pagesRef"] = pages_ref

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


def create_ingestion_failed_event(
    document_id: str,
    correlation_id: str,
    error_message: str,
    error_type: str = "IngestionError"
) -> Dict[str, Any]:
    return {
        "eventType": "IngestionFailed",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id,
        "source": "ingestion-service",
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


# ----------------------------------------------------------------------------
# Retrieval Events
# ----------------------------------------------------------------------------

def create_retrieval_completed_event(
    query: str,
    top_k: int,
    result_count: int,
    latency_ms: float,
    results_summary: Optional[list] = None,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    return {
        "eventType": "RetrievalCompleted",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id or generate_event_id(),
        "source": "retrieval-service",
        "version": "1.0",
        "payload": {
            "query": query,
            "topK": top_k,
            "resultCount": result_count,
            "latencyMs": latency_ms,
            "results": results_summary or []
        }
    }

# ============================================================================
# RabbitMQ Routing Keys (for consistency)
# ============================================================================

ROUTING_KEY_DISCOVERED = "documents.discovered"
ROUTING_KEY_EXTRACTED = "documents.extracted"
ROUTING_KEY_INDEXED = "documents.indexed"
ROUTING_KEY_INGESTION_FAILED = "documents.ingestion.failed"
ROUTING_KEY_EXTRACTION_FAILED = "documents.extraction.failed"
ROUTING_KEY_INDEXING_FAILED = "documents.indexing.failed"
ROUTING_KEY_RETRIEVAL_COMPLETED = "retrieval.completed"