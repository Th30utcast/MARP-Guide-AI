# Tier 2: Multi-Model Comparison

**Status**: 🚧 **Planned Implementation**

## Feature Scope

- Parallel answer generation with different LLMs (2-4 models)
- Side-by-side UI comparison
- User selects which models to compare
- Same retrieval context shared across all models
- Display model name, answer, and citations for each
- Store comparison results temporarily (same session storage as regular chat)
- Handle model failures gracefully (show error for failed model)

## Multi-Model Flow

``` mermaid
sequenceDiagram
  participant U as Web UI
  participant C as Chat Service
  participant A as Auth Service
  participant R as Redis
  participant Ret as Retrieval Service
  participant OR as OpenRouter API

  Note over U: User selects models & sends message

  U->>C: POST /chat/compare<br/>Headers: {session_token}<br/>{message, models: ["gpt-4", "claude"]}

  C->>A: Validate session
  A-->>C: {user_id}

  C->>R: Get chat:{user_id}
  C->>Ret: POST /retrieve (same context)
  Ret-->>C: {chunks, metadata}

  par Parallel LLM Calls
    C->>OR: Call model 1 (gpt-4)
    C->>OR: Call model 2 (claude)
  end

  OR-->>C: Response 1
  OR-->>C: Response 2

  C->>R: Store comparison result

  Note over C: Store as special<br/>comparison message type

  C-->>U: {answers: [{model, answer, citations}, ...]}

  Note over U: Display side-by-side
```

## UI Layout

```
┌────────────────────────────────────────────────────────┐
│  [Model Selector: □ GPT-4  □ Claude  □ Gemini]  [Send] │
├────────────────────────────────────────────────────────┤
│  Question: "What are exam regulations?"                │
├────────────────────────────────────────────────────────┤
│  ┌────────────────────┬────────────────────┐           │
│  │   GPT-4            │   Claude           │           │
│  ├────────────────────┼────────────────────┤           │
│  │ Exam regulations   │ Examinations       │           │
│  │ state that...      │ must follow...     │           │
│  │                    │                    │           │
│  │ Citations: [1,2]   │ Citations: [1,2]   │           │
│  └────────────────────┴────────────────────┘           │
│                                                         │
│  [Switch to regular chat mode]                         │
└────────────────────────────────────────────────────────┘
```

## API Endpoints

**Chat Service:**
```
POST /chat/compare        - Send message to multiple models
GET  /chat/history        - Returns both regular and comparison messages
```

**Request Format:**
```json
POST /chat/compare
Headers: {Authorization: Bearer <token>}
{
  "message": "What are exam regulations?",
  "models": ["gpt-4", "claude-sonnet-3.5"]
}
```

**Response Format:**
```json
{
  "message_id": "uuid",
  "user_message": "What are exam regulations?",
  "answers": [
    {
      "model": "gpt-4",
      "answer": "...",
      "citations": [...],
      "error": null
    },
    {
      "model": "claude-sonnet-3.5",
      "answer": "...",
      "citations": [...],
      "error": null
    }
  ],
  "retrieved_context": [...],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Technologies

- **Async**: asyncio for parallel LLM calls
- **LLM API**: OpenRouter (multi-model access)
- **Frontend**: Side-by-side layout component with model selector
- **Storage**: Redis (same temporary storage as regular chat)

---

## 1. Architecture Overview

**Modified Services:**
- **Chat Service**: Add compare endpoint, parallel LLM calling, comparison message storage

**Dependencies:**
- Builds on Tier 1 (Authentication & Session Management)
- Requires Auth Service for session validation
- Uses same Redis storage for comparison results
- Uses same Retrieval Service for document search
- Calls OpenRouter API with different model parameters

**No New Infrastructure:**
- Uses existing Redis for storage
- Uses existing Auth Service
- Uses existing Retrieval Service
- Only Chat Service needs modifications

## 2. Chat Service Modifications

**New Endpoint:**

**POST /chat/compare**
- Accept session token from Authorization header
- Accept message and array of model names
- Call Auth Service to validate token and get user_id
- Retrieve existing chat history from Redis
- Store user message with type "comparison"
- Call Retrieval Service once (same context for all models)
- Make parallel API calls to OpenRouter for each selected model
- Each call uses different model parameter but same prompt and context
- Collect all responses (handle failures gracefully)
- Store comparison result in Redis with all model responses
- Return all answers to frontend

**Modified Endpoint:**

**GET /chat/history**
- Returns both regular messages and comparison messages
- Comparison messages include all model responses
- Frontend renders differently based on message type

**Message Types:**
- Regular message: {role: "user"/"assistant", content, metadata}
- Comparison message: {role: "comparison", user_message, answers: [{model, answer, citations}]}

**Parallel Processing:**
- Use asyncio to call multiple models concurrently
- Set timeout per model call (30 seconds)
- If one model fails, still return results from successful models
- Mark failed models with error message

**Implementation Details:**
- Use asyncio.gather for parallel calls
- Each model call wrapped in try/except
- Same system prompt and retrieved context for all models
- Model parameter passed to OpenRouter to select which LLM
- Parse citations from each model response independently

## 3. Model Configuration

**Supported Models:**
- GPT-4 (OpenAI via OpenRouter)
- GPT-3.5 Turbo (OpenAI via OpenRouter)
- Claude Sonnet 3.5 (Anthropic via OpenRouter)
- Claude Haiku (Anthropic via OpenRouter)
- Gemini Pro (Google via OpenRouter)

**Model Selection:**
- Frontend provides checkboxes or dropdown for model selection
- User must select 2-4 models (minimum 2 for comparison)
- Model names sent to backend as array of strings
- Backend validates model names against allowed list
- Invalid models rejected with error

**OpenRouter Integration:**
- All models called via OpenRouter API
- Single API key, different model parameter
- Format: POST to OpenRouter with model field set per call
- Same request structure, different model value

**Default Models:**
- If user doesn't select, default to GPT-4 and Claude Sonnet 3.5

## 4. Response Storage

**Redis Storage Format:**

Regular chat messages remain same:
```
Key: chat:{user_id}
Value: [
  {role: "user", content: "...", timestamp: "..."},
  {role: "assistant", content: "...", metadata: {...}, timestamp: "..."}
]
```

Comparison messages added:
```
Key: chat:{user_id}
Value: [
  ...,
  {
    role: "comparison",
    user_message: "...",
    answers: [
      {model: "gpt-4", answer: "...", citations: [...], error: null},
      {model: "claude", answer: "...", citations: [...], error: null}
    ],
    retrieved_context: [...],
    timestamp: "..."
  }
]
```

**Storage Lifecycle:**
- Same TTL as regular chat (24 hours)
- Deleted on logout
- Deleted on session expiration
- Deleted on password reset

## 5. Frontend Integration

**UI Components:**

**Model Selector:**
- Checkbox group or multi-select dropdown
- Options: GPT-4, GPT-3.5, Claude Sonnet, Claude Haiku, Gemini
- Minimum 2 models required for comparison
- Maximum 4 models to avoid UI clutter

**Chat Mode Toggle:**
- Switch between regular chat and comparison mode
- Regular mode: single response from one model
- Comparison mode: side-by-side responses from multiple models

**Comparison Display:**
- Grid layout with columns for each model
- Each column shows: model name, answer, citations
- Equal width columns for fair comparison
- If model failed, show error message in that column

**Message Input:**
- Same input box for both modes
- In comparison mode, model selector visible
- In regular mode, model selector hidden

**Chat History Display:**
- Regular messages: standard chat bubble
- Comparison messages: expandable side-by-side view
- User can scroll through history with mixed message types

**Flows:**

**Comparison Chat Flow:**
- User toggles to comparison mode
- User selects 2-4 models via checkboxes
- User enters question
- Call POST /chat/compare with selected models
- Display loading state for all selected models
- Render responses side-by-side as they arrive
- Show error message if model fails

**History Load on Refresh:**
- Call GET /chat/history
- Render regular messages normally
- Render comparison messages in side-by-side layout
- Preserve user's last mode selection (localStorage)

**Mode Switching:**
- User can switch between modes anytime
- Mode preference stored in localStorage
- Comparison mode: shows model selector and calls /chat/compare
- Regular mode: hides model selector and calls /chat/message

## 6. Performance Considerations

**Parallel Processing:**
- All model calls happen concurrently
- Total response time = slowest model response time
- Typical: 5-15 seconds for all models

**Timeouts:**
- Per-model timeout: 30 seconds
- If model times out, mark as error
- Don't block other models

**Rate Limiting:**
- OpenRouter handles rate limiting per model
- If rate limited, return error for that model
- User can retry

**Cost Management:**
- Each comparison costs N model calls (N = number of selected models)
- More expensive than regular chat
- Consider adding warning in UI about costs
- For university project, likely not a concern

## 7. Security Considerations

**Authentication:**
- All comparison endpoints require session token
- Same validation flow as regular chat
- User isolation enforced (chat:{user_id})

**Model Validation:**
- Validate model names against whitelist
- Reject unknown models
- Prevent injection attacks via model names

**Input Validation:**
- Validate message content (same as regular chat)
- Validate models array (2-4 elements)
- Validate each model name is string

**API Key Security:**
- Same OpenRouter API key for all models
- Stored in environment variables
- Never exposed to frontend

## 8. Data Isolation

**User Comparison Isolation:**
- Same isolation as regular chat
- All comparison results stored under chat:{user_id}
- No user can access another user's comparisons

**Implementation:**
- Token validation returns user_id
- All Redis operations use user_id in key
- Same pattern as regular chat

## 9. Service Dependencies

**Chat Service depends on:**
- Redis (comparison message storage)
- Auth Service (session validation)
- Retrieval Service (document search)
- OpenRouter API (multiple model access)

**No New Dependencies:**
- Uses existing infrastructure
- Only Chat Service code changes

**Startup Order:**
- Same as Tier 1
- No new services to start

## 10. Environment Configuration

**Chat Service Environment Variables:**
- REDIS_HOST
- AUTH_SERVICE_URL
- RETRIEVAL_SERVICE_URL
- OPENROUTER_API_KEY (same as Tier 1)
