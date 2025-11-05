# Indexing Service Pipeline

Overview of the document chunking and vector embedding process.

``` mermaid
sequenceDiagram
  participant BR as RabbitMQ Broker
  participant IX as Indexing Worker
  participant FS as File System
  participant ST as SentenceTransformer<br/>(all-MiniLM-L6-v2)
  participant QD as Qdrant<br/>(Vector Database)

  Note over BR: DocumentExtracted event<br/>arrives in queue

  BR->>IX: Consume DocumentExtracted

  IX->>FS: Read extracted.json
  IX->>FS: Read pages.jsonl

  Note over IX: Load embedding model<br/>(30 seconds, done once at startup)

  loop For each page
    IX->>IX: Chunk text into tokens<br/>(200 tokens, 50 overlap)

    Note over IX: Creates 5-10 chunks per page
  end

  IX->>ST: Encode chunks (batch of 32)
  ST-->>IX: 384-dimensional embeddings

  Note over IX: Prepare Qdrant points<br/>(vector + metadata)

  IX->>QD: Upsert batch of points<br/>to marp-documents collection
  QD-->>IX: Success confirmation

  IX->>FS: Save chunks.json<br/>(for debugging)

  IX->>BR: Publish ChunksIndexed event

  Note over BR: Event sent to<br/>documents.indexed queue

  IX->>IX: Acknowledge message

  Note over IX: Indexing complete
```

## ChunksIndexed Event

```json
{
  "eventType": "ChunksIndexed",
  "eventId": "uuid",
  "timestamp": "2025-11-02T14:53:45Z",
  "correlationId": "uuid",
  "source": "indexing-service",
  "version": "1.0",
  "payload": {
    "documentId": "Intro-to-MARP",
    "chunkCount": 87,
    "embeddingModel": "all-MiniLM-L6-v2",
    "vectorDimension": 384,
    "collectionName": "marp-documents",
    "indexedAt": "2025-11-02T14:53:45Z"
  }
}
```

## Files Created

```
storage/extracted/
  Intro-to-MARP/
    discovered.json     ← (from ingestion)
    pages.jsonl         ← (from extraction)
    extracted.json      ← (from extraction)
    chunks.json         ← Chunk metadata (debugging)
```

## Example Qdrant Point

```json
{
  "id": 1234567890123456,
  "vector": [0.023, -0.145, 0.891, ...],  // 384 dimensions
  "payload": {
    "text": "Students must complete 120 credits across three years...",
    "document_id": "Intro-to-MARP",
    "chunk_index": 5,
    "title": "Introduction to MARP",
    "page": 2,
    "url": "https://www.lancaster.ac.uk/.../Intro-to-MARP.pdf"
  }
}
```

## Chunking Strategy

- **Method**: Token-based sliding window
- **Max tokens per chunk**: 200 (stays under model's 256 limit)
- **Overlap**: 50 tokens (25% context preservation)
- **Tokenizer**: SentenceTransformer tokenizer (accurate counting)

## Technologies

- **Worker**: Python worker process
- **ML Framework**: SentenceTransformers
- **Embedding Model**: all-MiniLM-L6-v2 (384-dim)
- **Vector Database**: Qdrant (cosine similarity)
- **Message Broker**: RabbitMQ (pika client)
- **Health Check**: HTTP server on port 8080
