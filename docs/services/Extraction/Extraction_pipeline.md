# Extraction Service Pipeline

Overview of the PDF text extraction process.

``` mermaid
sequenceDiagram
  participant BR as RabbitMQ Broker
  participant EX as Extraction Worker
  participant FS as File System
  participant PDF as PDFPlumber

  Note over BR: DocumentDiscovered event<br/>arrives in queue

  BR->>EX: Consume DocumentDiscovered

  EX->>FS: Read discovered.json
  EX->>FS: Read PDF from /app/pdfs

  EX->>PDF: Open PDF file
  PDF-->>EX: PDF object

  loop For each page
    EX->>PDF: Extract text from page
    PDF-->>EX: Page text
    EX->>PDF: Extract metadata
    PDF-->>EX: Title, author, year, etc.
  end

  EX->>FS: Save pages.jsonl<br/>(one page per line)
  EX->>FS: Save extracted.json

  EX->>BR: Publish DocumentExtracted event

  Note over BR: Event sent to<br/>documents.extracted queue

  EX->>EX: Acknowledge message

  Note over EX: Extraction complete
```

## DocumentExtracted Event

```json
{
  "eventType": "DocumentExtracted",
  "eventId": "uuid",
  "timestamp": "2025-11-02T14:53:39Z",
  "correlationId": "uuid",
  "source": "extraction-service",
  "version": "1.0",
  "payload": {
    "documentId": "Intro-to-MARP",
    "textExtracted": true,
    "pageCount": 10,
    "metadata": {
      "title": "MANUAL OF ACADEMIC REGULATIONS AND PROCEDURES (MARP)",
      "author": "Duff, Claire",
      "year": 2025,
      "creator": "Acrobat PDFMaker 25 for Word",
      "producer": "Adobe PDF Library 25.1.213"
    },
    "extractedAt": "2025-11-02T14:53:39Z",
    "extractionMethod": "pdfplumber"
  }
}
```

## Files Created

```
storage/extracted/
  Intro-to-MARP/
    discovered.json     ← (already exists from ingestion)
    pages.jsonl         ← Extracted text (one page per line)
    extracted.json      ← DocumentExtracted event
```

## Example pages.jsonl

```json
{"documentId": "Intro-to-MARP", "page": 1, "text": "MANUAL OF ACADEMIC REGULATIONS..."}
{"documentId": "Intro-to-MARP", "page": 2, "text": "MARP 2025-26 Introduction CONTENTS..."}
{"documentId": "Intro-to-MARP", "page": 3, "text": "SCOPE OF MARP The Manual of..."}
```

## Technologies

- **Worker**: Python worker process
- **PDF Extraction**: pdfplumber 0.10.3
- **Message Broker**: RabbitMQ (pika client)
- **Health Check**: HTTP server on port 8080
