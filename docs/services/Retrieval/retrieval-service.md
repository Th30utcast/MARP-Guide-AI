# Service Name: Retrieval Service

## Responsibility

Provides semantic search API over indexed documents using vector similarity search.

## Data Owned

This service is stateless and does not own data. It queries:

- Vector embeddings from Qdrant (collection: `marp-documents`)
- Uses the same embedding model (all-MiniLM-L6-v2) for query encoding

## API Endpoints

- [POST] /search - Execute semantic search over indexed documents
- [GET] /health - Health check (includes Qdrant connectivity check)

## Retrieval Service API

### POST /search

Execute vector/keyword retrieval against the index

**Request Body:**

```json
{
  "query": "string (required)",
  "top_k": "integer (optional, default: 5, max: 20)"
}
```

**Response: 200 OK**

```json
{
  "query": "What is the exam policy?",
  "results": [
    {
      "text": "string (chunk content, max 1700 chars)",
      "document_id": "string",
      "chunk_index": "integer",
      "title": "string",
      "page": "integer",
      "url": "string",
      "score": "float (cosine similarity, 0-1)"
    }
  ]
}
```

**Errors:**

- 400 Bad Request - Missing/invalid query or top_k parameter
- 422 Validation Error - Invalid parameter types
- 500 Internal Server Error - Qdrant connection failed or search error

**Notes:**

- Results are ordered by descending similarity score
- Duplicate text chunks are removed from results
- Text chunks are trimmed to 1700 characters for response efficiency

### GET /health

Health check endpoint (checks Qdrant connectivity)

```http
# Response: 200 OK
# Body: { "status": "healthy", "qdrant": "connected" }

# Response: 503 Service Unavailable - Qdrant not reachable
# Body: { "status": "unhealthy", "qdrant": "disconnected" }
```

## Events Published (Optional)

### RetrievalCompleted

Emitted after successful search (optional analytics event)

```json
{
  "eventType": "RetrievalCompleted",
  "payload": {
    "query": "string",
    "top_k": "integer",
    "result_count": "integer",
    "executed_at": "ISO-8601",
    "trace_id": "string"
  }
}
```

Routing key: `retrieval.completed`

## Technical Details

- **Model**: all-MiniLM-L6-v2 (loaded once at startup)
- **Vector dimension**: 384
- **Search method**: Cosine similarity in Qdrant
- **Port**: 8002
- **Deduplication**: Removes duplicate text from results
- **Text truncation**: Results truncated to 1700 chars with "…" suffix

## Configuration

Environment variables:
- `QDRANT_HOST` - Qdrant server hostname (default: "qdrant")
- `QDRANT_PORT` - Qdrant server port (default: 6333)
- `RABBITMQ_HOST` - RabbitMQ server hostname (default: "rabbitmq")
- `RABBITMQ_PORT` - RabbitMQ server port (default: 5672)
