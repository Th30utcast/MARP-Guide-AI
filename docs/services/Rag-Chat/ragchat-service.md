# Service Name: Chat Service (RAG)

## Responsibility

Implements RAG-powered question answering by combining retrieval with LLM generation to answer user queries about MARP documentation.

## Data Owned

This service is stateless and does not persist data. It orchestrates:

- Calls to Retrieval Service for relevant document chunks
- Calls to OpenRouter API for LLM-based answer generation
- In-memory prompt construction and response formatting
- Session validation via Auth Service
- Analytics event publishing via RabbitMQ

## API Endpoints

- [POST] /chat - Handle user chat queries using RAG pipeline (requires authentication)
- [POST] /chat/compare - Multi-model comparison for user queries (requires authentication)
- [POST] /chat/comparison/select - Record user's model selection from comparison (requires authentication)
- [GET] /health - Health check endpoint

## Chat Service API

### POST /chat

Handles user chat queries using the RAG pipeline (Retrieval-Augmented Generation)

**Authentication:** Required via `Authorization: Bearer <session_token>` header

**Request Body:**

```json
{
  "query": "string (required, max 1000 chars)",
  "top_k": "integer (optional, default: 8, range: 1-20)",
  "session_id": "string (optional, for analytics)",
  "model_id": "string (optional, defaults to openai/gpt-4o-mini)"
}
```

**Response: 200 OK**

```json
{
  "query": "What is the exam policy?",
  "answer": "According to the MARP General Regulations [1], students must complete examinations as scheduled. If illness occurs during exams, contact your department immediately [2].",
  "citations": [
    {
      "title": "General Regulations",
      "page": 15,
      "url": "https://lancaster.ac.uk/.../General-Regs.pdf"
    },
    {
      "title": "Assessment Regulations",
      "page": 8,
      "url": "https://lancaster.ac.uk/.../Assessment-Regs.pdf"
    }
  ]
}
```

**Errors:**

- 400 Bad Request - Empty query or > 1000 characters
- 401 Unauthorized - Invalid or missing session token
- 500 Internal Server Error - Chat processing failed

**Quality Features:**
- Query reformulation for typo correction (if enabled)
- Anti-hallucination: Rejects answers without citations
- Citation deduplication and renumbering
- Fallback handling for insufficient information

**Events Published:**
- `QuerySubmitted` - When query received
- `ResponseGenerated` - When answer generated

### POST /chat/compare

Generates answers from multiple LLM models in parallel for comparison

**Authentication:** Required via `Authorization: Bearer <session_token>` header

**Request Body:**

```json
{
  "query": "string (required, max 1000 chars)",
  "top_k": "integer (optional, default: 8, range: 1-20)",
  "session_id": "string (optional, for analytics)"
}
```

**Response: 200 OK**

```json
{
  "query": "What is the exam policy?",
  "results": [
    {
      "model_id": "openai/gpt-4o-mini",
      "model_name": "GPT-4o Mini",
      "answer": "According to MARP [1]...",
      "citations": [...]
    },
    {
      "model_id": "google/gemma-3n-e2b-it:free",
      "model_name": "Google Gemma 3n 2B",
      "answer": "Based on the regulations [1]...",
      "citations": [...]
    },
    {
      "model_id": "deepseek/deepseek-chat",
      "model_name": "DeepSeek Chat",
      "answer": "The exam policy states [1]...",
      "citations": [...]
    }
  ]
}
```

**Events Published:**
- `ModelComparisonTriggered` - When comparison is initiated

### POST /chat/comparison/select

Records user's model preference from comparison results

**Authentication:** Required via `Authorization: Bearer <session_token>` header

**Request Body:**

```json
{
  "query": "string",
  "model_id": "string",
  "answer": "string",
  "session_id": "string (optional)",
  "latency_ms": "float",
  "citation_count": "integer",
  "retrieval_count": "integer"
}
```

**Response: 200 OK**

```json
{
  "status": "ok",
  "message": "Selection recorded"
}
```

**Events Published:**
- `QuerySubmitted` - For selected model only
- `ResponseGenerated` - For selected model only

### GET /health

Health check and configuration status

**Response: 200 OK**

```json
{
  "status": "ok",
  "service": "ChatService",
  "retrieval_url": "http://retrieval:8002",
  "openrouter_configured": true,
  "model": "openai/gpt-4o-mini"
}
```

---

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
- Context from retrieved chunks (max 3500 tokens)
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

Sends prompt to OpenRouter API using configured LLM model

**Configuration:**

- Default Model: `openai/gpt-4o-mini`
- Temperature: 0.4 (balanced for focused answers)
- Max tokens: 1200 (prevents cutoff)
- Max context: 3500 tokens
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

**Authentication:**
- All endpoints require Bearer token authentication
- Session validation via Auth Service `/auth/validate` endpoint
- Returns 401 if session invalid or expired

**Retrieval:**
- HTTP calls to Retrieval Service (via retrieval_client.py)
- Default top_k: 8 chunks

**LLM Integration:**
- Provider: OpenRouter API (OpenAI SDK compatible)
- Primary Model: `openai/gpt-4o-mini` (configurable via OPENROUTER_MODEL env var)
- Temperature: 0.4
- Max tokens: 1200
- Max context: 3500 tokens

**Query Processing:**
- Query reformulation: Optional (configurable via ENABLE_QUERY_REFORMULATION)
- Reformulation model: Same as primary model
- Input validation: Max 1000 characters

**Citation Handling:**
- Anti-hallucination: Rejects answers without citations
- Deduplication: Removes duplicate (title, page) pairs
- Renumbering: Ensures consecutive citation numbers
- Minimum citations: 2 (for final MVP), 1 (for Assessment 1)

**Context Management:**
- Limits context based on model capacity
- Token estimation: ~4 characters per token
- Chunk trimming: Long texts truncated to 1700 chars

**Analytics Events:**
- Published to RabbitMQ exchange: `events`
- Event types: QuerySubmitted, ResponseGenerated
- Events include user_id, session_id, model_id, latency metrics

**Error Handling:**
- No chunks found: Returns fallback message
- LLM timeout: 60 seconds
- Retrieval failure: Returns HTTP 500 with error details

**Configuration:**
- RETRIEVAL_URL: Retrieval Service endpoint
- OPENROUTER_API_KEY: OpenRouter API key
- REDIS_HOST/PORT: Session storage
- RABBITMQ_HOST/PORT: Event publishing
- PRIMARY_MODEL_ID: Default LLM model
- ENABLE_QUERY_REFORMULATION: Enable/disable query reformulation
