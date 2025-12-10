# Ingestion Service Pipeline

Overview of the PDF discovery and download process.

``` mermaid
sequenceDiagram
  participant WEB as Lancaster MARP Website
  participant IG as Ingestion Service<br/>(FastAPI)
  participant FS as File System<br/>(/app/pdfs)
  participant BR as RabbitMQ Broker

  Note over IG: Triggered automatically<br/>on startup

  IG->>WEB: HTTP GET (scrape MARP page)
  WEB-->>IG: HTML with PDF links

  IG->>IG: Parse with BeautifulSoup<br/>Extract titles & URLs

  loop For each PDF
    IG->>WEB: Download PDF
    WEB-->>IG: PDF file

    IG->>IG: Calculate MD5 checksum<br/>Skip if already exists

    alt Success
      IG->>FS: Save {documentId}.pdf
      IG->>FS: Save discovered.json

      IG->>BR: Publish DocumentDiscovered event
      Note over BR: Event sent to<br/>documents.discovered queue
    else Failure
      IG->>BR: Publish IngestionFailed event
      Note over BR: Event sent to<br/>documents.ingestion.failed
    end
  end

  Note over IG: Ingestion complete
```

## DocumentDiscovered Event

```json
{
  "eventType": "DocumentDiscovered",
  "eventId": "uuid",
  "timestamp": "2025-11-02T14:53:38Z",
  "correlationId": "uuid",
  "source": "ingestion-service",
  "version": "1.0",
  "payload": {
    "documentId": "Intro-to-MARP",
    "title": "Introduction to MARP",
    "url": "/app/pdfs/Intro-to-MARP.pdf",
    "originalUrl": "https://www.lancaster.ac.uk/.../Intro-to-MARP.pdf",
    "fileSize": 224431,
    "checksum": "a3d5e9f2... (MD5)"
  }
}
```

## Files Created

```
pdfs/
  Intro-to-MARP.pdf
  General-Regs.pdf
  ...

storage/extracted/
  Intro-to-MARP/
    discovered.json    ← DocumentDiscovered event
```

## IngestionFailed Event

Published when PDF download or validation fails:

```json
{
  "eventType": "IngestionFailed",
  "eventId": "uuid",
  "timestamp": "2025-11-02T14:54:00Z",
  "correlationId": "uuid",
  "source": "ingestion-service",
  "version": "1.0",
  "payload": {
    "documentId": "Failed-Doc",
    "errorType": "FetchError",
    "errorMessage": "Failed to download PDF: HTTP 404 Not Found",
    "failedAt": "2025-11-02T14:54:00Z"
  }
}
```

Routing key: `documents.ingestion.failed`

## Technologies

- **Framework**: FastAPI + Uvicorn
- **Web Scraping**: BeautifulSoup4 + lxml
- **HTTP Client**: requests
- **Message Broker**: RabbitMQ (pika client)
