import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


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
    original_url: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "documentId": document_id,
        "title": title,
        "url": url,
        "discoveredAt": get_utc_timestamp(),
        "fileSize": file_size,
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
        "payload": payload,
    }


def create_document_extracted_event(
    document_id: str,
    correlation_id: str,
    page_count: int,
    text_extracted: bool,
    pdf_metadata: Dict[str, Any],
    extraction_method: str = "pdfplumber",
    url: Optional[str] = None,
    pages_ref: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "documentId": document_id,
        "textExtracted": text_extracted,
        "pageCount": page_count,
        "metadata": pdf_metadata,  # PDF's internal metadata
        "extractedAt": get_utc_timestamp(),
        "extractionMethod": extraction_method,
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
        "payload": payload,
    }


def create_chunks_indexed_event(
    document_id: str,
    correlation_id: str,
    chunk_count: int,
    embedding_model: str,
    vector_dim: int,
    index_name: Optional[str] = "marp-documents",
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
            "indexedAt": get_utc_timestamp(),
        },
    }


def create_extraction_failed_event(
    document_id: str, correlation_id: str, error_message: str, error_type: str = "ExtractionError"
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
            "failedAt": get_utc_timestamp(),
        },
    }


def create_ingestion_failed_event(
    document_id: str, correlation_id: str, error_message: str, error_type: str = "IngestionError"
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
            "failedAt": get_utc_timestamp(),
        },
    }


def create_indexing_failed_event(
    document_id: str, correlation_id: str, error_message: str, error_type: str = "IndexingError"
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
            "failedAt": get_utc_timestamp(),
        },
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
    correlation_id: Optional[str] = None,
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
            "results": results_summary or [],
        },
    }


# ----------------------------------------------------------------------------
# User Interaction Events
# ----------------------------------------------------------------------------


def create_query_submitted_event(
    query: str,
    user_session_id: str,
    model_id: str,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "eventType": "QuerySubmitted",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id or generate_event_id(),
        "source": "chat-service",
        "version": "1.0",
        "payload": {
            "query": query,
            "userSessionId": user_session_id,
            "modelId": model_id,
            "submittedAt": get_utc_timestamp(),
        },
    }


def create_response_generated_event(
    query: str,
    response: str,
    model_id: str,
    user_session_id: str,
    latency_ms: float,
    token_count: Optional[int] = None,
    citation_count: int = 0,
    retrieval_count: int = 0,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "query": query,
        "response": response,
        "modelId": model_id,
        "userSessionId": user_session_id,
        "latencyMs": latency_ms,
        "citationCount": citation_count,
        "retrievalCount": retrieval_count,
        "generatedAt": get_utc_timestamp(),
    }

    if token_count is not None:
        payload["tokenCount"] = token_count

    return {
        "eventType": "ResponseGenerated",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id or generate_event_id(),
        "source": "chat-service",
        "version": "1.0",
        "payload": payload,
    }


def create_feedback_received_event(
    response_id: str,
    user_session_id: str,
    feedback_type: str,  # "positive", "negative"
    comment: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "responseId": response_id,
        "userSessionId": user_session_id,
        "feedbackType": feedback_type,
        "receivedAt": get_utc_timestamp(),
    }

    if comment:
        payload["comment"] = comment

    return {
        "eventType": "FeedbackReceived",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id or generate_event_id(),
        "source": "chat-service",
        "version": "1.0",
        "payload": payload,
    }


def create_citation_clicked_event(
    citation_id: str,
    document_id: str,
    page_number: int,
    user_session_id: str,
    response_id: str,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "eventType": "CitationClicked",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id or generate_event_id(),
        "source": "ui-service",
        "version": "1.0",
        "payload": {
            "citationId": citation_id,
            "documentId": document_id,
            "pageNumber": page_number,
            "userSessionId": user_session_id,
            "responseId": response_id,
            "clickedAt": get_utc_timestamp(),
        },
    }


def create_model_comparison_triggered_event(
    query: str,
    user_session_id: str,
    models: list,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "eventType": "ModelComparisonTriggered",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id or generate_event_id(),
        "source": "chat-service",
        "version": "1.0",
        "payload": {
            "query": query,
            "userSessionId": user_session_id,
            "models": models,
            "triggeredAt": get_utc_timestamp(),
        },
    }


def create_model_selected_event(
    model_id: str,
    user_session_id: str,
    comparison_id: str,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "eventType": "ModelSelected",
        "eventId": generate_event_id(),
        "timestamp": get_utc_timestamp(),
        "correlationId": correlation_id or generate_event_id(),
        "source": "chat-service",
        "version": "1.0",
        "payload": {
            "modelId": model_id,
            "userSessionId": user_session_id,
            "comparisonId": comparison_id,
            "selectedAt": get_utc_timestamp(),
        },
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

# User Interaction Routing Keys
ROUTING_KEY_QUERY_SUBMITTED = "analytics.query.submitted"
ROUTING_KEY_RESPONSE_GENERATED = "analytics.response.generated"
ROUTING_KEY_FEEDBACK_RECEIVED = "analytics.feedback.received"
ROUTING_KEY_CITATION_CLICKED = "analytics.citation.clicked"
ROUTING_KEY_MODEL_COMPARISON_TRIGGERED = "analytics.model.comparison.triggered"
ROUTING_KEY_MODEL_SELECTED = "analytics.model.selected"
