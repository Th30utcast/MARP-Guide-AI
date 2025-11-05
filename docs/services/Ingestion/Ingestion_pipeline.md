# Ingestion Service Pipeline

Overview of the PDF discovery and download process.

``` mermaid
sequenceDiagram
  participant WEB as Lancaster MARP Website
  participant IG as Ingestion Service<br/>(FastAPI)
  participant FS as File System<br/>(/app/pdfs)
  participant BR as RabbitMQ Broker

  Note over IG: Triggered on startup<br/>or via POST /ingest

  IG->>WEB: HTTP GET (scrape MARP page)
  WEB-->>IG: HTML with PDF links

  IG->>IG: Parse with BeautifulSoup<br/>Extract titles & URLs

  loop For each PDF
    IG->>WEB: Download PDF
    WEB-->>IG: PDF file

    IG->>FS: Save {documentId}.pdf
    IG->>FS: Save discovered.json

    IG->>BR: Publish DocumentDiscovered event

    Note over BR: Event sent to<br/>documents.discovered queue
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
    "fileSize": 224431
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

## Technologies

- **Framework**: FastAPI + Uvicorn
- **Web Scraping**: BeautifulSoup4 + lxml
- **HTTP Client**: requests
- **Message Broker**: RabbitMQ (pika client)
