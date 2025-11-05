# Retrieval Service Pipeline

Overview of the semantic search process.

``` mermaid
sequenceDiagram
  participant CLIENT as Client<br/>(Chat Service or User)
  participant RT as Retrieval Service<br/>(FastAPI)
  participant ST as SentenceTransformer<br/>(all-MiniLM-L6-v2)
  participant QD as Qdrant<br/>(Vector Database)
  participant BR as RabbitMQ Broker<br/>(optional)

  Note over RT: Model loaded once<br/>at startup (~30s)

  CLIENT->>RT: POST /search<br/>{ query, top_k }

  RT->>RT: Validate request<br/>(query length, top_k range)

  RT->>ST: Encode query text
  ST-->>RT: 384-dimensional query vector

  RT->>QD: Search marp-documents<br/>(cosine similarity)
  QD-->>RT: Top-K similar points<br/>(with scores & metadata)

  RT->>RT: Remove duplicate text chunks

  RT->>RT: Trim text to 800 chars

  RT->>RT: Format SearchResponse<br/>(results with metadata)

  RT->>BR: Publish RetrievalCompleted<br/>(optional analytics)

  RT-->>CLIENT: 200 OK<br/>{ query, results[] }

  Note over CLIENT: Results ready for use<br/>(e.g., RAG context)
```

## Search Request

```json
{
  "query": "What are the graduation requirements?",
  "top_k": 5
}
```

## Search Response

```json
{
  "query": "What are the graduation requirements?",
  "results": [
    {
      "text": "Students must complete 120 credits across three years...",
      "document_id": "Intro-to-MARP",
      "chunk_index": 42,
      "title": "Introduction to MARP",
      "page": 15,
      "url": "https://www.lancaster.ac.uk/.../Intro-to-MARP.pdf",
      "score": 0.87
    },
    {
      "text": "Graduation requirements include successful completion...",
      "document_id": "General-Regs",
      "chunk_index": 12,
      "title": "General Regulations",
      "page": 8,
      "url": "https://www.lancaster.ac.uk/.../General-Regs.pdf",
      "score": 0.82
    }
  ]
}
```

## RetrievalCompleted Event (Optional)

```json
{
  "eventType": "RetrievalCompleted",
  "eventId": "uuid",
  "timestamp": "2025-11-02T14:55:12Z",
  "source": "retrieval-service",
  "version": "1.0",
  "payload": {
    "query": "What are the graduation requirements?",
    "top_k": 5,
    "result_count": 5,
    "executed_at": "2025-11-02T14:55:12Z",
    "trace_id": "trace-xyz"
  }
}
```

## Search Configuration

- **Collection**: marp-documents
- **Distance Metric**: Cosine similarity
- **Vector Dimension**: 384
- **Default top_k**: 5
- **Max top_k**: 20
- **Query timeout**: 30 seconds
- **Max query length**: 512 characters

## Data Flow

1. **Query Encoding**: User text → 384-dimensional vector
2. **Vector Search**: Query vector → Qdrant cosine similarity search
3. **Deduplication**: Remove duplicate text chunks
4. **Formatting**: Trim text, format metadata
5. **Analytics**: Optional event publishing

## Technologies

- **Framework**: FastAPI + Pydantic
- **ML Framework**: SentenceTransformers
- **Embedding Model**: all-MiniLM-L6-v2 (384-dim)
- **Vector Database**: Qdrant (read-only queries)
- **Message Broker**: RabbitMQ (optional, for analytics)
- **HTTP Client**: httpx (async support)
