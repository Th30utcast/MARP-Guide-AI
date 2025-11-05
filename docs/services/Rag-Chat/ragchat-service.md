# Service Name: Chat Service (RAG)

## Responsibility

Implements RAG-powered question answering by combining retrieval with LLM generation to answer user queries about MARP documentation.

## Data Owned

This service is stateless and does not persist data. It orchestrates:

- Calls to Retrieval Service for relevant document chunks
- Calls to OpenRouter API for LLM-based answer generation
- In-memory prompt construction and response formatting

## API Endpoints

- [POST] /chat - Handle user chat queries using RAG pipeline
- [GET] /health - Health check endpoint

## Chat Service API

### POST /chat

Handles user chat queries using the RAG pipeline (Retrieval-Augmented Generation)

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
  "answer": "According to the MARP Academic Regulations 2024 (page 15), students must complete...",
  "citations": [
    {
      "title": "Academic Regulations 2024",
      "page": 15,
      "url": "https://..."
    },
    {
      "title": "Examination Guidelines",
      "page": 8,
      "url": "https://..."
    }
  ]
}
```

**Errors:**

- 400 Bad Request - Missing or invalid query
- 502 Bad Gateway - Retrieval Service or OpenRouter API failure
- 500 Internal Server Error

### GET /health

Liveness/readiness probe

```http
# Response: 200 OK
# Body: { "status": "ok" }
```

## RAG Pipeline (4 Steps)

### 1. Retrieval

Calls Retrieval Service with user query to get top-K relevant chunks

```http
POST http://retrieval:8002/search
Body: { "query": "...", "top_k": 5 }
```

### 2. Augmentation

Builds RAG prompt with:

- System instructions (answer based on context only)
- Context from retrieved chunks (max 2000 tokens)
- User query
- Citation requirements

**Prompt Template:**

```text
You are a helpful assistant that answers questions about Lancaster University's MARP.

IMPORTANT:
- Answer ONLY based on provided context
- Include specific references (titles and page numbers)
- Be concise and clear
- Use academic language

CONTEXT:
[Source: Academic Regulations 2024 - Page 15]
Students must complete 120 credits...

---

[Source: Examination Guidelines - Page 8]
The exam policy states...

QUESTION: What is the exam policy?

ANSWER:
```

### 3. Generation

Sends prompt to OpenRouter API using DeepSeek Chat v3.1 model

**Configuration:**

- Model: `deepseek/deepseek-chat-v3.1:free`
- Temperature: 0.7
- Max tokens: 500
- Timeout: 60 seconds

### 4. Citation

Extracts citations from retrieved chunks, removing duplicates by (title, page)

## Events Published (Optional)

### AnswerGenerated

Emitted after successful chat response (optional analytics event)

```json
{
  "eventType": "AnswerGenerated",
  "payload": {
    "query": "string",
    "answer": "string",
    "citation_count": "integer",
    "generated_at": "ISO-8601",
    "trace_id": "string"
  }
}
```

Routing key: `chat.answer.generated`

## Technical Details

- **Retrieval Client**: HTTP calls to Retrieval Service (httpx)
- **LLM Provider**: OpenRouter API (OpenAI SDK compatible)
- **LLM Model**: DeepSeek Chat v3.1 (free tier)
- **Context Management**: Limits context to 2000 tokens (~8000 characters)
- **Token Estimation**: ~4 characters per token
- **Citation Deduplication**: Removes duplicate (title, page) pairs
- **Error Handling**: Returns helpful message if no relevant chunks found
