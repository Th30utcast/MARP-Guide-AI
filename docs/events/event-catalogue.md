# Event Catalogue

This document defines all events used in the MARP-Guide AI system. Events enable decoupled communication between microservices following Event-Driven Architecture (EDA) principles.

## Overview

Total Events: 7

| Event Name | Producer Service | Consumer Service(s) |
|------------|-----------------|---------------------|
| DocumentDiscovered | Ingestion Service | Extraction Service |
| DocumentExtracted | Extraction Service | Indexing Service |
| ChunksIndexed | Indexing Service | (None - Monitoring Service planned) |
| IngestionFailed | Ingestion Service | (None - Monitoring Service planned) |
| ExtractionFailed | Extraction Service | (None - Monitoring Service planned) |
| IndexingFailed | Indexing Service | (None - Monitoring Service planned) |
| RetrievalCompleted | Retrieval Service | (None - Monitoring Service planned) |

--- 

## Event Definitions

### 1. DocumentDiscovered

**Event Name:** DocumentDiscovered

**Triggered By:** Ingestion Service

**Consumed By:** Extraction Service

**Purpose:** Notifies the system that a new MARP PDF document has been discovered and is ready for extraction.

**Schema:**

```json
{
  "eventType": "DocumentDiscovered",
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-10-22T14:30:00Z",
  "correlationId": "abc-123-xyz",
  "source": "ingestion-service",
  "version": "1.0",
  "payload": {
    "documentId": "marp-general-regs-2025",
    "title": "General Regulations",
    "url": "/app/storage/pdfs/marp-general-regs-2025.pdf",
    "discoveredAt": "2025-10-22T14:30:00Z",
    "fileSize": 2457600,
    "originalUrl": "https://lancaster.ac.uk/academic-standards-and-quality/regulations-and-policies/manual-of-academic-regulations-and-procedures/general-regs.pdf"
  }
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| documentId | string | Unique identifier for the discovered document |
| title | string | Document title extracted from the webpage or PDF metadata |
| url | string | Path to the downloaded PDF file (local file path for extraction) |
| discoveredAt | string (ISO 8601) | Timestamp when the document was discovered |
| fileSize | integer | Size of the PDF file in bytes |
| originalUrl | string (optional) | Original web URL where the PDF was fetched from |

**Consumer Action:**

The Extraction Service subscribes to this event and:
1. Downloads the PDF from the provided URL
2. Validates the file integrity
3. Prepares it for text and metadata extraction

--- --- --- --- 

### 2. DocumentExtracted

**Event Name:** DocumentExtracted

**Triggered By:** Extraction Service

**Consumed By:** Indexing Service

**Purpose:** Notifies the system that text and metadata have been successfully extracted from a PDF document and are ready for chunking and indexing.

**Schema:**

```json
{
  "eventType": "DocumentExtracted",
  "eventId": "660f9500-f39c-52e5-b827-557766551111",
  "timestamp": "2025-10-22T14:32:15Z",
  "correlationId": "abc-123-xyz",
  "source": "extraction-service",
  "version": "1.0",
  "payload": {
    "documentId": "marp-general-regs-2025",
    "textExtracted": true,
    "pageCount": 45,
    "metadata": {
      "title": "General Regulations",
      "author": "Lancaster University",
      "year": 2025,
      "subject": "Academic Regulations"
    },
    "extractedAt": "2025-10-22T14:32:15Z",
    "extractionMethod": "pdfplumber",
    "url": "https://lancaster.ac.uk/academic-standards-and-quality/regulations-and-policies/manual-of-academic-regulations-and-procedures/general-regs.pdf",
    "pagesRef": "/app/storage/extracted/marp-general-regs-2025/pages.jsonl"
  }
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| documentId | string | Unique identifier for the document (matches DocumentDiscovered) |
| textExtracted | boolean | Whether text extraction was successful |
| pageCount | integer | Total number of pages in the PDF |
| metadata | object | PDF metadata (title, author, year, subject) |
| extractedAt | string (ISO 8601) | Timestamp when extraction completed |
| extractionMethod | string | Tool/library used for extraction (e.g., "pdfplumber", "PyPDF2") |
| url | string (optional) | Original source URL of the PDF document (for citations) |
| pagesRef | string (optional) | File path to the extracted pages data (pages.jsonl) |

**Consumer Action:**

The Indexing Service subscribes to this event and:
1. Retrieves the extracted text from storage
2. Begins the chunking process
3. Prepares chunks for embedding generation

--- --- --- ---

### 3. ChunksIndexed

**Event Name:** ChunksIndexed

**Triggered By:** Indexing Service

**Consumed By:** (None - Monitoring Service planned)

**Purpose:** Notifies the system that document chunks have been embedded and indexed in the vector database, making them available for retrieval.

**Schema:**

```json
{
  "eventType": "ChunksIndexed",
  "eventId": "770a0611-g40d-63f6-c938-668877662222",
  "timestamp": "2025-10-22T14:35:42Z",
  "correlationId": "abc-123-xyz",
  "source": "indexing-service",
  "version": "1.0",
  "payload": {
    "documentId": "marp-general-regs-2025",
    "chunkCount": 142,
    "embeddingModel": "all-MiniLM-L6-v2",
    "vectorDim": 384,
    "indexName": "marp-documents",
    "indexedAt": "2025-10-22T14:35:42Z"
  }
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| documentId | string | Unique identifier for the document (matches previous events) |
| chunkCount | integer | Number of chunks created and indexed |
| embeddingModel | string | Name of the embedding model used |
| vectorDim | integer | Dimension of the embedding vectors |
| indexName | string | Name of the vector database collection |
| indexedAt | string (ISO 8601) | Timestamp when indexing completed |

**Consumer Action:**

(Planned) The Monitoring Service will subscribe to this event and:
1. Update indexing statistics
2. Track system health metrics

---

### 4. IngestionFailed

**Event Name:** IngestionFailed

**Triggered By:** Ingestion Service

**Consumed By:** (None - Monitoring Service planned)

**Purpose:** Notifies the system that document ingestion has failed, enabling error tracking and alerting.

**Schema:**

```json
{
  "eventType": "IngestionFailed",
  "eventId": "880b1722-h51e-74g7-d049-779988773333",
  "timestamp": "2025-10-22T14:31:00Z",
  "correlationId": "abc-123-xyz",
  "source": "ingestion-service",
  "version": "1.0",
  "payload": {
    "documentId": "marp-general-regs-2025",
    "errorType": "FetchError",
    "errorMessage": "Failed to download PDF: HTTP 404 Not Found",
    "failedAt": "2025-10-22T14:31:00Z"
  }
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| documentId | string | Unique identifier for the document |
| errorType | string | Type of error (IngestionError, FetchError, etc.) |
| errorMessage | string | Detailed error description |
| failedAt | string (ISO 8601) | Timestamp when failure occurred |

**Consumer Action:**

(Planned) The Monitoring Service will subscribe to this event and:
1. Log errors for debugging
2. Trigger alerts if failure rate exceeds threshold
3. Update ingestion failure metrics

---

### 5. ExtractionFailed

**Event Name:** ExtractionFailed

**Triggered By:** Extraction Service

**Consumed By:** (None - Monitoring Service planned)

**Purpose:** Notifies the system that PDF extraction has failed, enabling error tracking and retry logic.

**Schema:**

```json
{
  "eventType": "ExtractionFailed",
  "eventId": "990c2833-i62f-85h8-e150-880099884444",
  "timestamp": "2025-10-22T14:32:30Z",
  "correlationId": "abc-123-xyz",
  "source": "extraction-service",
  "version": "1.0",
  "payload": {
    "documentId": "marp-general-regs-2025",
    "errorType": "CorruptedFileError",
    "errorMessage": "PDF file is corrupted and cannot be parsed",
    "failedAt": "2025-10-22T14:32:30Z"
  }
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| documentId | string | Unique identifier for the document (matches DocumentDiscovered) |
| errorType | string | Type of error (ExtractionError, FileNotFound, CorruptedFileError, etc.) |
| errorMessage | string | Detailed error description |
| failedAt | string (ISO 8601) | Timestamp when failure occurred |

**Consumer Action:**

(Planned) The Monitoring Service will subscribe to this event and:
1. Log errors for debugging
2. Track extraction failure patterns
3. Trigger alerts for repeated failures

---

### 6. IndexingFailed

**Event Name:** IndexingFailed

**Triggered By:** Indexing Service

**Consumed By:** (None - Monitoring Service planned)

**Purpose:** Notifies the system that document indexing has failed, enabling error tracking and recovery.

**Schema:**

```json
{
  "eventType": "IndexingFailed",
  "eventId": "aa0d3944-j73g-96i9-f261-991100995555",
  "timestamp": "2025-10-22T14:36:00Z",
  "correlationId": "abc-123-xyz",
  "source": "indexing-service",
  "version": "1.0",
  "payload": {
    "documentId": "marp-general-regs-2025",
    "errorType": "VectorDBError",
    "errorMessage": "Failed to connect to Qdrant: Connection timeout",
    "failedAt": "2025-10-22T14:36:00Z"
  }
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| documentId | string | Unique identifier for the document (matches previous events) |
| errorType | string | Type of error (IndexingError, VectorDBError, EmbeddingError, etc.) |
| errorMessage | string | Detailed error description |
| failedAt | string (ISO 8601) | Timestamp when failure occurred |

**Consumer Action:**

(Planned) The Monitoring Service will subscribe to this event and:
1. Log errors for debugging
2. Track indexing failure rates
3. Trigger alerts for infrastructure issues

---

### 7. RetrievalCompleted

**Event Name:** RetrievalCompleted

**Triggered By:** Retrieval Service

**Consumed By:** (None - Monitoring Service planned)

**Purpose:** Logs retrieval operations for analytics, performance monitoring, and query pattern analysis.

**Schema:**

```json
{
  "eventType": "RetrievalCompleted",
  "eventId": "bb0e4055-k84h-a7j0-g372-aa2211aa6666",
  "timestamp": "2025-10-22T15:00:30Z",
  "correlationId": "def-456-uvw",
  "source": "retrieval-service",
  "version": "1.0",
  "payload": {
    "query": "What are the requirements for grade appeals?",
    "topK": 5,
    "resultCount": 5,
    "latencyMs": 145.7,
    "results": [
      {
        "documentId": "marp-general-regs-2025",
        "chunkIndex": 23,
        "score": 0.87
      }
    ]
  }
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| query | string | Original user query string |
| topK | integer | Requested number of results |
| resultCount | integer | Actual number of results returned |
| latencyMs | float | End-to-end retrieval latency in milliseconds |
| results | array | Lightweight summary of results (documentId, chunkIndex, score) |

**Consumer Action:**

(Planned) The Monitoring Service will subscribe to this event and:
1. Track query performance metrics
2. Analyze common query patterns
3. Monitor retrieval latency and quality

---

## Event Design Principles

All events in this catalogue follow these principles:

- **Self-contained:** Events contain all necessary information without requiring additional service queries
- **Immutable:** Events cannot be changed after publishing
- **Minimal:** Include only essential data (no large payloads)
- **Traceable:** All events include `correlationId` for end-to-end tracing
- **Timestamped:** All events use ISO 8601 format timestamps
- **Versioned:** All events include schema version for evolution support

## Standard Event Structure

All events follow this structure:

```json
{
  "eventType": "string",        // Event name in PastTense format
  "eventId": "string (UUID)",   // Unique identifier for this event instance
  "timestamp": "string (ISO 8601)", // When the event occurred
  "correlationId": "string",    // Traces related events through the system
  "source": "string",           // Service that produced this event
  "version": "string",          // Schema version (e.g., "1.0")
  "payload": {                  // Event-specific data
    // varies by event type
  }
}
```

## Correlation ID Tracking

The `correlationId` allows tracing a document's journey through the system:

**Success Flow:**
```
DocumentDiscovered (correlationId: abc-123-xyz)
    ↓
DocumentExtracted (correlationId: abc-123-xyz)
    ↓
ChunksIndexed (correlationId: abc-123-xyz)
```

**Failure Flows:**
```
DocumentDiscovered (correlationId: abc-123-xyz)
    ↓
IngestionFailed (correlationId: abc-123-xyz)
```

```
DocumentDiscovered (correlationId: abc-123-xyz)
    ↓
ExtractionFailed (correlationId: abc-123-xyz)
```

```
DocumentDiscovered (correlationId: abc-123-xyz)
    ↓
DocumentExtracted (correlationId: abc-123-xyz)
    ↓
IndexingFailed (correlationId: abc-123-xyz)
```

All events related to processing a single document share the same `correlationId`, enabling:
- End-to-end system monitoring
- Debugging and troubleshooting
- Performance analysis per document
- Failure tracking and correlation

## Event Versioning Strategy

We use **additive changes only** for schema evolution:
- New optional fields can be added
- Existing fields cannot be removed or changed
- Old consumers ignore new fields
- Maintains backwards compatibility

Example evolution:
```json
// Version 1.0
{
  "payload": {
    "documentId": "...",
    "chunkCount": 142
  }
}

// Version 1.1 (backwards compatible)
{
  "payload": {
    "documentId": "...",
    "chunkCount": 142,
    "processingTimeMs": 1250  // New optional field
  }
}
```

--- --- --- ---

**Last Updated:** Nov 5 2025
**Assessment:** Assessment 1 - First Increment
