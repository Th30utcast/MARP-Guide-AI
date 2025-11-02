# Microservices Architecture with Event Broker

```mermaid
flowchart TB
  subgraph External["External Systems"]
    MARP[Lancaster MARP Website]
  end

  subgraph Ingestion["Ingestion Service (FastAPI)"]
    IG[FastAPI App<br/>]
    Scraper[Web Scraper<br/>]
    Fetcher[PDF Fetcher<br/>Downloads PDFs]
  end

  subgraph Storage["Shared Storage (Docker Volumes)"]
    PDFs[(PDFs Directory<br/>)]
    Events[(Event-Sourced Data<br/>)]
  end

  subgraph Broker["Event Broker (RabbitMQ)"]
    Exchange{events<br/>topic exchange}
    Q1([documents.discovered])
    Q2([documents.extracted])
    Q3([documents.indexed])
  end

  subgraph Extraction["Extraction Service (Worker)"]
    EW[RabbitMQ Consumer<br/>]
    ES[Extraction Service<br/>]
  end

  subgraph Indexing["Indexing Service (Worker)"]
    IW[RabbitMQ Consumer<br/>]
    IS[Indexing Service<br/>]
  end

  subgraph VectorDB["Qdrant Vector Database"]
    VDB[(marp-documents<br/>)]
  end

  subgraph Future["🚧 Future Services"]
    Retrieval[Retrieval Service<br/>Semantic Search]
    Chat[Chat Service<br/>RAG + LLM]
    UI[Web UI<br/>Chat Interface]
  end

  MARP -->|HTTP GET| Scraper
  Scraper --> Fetcher
  Fetcher --> PDFs
  Fetcher --> Events
  IG -->|publish| Exchange
  Exchange --> Q1
  Q1 -->|consume| EW
  EW --> ES
  ES --> PDFs
  ES --> Events
  ES -->|publish| Exchange
  Exchange --> Q2
  Q2 -->|consume| IW
  IW --> IS
  IS --> Events
  IS -->|store vectors| VDB
  IS -->|publish| Exchange
  Exchange --> Q3

  VDB -.->|future| Retrieval
  Retrieval -.->|future| Chat
  Chat -.->|future| UI

  style Ingestion fill:#00A310
  style Extraction fill:#00A310
  style Indexing fill:#00A310
  style Broker fill:#A3A300
  style Storage fill:#003BD1
  style VectorDB fill:#003BD1
  style Future fill:,stroke-dasharray: 5 5
```

## Legend

- **Green**: Implemented and operational services
- **Yellow**: Message broker infrastructure
- **Blue**: Data storage systems
- **Gray (dashed)**: Planned future components

## Current Status

- ✅ **Operational**: Ingestion → Extraction → Indexing pipeline
- 🚧 **In Development**: Retrieval, Chat, and Web UI services

## Event Details

### 1. DocumentDiscovered

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
    "discoveredAt": "2025-11-02T14:53:38Z",
    "fileSize": 224431
  }
}
```

### 2. DocumentExtracted

```json
{
  "eventType": "DocumentExtracted",
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

### 3. ChunksIndexed

```json
{
  "eventType": "ChunksIndexed",
  "payload": {
    "documentId": "Intro-to-MARP",
    "chunkCount": 10,
    "embeddingModel": "all-MiniLM-L6-v2",
    "vectorDim": 384,
    "indexName": "marp-documents",
    "indexedAt": "2025-11-02T14:53:57Z"
  }
}
```

## Storage Structure

```
pdfs/
  Intro-to-MARP.pdf
  General-Regs.pdf
  ...

storage/extracted/
  Intro-to-MARP/
    discovered.json    ← DocumentDiscovered event
    pages.jsonl        ← Extracted text (one page per line)
    extracted.json     ← DocumentExtracted event
    chunks.json        ← All chunks with metadata
    indexed.json       ← ChunksIndexed event
```
