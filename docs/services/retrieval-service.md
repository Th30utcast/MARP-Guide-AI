Retrieval Service
Overview: Handles search requests across indexed documents. It receives a user query, retrieves the most relevant chunks or snippets from the vector database, and returns them ranked by similarity score.


Retrieval Service API:

POST /search
Execute vector/keyword retrieval against the index
Body (JSON):
{
"query": string, # required
"top_k": integer, # optional, default: 5, max: 20
"filters": { # optional exact-match filters
"source_url": string?,
"content_type": "pdf"|"md"?,
"document_id": string?
}
}
Response: 200 OK
Returns (JSON array length <= top_k):
[
{
"text": string, # snippet/passage
"metadata": {
"id": string, # chunk or doc id
"title": string,
"page": integer?,
"url": string? # canonical link for citation
},
"score": number # higher is more relevant, [0..1]
},
...
]

Errors:
400 Bad Request # missing/invalid "query", invalid "top_k"/filters
413 Payload Too Large # query exceeds max length
429 Too Many Requests # rate limit exceeded
500 Internal Server Error

Notes:
- Results are ordered by descending score; ties break by recency, then id.
- Responses are deterministic for a fixed index version.

GET /healthz
Liveness probe
Response: 200 OK, JSON { "status": "ok" }

GET /readyz
Readiness probe (index + vector store reachable)
Response: 200 OK, JSON { "status": "ready" } or 503 Service Unavailable
Event: RetrievalCompleted (optional)
Emitted after successful /search
Payload schema:
{
"query": string,
"top_k": integer,
"results": [ { "id": string, "title": string, "url": string?, "score": number } ],
"executed_at": ISO-8601,
"trace_id": string
}
Routing key/topic: retrieval.query.completed
Limits:
query.max_length = 512 chars
top_k.default = 5, top_k.max = 20
timeout.ms = 2000
Error Schema (all errors):
{ "type": "about:blank"|string, "code": string, "message": string, "correlation_id": string }
Security (placeholder):
Auth: none (dev) | API key (prod)
CORS: allowlist of origins
