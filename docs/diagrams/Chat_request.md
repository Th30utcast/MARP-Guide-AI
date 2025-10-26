``` mermaid
sequenceDiagram
  participant U as Web UI
  participant C as Chat Service
  participant R as Retrieval Service
  participant V as Vector DB

  U->>C: POST /chat {message, session_id}
  C->>R: POST /search {query, top_k}
  R->>V: embed(query) + search(top_k)
  V-->>R: top-k snippets + metadata
  R-->>C: search results
  C->>C: Compose prompt + call LLM (OpenRouter)
  C-->>U: {answer, citations[title,page,url]}

```