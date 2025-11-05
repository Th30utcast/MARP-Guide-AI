# Service Name: Retrieval Service

## Responsibility

Provides semantic search API over indexed documents using vector similarity search.

## Data Owned

This service is stateless and does not own data. It queries:

- Vector embeddings from Qdrant (collection: `marp-documents`)
- Uses the same embedding model (all-MiniLM-L6-v2) for query encoding

## API Endpoints

- [POST] /search - Execute semantic search over indexed documents
- [GET] /health - Liveness probe
- [GET] /ready - Readiness probe (checks Qdrant connectivity)

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
      "text": "string (chunk content, max 800 chars)",
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
- 413 Payload Too Large - Query exceeds max length (512 chars)
- 429 Too Many Requests - Rate limit exceeded
- 500 Internal Server Error - Qdrant connection failed

**Notes:**

- Results are ordered by descending similarity score
- Duplicate text chunks are removed from results
- Text chunks are trimmed to 800 characters for response efficiency

### GET /health

Liveness probe

```http
# Response: 200 OK
# Body: { "status": "ok" }
```

### GET /ready

Readiness probe (checks if Qdrant is reachable)

```http
# Response: 200 OK - Service is ready
# Body: { "status": "ready" }

# Response: 503 Service Unavailable - Qdrant not reachable
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

Routing key: `retrieval.query.completed`

## Technical Details

- **Model**: all-MiniLM-L6-v2 (loaded once at startup)
- **Vector dimension**: 384
- **Search method**: Cosine similarity in Qdrant
- **Query timeout**: 30 seconds
- **Max query length**: 512 characters
- **Deduplication**: Removes duplicate text from results
