# Chat Service Pipeline (RAG)

Overview of the Retrieval-Augmented Generation process.

```mermaid
sequenceDiagram
  participant USER as User/Client
  participant CHAT as Chat Service<br/>(FastAPI)
  participant RET as Retrieval Service
  participant OR as OpenRouter API<br/>(DeepSeek Chat)
  participant BR as RabbitMQ Broker<br/>(optional)

  USER->>CHAT: POST /chat<br/>{ query, top_k }

  Note over CHAT: Step 1: Retrieval

  CHAT->>RET: POST /search<br/>{ query, top_k }
  RET-->>CHAT: Relevant chunks<br/>(with metadata)

  alt No chunks found
    CHAT-->>USER: 200 OK<br/>"No relevant information found"
  else Chunks retrieved
    Note over CHAT: Step 2: Augmentation<br/>(Build RAG prompt)

    CHAT->>CHAT: Extract text from chunks<br/>(max 2000 tokens)

    CHAT->>CHAT: Build prompt:<br/>- System instructions<br/>- Context chunks<br/>- User query

    Note over CHAT: Step 3: Generation

    CHAT->>OR: POST /chat/completions<br/>(DeepSeek Chat v3.1)
    OR-->>CHAT: Generated answer

    Note over CHAT: Step 4: Citation

    CHAT->>CHAT: Extract citations<br/>(title, page, url)

    CHAT->>CHAT: Deduplicate by (title, page)

    CHAT->>BR: Publish AnswerGenerated<br/>(optional analytics)

    CHAT-->>USER: 200 OK<br/>{ answer, citations[] }
  end
```

## Chat Request

```json
{
  "query": "What is the exam policy?",
  "top_k": 5
}
```

## Chat Response

```json
{
  "query": "What is the exam policy?",
  "answer": "According to the MARP Academic Regulations 2024 (page 15), students must complete 120 credits across three years. The exam policy states that students are required to sit examinations in person unless granted special accommodations. Refer to the Examination Guidelines (page 8) for detailed requirements.",
  "citations": [
    {
      "title": "Academic Regulations 2024",
      "page": 15,
      "url": "https://www.lancaster.ac.uk/.../Academic-Regs.pdf"
    },
    {
      "title": "Examination Guidelines",
      "page": 8,
      "url": "https://www.lancaster.ac.uk/.../Exam-Guidelines.pdf"
    }
  ]
}
```

## Technologies

- **Framework**: FastAPI + Pydantic
- **HTTP Client**: httpx (for Retrieval Service)
- **LLM Provider**: OpenRouter API
- **LLM SDK**: OpenAI SDK (compatible with OpenRouter)
- **Model**: deepseek/deepseek-chat-v3.1:free
- **Message Broker**: RabbitMQ (optional, for analytics)
