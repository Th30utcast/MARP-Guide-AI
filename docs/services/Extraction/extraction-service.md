# Service Name: Extraction Service

## Responsibility

Extracts text and metadata from PDF documents page-by-page using pdfplumber.

## Data Owned

- Extracted page content (stored in `/app/storage/extracted/{document_id}/pages.jsonl`)
- Extraction events (stored in `/app/storage/extracted/{document_id}/extracted.json`)
- PDF metadata (page count, creation date, extracted text statistics)

## API Endpoints

This service operates as an event-driven worker consuming from RabbitMQ. It does not expose HTTP endpoints except:

- [GET] /health - Health check endpoint (port 8080)

## Extraction Service Events

### Events Consumed

#### DocumentDiscovered

Consumes events from the Ingestion Service to begin extraction

```json
{
  "eventType": "DocumentDiscovered",
  "payload": {
    "document_id": "string",
    "url": "string (local file path)",
    "title": "string"
  }
}
```

Queue: `extraction_queue`
Routing key: `documents.discovered`

### Events Published

#### DocumentExtracted

Emitted when PDF extraction is successfully completed

```json
{
  "eventType": "DocumentExtracted",
  "eventId": "uuid",
  "timestamp": "ISO-8601",
  "correlationId": "uuid",
  "source": "extraction-service",
  "version": "1.0",
  "payload": {
    "document_id": "string",
    "page_count": "integer",
    "text_extracted": "boolean",
    "extraction_method": "pdfplumber",
    "pdf_metadata": {
      "title": "string",
      "author": "string",
      "creation_date": "string",
      "year": "integer"
    },
    "pages_ref": "string (absolute path to pages.jsonl)"
  }
}
```

Routing key: `documents.extracted`

#### ExtractionFailed

Emitted when PDF extraction fails

```json
{
  "eventType": "ExtractionFailed",
  "payload": {
    "document_id": "string",
    "error": "string",
    "failed_at": "ISO-8601"
  }
}
```

Routing key: `documents.extraction.failed`

## Data Format

### pages.jsonl

One JSON object per line, each representing a page:

```jsonl
{"documentId": "doc123", "page": 1, "text": "Page 1 content..."}
{"documentId": "doc123", "page": 2, "text": "Page 2 content..."}
```
