# Event Catalogue

This document defines all events used in the MARP-Guide AI system. Events enable decoupled communication between microservices following Event-Driven Architecture (EDA) principles.

## Overview

Total Events: 3

| Event Name | Producer Service | Consumer Service(s) |
|------------|-----------------|---------------------|
| DocumentDiscovered | Ingestion Service | Extraction Service |
| DocumentExtracted | Extraction Service | Indexing Service |
| ChunksIndexed | Indexing Service | Chat Service, Monitoring Service |
--- --- --- --- 

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
    "url": "https://lancaster.ac.uk/academic-standards-and-quality/regulations-and-policies/manual-of-academic-regulations-and-procedures/general-regs.pdf",
    "discoveredAt": "2025-10-22T14:30:00Z",
    "fileSize": 2457600
  }
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| documentId | string | Unique identifier for the discovered document |
| title | string | Document title extracted from the webpage or PDF metadata |
| url | string | Full URL to the PDF document |
| discoveredAt | string (ISO 8601) | Timestamp when the document was discovered |
| fileSize | integer | Size of the PDF file in bytes |

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
    "extractionMethod": "pdfplumber"
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

**Consumer Action:**

The Indexing Service subscribes to this event and:
1. Retrieves the extracted text from storage
2. Begins the chunking process
3. Prepares chunks for embedding generation

--- --- --- ---

### 3. ChunksIndexed

**Event Name:** ChunksIndexed

**Triggered By:** Indexing Service

**Consumed By:** Chat Service, Monitoring Service

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
    "vectorDimension": 384,
    "indexedAt": "2025-10-22T14:35:42Z",
    "vectorDbCollection": "marp-documents"
  }
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| documentId | string | Unique identifier for the document (matches previous events) |
| chunkCount | integer | Number of chunks created and indexed |
| embeddingModel | string | Name of the embedding model used |
| vectorDimension | integer | Dimension of the embedding vectors |
| indexedAt | string (ISO 8601) | Timestamp when indexing completed |
| vectorDbCollection | string | Name of the vector database collection |

**Consumer Action:**

The Chat Service subscribes to this event and:
1. Updates its internal registry of available documents
2. Makes the document searchable for user queries

The Monitoring Service subscribes to this event and:
1. Updates indexing statistics
2. Tracks system health metrics

--- --- --- ---

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

```
DocumentDiscovered (correlationId: abc-123-xyz)
    ↓
DocumentExtracted (correlationId: abc-123-xyz)
    ↓
ChunksIndexed (correlationId: abc-123-xyz)
```

All events related to processing a single document share the same `correlationId`, enabling:
- End-to-end system monitoring
- Debugging and troubleshooting
- Performance analysis per document

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

**Last Updated:** Oct 26 2025
**Assessment:** Assessment 1 - First Increment
