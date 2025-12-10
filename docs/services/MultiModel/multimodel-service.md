# Service Name: Multi-Model Comparison Service

> **NOTICE**
> This is NOT a separate service. Multi-model comparison functionality has been integrated into the Chat Service.
> See [Chat Service Documentation](../Rag-Chat/ragchat-service.md) for current implementation details.
> Endpoints: `POST /chat/compare` and `POST /chat/comparison/select`

## Responsibility

Provides parallel LLM comparison by generating answers from 3 different models simultaneously, allowing users to compare outputs side-by-side and select their preferred model.

## Data Owned

This service is stateless and does not persist data. It orchestrates:

- Parallel calls to 3 LLM models via OpenRouter API
- Shared retrieval context from Retrieval Service
- User model preference saving via Auth Service
- Analytics event publishing via RabbitMQ

## API Endpoints

> **Note:** These endpoints are part of the Chat Service, not a separate service.

- [POST] /chat/compare - Generate parallel answers from 3 LLM models (requires authentication)
- [POST] /chat/comparison/select - Save user's model selection from comparison (requires authentication)

## Multi-Model Comparison API

### POST /chat/compare

Multi-model comparison endpoint - generates answers from 3 LLM models in parallel for side-by-side comparison

**Authentication:** Required via `Authorization: Bearer <session_token>` header

**Request Body:**

```json
{
  "query": "string (required)",
  "top_k": "integer (optional, default: 8)",
  "session_id": "string (optional, for analytics)"
}
```

**Models Used (Current Configuration):**
1. `openai/gpt-4o-mini` (GPT-4o Mini)
2. `google/gemma-3n-e2b-it:free` (Google Gemma 3n 2B)
3. `deepseek/deepseek-chat` (DeepSeek Chat)

> **Note:** Model list is configurable via `COMPARISON_MODELS` in chat service config

**Response: 200 OK**

```json
{
  "query": "What is the grade appeal process?",
  "reformulated_query": "What is the process for appealing academic grades?",
  "results": [
    {
      "model_id": "google/gemma-3n-e2b-it:free",
      "model_name": "Gemini 3N (2B)",
      "answer": "The grade appeal process involves...",
      "citations": [
        {
          "title": "Assessment Regulations",
          "page": 12,
          "url": "https://..."
        }
      ]
    },
    {
      "model_id": "meta-llama/llama-3.2-3b-instruct:free",
      "model_name": "Llama 3.2 (3B)",
      "answer": "To appeal a grade, you must...",
      "citations": [...]
    },
    {
      "model_id": "microsoft/phi-3-mini-128k-instruct:free",
      "model_name": "Phi-3 Mini (3.8B)",
      "answer": "According to MARP regulations...",
      "citations": [...]
    }
  ],
  "latency_ms": 3247.5,
  "retrieval_count": 8
}
```

**Features:**
- Parallel execution (3 models simultaneously using ThreadPoolExecutor)
- Query reformulation before retrieval (optional, configurable)
- Shared document chunks across all models
- Per-model citation extraction
- Total latency includes all parallel calls + retrieval

**Errors:**
- 401 Unauthorized - Invalid or missing session token
- 500 Internal Server Error - Comparison failed

**Events Published:**
- `ModelComparisonTriggered` - When comparison initiated

---

### POST /chat/comparison/select

Save user's model selection from comparison results

**Authentication:** Required via `Authorization: Bearer <session_token>` header

**Query Parameters:**
- `model_id` (required) - Selected model identifier (e.g., "meta-llama/llama-3.2-3b-instruct:free")

**Response: 200 OK**

```json
{
  "message": "Model preference saved",
  "model_id": "meta-llama/llama-3.2-3b-instruct:free"
}
```

**Behavior:**
- Calls Auth Service `/auth/preferences/model` endpoint
- Persists selection across sessions
- Future `/chat` requests can use saved preference

**Errors:**
- 401 Unauthorized - Invalid or missing session token
- 500 Internal Server Error - Failed to save selection

---

## Technical Details

**Authentication:**
- All endpoints require Bearer token authentication
- Session validation via Auth Service `/auth/validate` endpoint
- Returns 401 if session invalid or expired

**Retrieval:**
- HTTP calls to Retrieval Service (via retrieval_client.py)
- Single retrieval call shared across all 3 models
- Default top_k: 8 chunks

**LLM Integration:**
- Provider: OpenRouter API (OpenAI SDK compatible)
- Parallel execution: ThreadPoolExecutor with 3 workers
- Temperature: 0.7
- Max tokens: 500
- Timeout: 60 seconds per model

**Models:**
1. **Gemini 3N (2B)** - `google/gemma-3n-e2b-it:free`
2. **Llama 3.2 (3B)** - `meta-llama/llama-3.2-3b-instruct:free`
3. **Phi-3 Mini (3.8B)** - `microsoft/phi-3-mini-128k-instruct:free`

**Query Processing:**
- Query reformulation: Optional (configurable via ENABLE_QUERY_REFORMULATION)
- Single reformulated query used for all models
- Input validation: Max 1000 characters

**Citation Handling:**
- Per-model citation extraction
- Deduplication: Removes duplicate (title, page) pairs per model
- Each model has independent citation list

**Analytics Events:**
- Published to RabbitMQ exchange: `events`
- Event type: ModelComparisonTriggered
- Includes query, user_id, session_id, models array

**Error Handling:**
- Individual model failures don't block others
- Failed models return error in their result slot
- At least 1 successful model required

**Configuration:**
- RETRIEVAL_URL: Retrieval Service endpoint
- OPENROUTER_API_KEY: OpenRouter API key
- AUTH_SERVICE_URL: Auth Service endpoint
- RABBITMQ_HOST/PORT: Event publishing
- ENABLE_QUERY_REFORMULATION: Enable/disable query reformulation

---

## Service Integration

**Called By:**
- Web UI (comparison view)

**Calls:**
- Retrieval Service (document search)
- OpenRouter API (3 parallel LLM calls)
- Auth Service (session validation, preference saving)

**Publishes Events To:**
- RabbitMQ (ModelComparisonTriggered)

**Network Communication:**
- HTTP REST endpoints (same container as Chat Service, port 8003)
- RabbitMQ AMQP connection on port 5672
