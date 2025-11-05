# Tier 2: Multi-Model Comparison

**Status**: 🚧 **Planned Implementation**

## Feature Scope

- Parallel answer generation with different LLMs
- Side-by-side UI comparison

## Multi-Model Flow

``` mermaid
sequenceDiagram
  participant U as Web UI
  participant C as Chat Service
  participant R as Retrieval Service
  participant LLM1 as Model 1<br/>(e.g., GPT-4)
  participant LLM2 as Model 2<br/>(e.g., Claude)

  U->>C: POST /chat/compare<br/>{message, models: ["gpt-4", "claude"]}

  C->>R: POST /search (same context)
  R-->>C: Retrieved chunks

  par Parallel LLM Calls
    C->>LLM1: Generate answer
    C->>LLM2: Generate answer
  end

  LLM1-->>C: Answer 1
  LLM2-->>C: Answer 2

  C-->>U: {answers: [{model, answer}, ...]}

  Note over U: Display side-by-side
```

## UI Layout

```
┌──────────────────────────────────────────────────┐
│  Question: "What are exam regulations?"          │
├──────────────────────────────────────────────────┤
│  ┌──────────────────┬──────────────────┐         │
│  │   GPT-4          │   Claude         │         │
│  ├──────────────────┼──────────────────┤         │
│  │ Exam regulations │ Examinations     │         │
│  │ state that...    │ must follow...   │         │
│  │                  │                  │         │
│  │ Citations: [1,2] │ Citations: [1,2] │         │
│  └──────────────────┴──────────────────┘         │
└──────────────────────────────────────────────────┘
```

## API Endpoint

```
POST /chat/compare
{
  "message": "What are exam regulations?",
  "models": ["gpt-4", "claude-3"]
}

Response:
{
  "answers": [
    {"model": "gpt-4", "answer": "...", "citations": [...]},
    {"model": "claude-3", "answer": "...", "citations": [...]}
  ]
}
```

## Technologies

- **Async**: asyncio for parallel LLM calls
- **LLM API**: OpenRouter (multi-model access)
- **Frontend**: Side-by-side layout component
