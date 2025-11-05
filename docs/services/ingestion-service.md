Ingestion Service
Overview: Discovers and fetches MARP PDFs from external sources, stores metadata, and publishes discovery events to the message broker for downstream services (Extraction, Indexing).

Ingestion Service API:

POST /documents/discover
Trigger discovery of MARP/PDF sources (async)
Accepts query or JSON params to scope discovery (all optional):
source_url: string (HTTP/HTTPS directory or index page)
repo: string (e.g., "org/repo" or full git URL)
path: string (subdirectory within source)
recursive: boolean (default: true)
include: string (glob/regex for filenames, e.g., ".pdf,.md")
exclude: string (glob/regex to skip paths)
max_depth: integer (crawl depth)
Response: 202 Accepted, returns job ID
Errors: 400 Bad Request (invalid params), 502 Bad Gateway (source fetch failed), 500 Internal Server Error

GET /documents
List discovered documents (latest first)
Optional filters: status (discovered|queued|fetched|failed), source_url, limit, offset
Response: 200 OK, JSON array of documents
Errors: 500 Internal Server Error

GET /documents/{id}
Get metadata and current discovery status for a document
Response: 200 OK, JSON document object
Errors: 404 Not Found, 500 Internal Server Error

GET /healthz
Liveness/readiness probe
Response: 200 OK, JSON { status: "ok" }
Event: DocumentDiscovered
Emitted for each valid item found (message broker)
Payload schema: { id: string, title: string, source_url: string, content_type: "pdf"|"md", discovered_at: ISO-8601 }
Routing key/topic: ingestion.document.discovered
