RAG / Chat Service
Overview: This is the user-facing API that answers natural language questions using the RAG pipeline.It accepts a message, calls the Retrieval Service internally to fetch relevant snippets, and then generates an answer that includes citations for transparency.


Chat Service API:

POST /chat
Handles user chat queries using the RAG pipeline (Retrieval-Augmented Generation).
Body: {
"message": "What is the exam policy?",
"session_id": "abc123"
}
Response: 200 OK
Returns: {
"answer": "The exam policy states...",
"citations": [
{ "title": "...", "page": 12, "url": "..." },
{ "title": "...", "page": 15, "url": "..." }
]
}
Errors: 400 Bad Request (missing message), 502 Bad Gateway (retrieval failure), 500 Internal Server Error

GET /healthz
Liveness/readiness probe
Response: 200 OK, JSON { "status": "ok" }
Event: AnswerGenerated
Emitted after a successful chat response is generated (message broker).
Payload schema: {
"session_id": string,
"message": string,
"answer": string,
"citations": [ { "title": string, "url": string?, "page": integer? } ],
"generated_at": ISO-8601
}
Routing key/topic: chat.answer.generated
