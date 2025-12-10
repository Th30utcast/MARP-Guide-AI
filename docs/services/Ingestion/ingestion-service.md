# Service Name: Ingestion Service

## Responsibility

Discovers and downloads PDF documents from the MARP website, initiating the document processing pipeline.

## Data Owned

- Downloaded PDF files (stored in `/app/pdfs`)
- Document discovery events (stored in `/app/storage/extracted/{document_id}/discovered.json`)
- PDF metadata (title, URL, file size, MD5 checksum)

## API Endpoints

- [POST] /documents/discover - Trigger discovery of MARP PDFs (async)
- [GET] /documents - List all discovered documents
- [GET] /documents/{id} - Get metadata for specific document
- [GET] /health - Health check endpoint

## Ingestion Service API

### POST /documents/discover

Trigger discovery of MARP PDFs

```http
# Response: 202 Accepted, returns job ID
```

### GET /documents

List all discovered documents

```http
# Response: 200 OK, JSON array of documents
```

### GET /documents/{id}

Get metadata for specific document

```http
# Response: 200 OK, JSON document object
# Errors: 404 Not Found
```

### GET /health

Health check endpoint

```http
# Response: 200 OK, JSON { "status": "ok" }
```

## Events Published

### DocumentDiscovered

Emitted when a PDF is successfully discovered and downloaded

```json
{
  "eventType": "DocumentDiscovered",
  "eventId": "uuid",
  "timestamp": "ISO-8601",
  "correlationId": "uuid",
  "source": "ingestion-service",
  "version": "1.0",
  "payload": {
    "document_id": "string",
    "title": "string",
    "url": "string (local file path)",
    "file_size": "integer",
    "checksum": "string (MD5)",
    "original_url": "string (web URL)"
  }
}
```

Routing key: `documents.discovered`

### IngestionFailed

Emitted when PDF discovery or download fails

```json
{
  "eventType": "IngestionFailed",
  "eventId": "uuid",
  "timestamp": "ISO-8601",
  "correlationId": "uuid",
  "source": "ingestion-service",
  "version": "1.0",
  "payload": {
    "document_id": "string",
    "error_type": "string (FetchError, ValidationError, etc.)",
    "error_message": "string",
    "failed_at": "ISO-8601"
  }
}
```

Routing key: `documents.ingestion.failed`

## Configuration

Environment variables:
- `MARP_URL` - Lancaster MARP website URL (default: hardcoded in docker-compose)
- `PDF_OUTPUT_DIR` - Directory for downloaded PDFs (default: "/app/pdfs")
- `STORAGE_PATH` - Directory for event storage (default: "/app/storage/extracted")
- `RABBITMQ_HOST` - RabbitMQ hostname (default: "rabbitmq")
- `RABBITMQ_PORT` - RabbitMQ port (default: 5672)

## Technical Details

- **Port**: 8001
- **Scraping**: BeautifulSoup4 for HTML parsing
- **Download**: Requests library with MD5 checksum validation
- **Event Storage**: JSON files saved to disk for event sourcing
- **Error Handling**: Publishes IngestionFailed events on errors
