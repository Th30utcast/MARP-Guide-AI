# Web UI Pipeline

Overview of the user interaction flows through the React-based Web UI.

## Registration Flow

```mermaid
sequenceDiagram
    participant USER as User/Browser
    participant UI as React App<br/>(Web UI)
    participant AUTH as Auth Service<br/>(Port 8004)

    USER->>UI: Navigate to app<br/>(first time)
    UI-->>USER: Show Login page

    USER->>UI: Click "Register"
    UI-->>USER: Show Registration form

    USER->>UI: Submit registration<br/>{email, password}
    UI->>UI: Validate form inputs<br/>(email format, password length)

    alt Validation fails
        UI-->>USER: Show validation error
    else Validation passes
        UI->>AUTH: POST /auth/register<br/>{email, password}

        alt Email already exists
            AUTH-->>UI: 400 Bad Request
            UI-->>USER: "Email already registered"
        else Registration success
            AUTH-->>UI: 201 Created<br/>{user_id, email}
            UI-->>USER: Success message +<br/>redirect to Login
        end
    end
```

## Login and Session Validation Flow

```mermaid
sequenceDiagram
    participant USER as User/Browser
    participant UI as React App<br/>(Web UI)
    participant AUTH as Auth Service<br/>(Port 8004)
    participant LS as LocalStorage

    Note over USER: User logs in
    USER->>UI: Enter credentials
    UI->>AUTH: POST /auth/login<br/>{email, password}

    alt Invalid credentials
        AUTH-->>UI: 401 Unauthorized
        UI-->>USER: "Invalid email or password"
    else Valid credentials
        AUTH-->>UI: 200 OK<br/>{session_token, user_id,<br/>email, is_admin}
        UI->>LS: Store session_token<br/>user_email, user_id
        UI->>UI: Set authenticated state
        UI-->>USER: Redirect to Chat interface
    end

    Note over USER: User refreshes page
    USER->>UI: Reload application
    UI->>LS: Get session_token
    LS-->>UI: {session_token}

    alt No token found
        UI-->>USER: Show Login page
    else Token exists
        UI->>AUTH: GET /auth/validate<br/>Bearer: {token}

        alt Session expired
            AUTH-->>UI: 401 Unauthorized
            UI->>LS: Clear all data
            UI-->>USER: Show Login page
        else Session valid
            AUTH-->>UI: {user_id, email, is_admin}
            UI->>UI: Restore authenticated state
            UI-->>USER: Show Chat interface
        end
    end
```

## Chat Query Flow (First Query)

```mermaid
sequenceDiagram
    participant USER as User/Browser
    participant UI as React App<br/>(Web UI)
    participant CHAT as Chat Service<br/>(Port 8003)
    participant RET as Retrieval Service<br/>(Port 8002)
    participant OR as OpenRouter API

    USER->>UI: Type query + press send
    UI->>UI: Check queryCount<br/>(queryCount = 0)
    UI->>UI: Increment to queryCount = 1

    UI->>CHAT: POST /api/chat<br/>Bearer: {token}<br/>{query, model_id}

    Note over CHAT: Validate session (Redis)

    CHAT->>RET: POST /search<br/>{query, top_k}
    RET-->>CHAT: {results: [...chunks...]}

    CHAT->>OR: POST /chat/completions<br/>(with RAG prompt)
    OR-->>CHAT: Generated answer

    CHAT->>CHAT: Extract citations<br/>Deduplicate<br/>Renumber

    CHAT-->>UI: 200 OK<br/>{answer, citations}

    UI->>UI: Add to chatMessages<br/>Store queryCount = 1
    UI-->>USER: Display answer +<br/>clickable citations
```

## Multi-Model Comparison Flow (Second Query)

```mermaid
sequenceDiagram
    participant USER as User/Browser
    participant UI as React App<br/>(Web UI)
    participant CHAT as Chat Service<br/>(Port 8003)
    participant RET as Retrieval Service
    participant OR1 as OpenRouter<br/>(GPT-4o Mini)
    participant OR2 as OpenRouter<br/>(Gemma 3n)
    participant OR3 as OpenRouter<br/>(DeepSeek)

    USER->>UI: Type query + press send
    UI->>UI: Check queryCount<br/>(queryCount = 1)
    UI->>UI: Detect 2nd query!<br/>Trigger comparison

    UI-->>USER: Show "Comparing models..." loader

    UI->>CHAT: POST /api/chat/compare<br/>Bearer: {token}<br/>{query}

    Note over CHAT: Single retrieval call<br/>(shared across models)
    CHAT->>RET: POST /search<br/>{query, top_k}
    RET-->>CHAT: {results: [...chunks...]}

    Note over CHAT: Parallel generation

    par Model 1
        CHAT->>OR1: GPT-4o Mini
        OR1-->>CHAT: Answer 1
    and Model 2
        CHAT->>OR2: Gemma 3n 2B
        OR2-->>CHAT: Answer 2
    and Model 3
        CHAT->>OR3: DeepSeek Chat
        OR3-->>CHAT: Answer 3
    end

    CHAT->>CHAT: Extract citations<br/>per model

    CHAT-->>UI: 200 OK<br/>{results: [{model, answer, citations}...]}

    UI->>UI: Set comparisonShown = true
    UI-->>USER: Display 3 responses<br/>side-by-side

    USER->>UI: Click "Select this model"<br/>on preferred answer

    UI->>CHAT: POST /api/chat/comparison/select<br/>{query, model_id, answer, ...}
    CHAT-->>UI: 200 OK

    UI->>UI: Store selectedModel<br/>in localStorage
    UI-->>USER: Show "Model selected!" message
```

## Analytics Dashboard Flow

```mermaid
sequenceDiagram
    participant USER as User/Browser
    participant UI as React App<br/>(Web UI)
    participant AN as Analytics Service<br/>(Port 8005)
    participant AUTH as Auth Service

    USER->>UI: Click "Analytics" in sidebar
    UI->>UI: Check if user is admin

    alt Admin User
        UI->>AN: GET /analytics/summary<br/>Bearer: {token}
        AN->>AUTH: Validate session (Redis)
        AUTH-->>AN: {user_id, is_admin: true}
        AN-->>UI: Global statistics<br/>(all users)

        UI->>AN: GET /analytics/queries/popular<br/>Bearer: {token}
        AN-->>UI: Popular queries<br/>(all users)

        UI->>AN: GET /analytics/models/stats<br/>Bearer: {token}
        AN-->>UI: Model performance<br/>(all users)

        UI-->>USER: Display global analytics
    else Regular User
        UI->>AN: GET /analytics/summary<br/>?user_id={user_id}<br/>Bearer: {token}
        AN->>AUTH: Validate session
        AUTH-->>AN: {user_id, is_admin: false}
        AN-->>UI: Personal statistics<br/>(user-specific)

        UI->>AN: GET /analytics/queries/popular<br/>?user_id={user_id}<br/>Bearer: {token}
        AN-->>UI: User's query history

        UI-->>USER: Display personal analytics
    end
```

## Logout Flow

```mermaid
sequenceDiagram
    participant USER as User/Browser
    participant UI as React App<br/>(Web UI)
    participant AUTH as Auth Service<br/>(Port 8004)
    participant LS as LocalStorage

    USER->>UI: Click "Logout" button
    UI->>LS: Get session_token
    LS-->>UI: {session_token}

    UI->>AUTH: POST /auth/logout<br/>Bearer: {token}
    AUTH-->>UI: 200 OK<br/>{"message": "Logout successful"}

    UI->>LS: Clear session_token
    UI->>LS: Clear user_email
    UI->>LS: Clear user_id
    UI->>LS: Clear chatMessages
    UI->>LS: Clear queryCount
    UI->>LS: Clear comparisonShown
    UI->>LS: Clear selectedModel

    UI->>UI: Reset authenticated state
    UI-->>USER: Redirect to Login page
```

## Reset Functionality Flow

```mermaid
sequenceDiagram
    participant USER as User/Browser
    participant UI as React App<br/>(Web UI)
    participant AN as Analytics Service<br/>(Port 8005)
    participant LS as LocalStorage

    USER->>UI: Click "Reset" button
    UI-->>USER: Confirm dialog<br/>"Are you sure?"

    alt User cancels
        USER->>UI: Click "Cancel"
        UI-->>USER: No action
    else User confirms
        USER->>UI: Click "OK"

        UI->>AN: POST /analytics/reset
        AN-->>UI: 200 OK

        UI->>LS: Clear selectedModel
        UI->>LS: Clear comparisonShown
        UI->>LS: Clear chatMessages
        UI->>LS: Clear queryCount

        UI->>UI: Reload page
        UI-->>USER: Fresh state with<br/>empty chat history
    end
```

## Error Handling Flow

```mermaid
sequenceDiagram
    participant USER as User/Browser
    participant UI as React App<br/>(Web UI)
    participant API as Backend API

    USER->>UI: Perform action<br/>(login, query, etc.)
    UI->>API: API request

    alt Network error
        API--xUI: Connection timeout /<br/>Network disconnected
        UI-->>USER: "Network error.<br/>Check your connection."
    else Session expired
        API-->>UI: 401 Unauthorized
        UI->>UI: Clear localStorage
        UI-->>USER: Redirect to Login +<br/>"Session expired"
    else Service error
        API-->>UI: 500 Internal Server Error
        UI-->>USER: "Service error.<br/>Try rephrasing your question."
    else Validation error
        API-->>UI: 400 Bad Request<br/>{detail: "..."}
        UI-->>USER: Show specific error message
    end
```

## Component Hierarchy

```
App.jsx (Root)
├── Login.jsx (Unauthenticated)
├── Register.jsx (Unauthenticated)
└── Authenticated Layout
    ├── Sidebar.jsx
    │   ├── User Info
    │   ├── Navigation (Chat / Analytics)
    │   └── Action Buttons (Logout, Reset)
    │
    └── Main Content Area
        ├── ChatContainer.jsx (if page = "chat")
        │   ├── ModelSelector.jsx
        │   ├── MessageList.jsx
        │   │   ├── Message.jsx (multiple)
        │   │   └── Citation.jsx (multiple)
        │   ├── ChatInput.jsx
        │   └── ModelComparison.jsx (if comparison active)
        │
        └── Analytics.jsx (if page = "analytics")
            ├── Summary Stats
            ├── Popular Queries
            └── Model Performance
```

## State Flow Diagram

```mermaid
stateDiagram-v2
    [*] --> Unauthenticated

    Unauthenticated --> Login: User navigates
    Unauthenticated --> Register: User clicks Register

    Login --> Authenticated: Valid credentials
    Register --> Login: Registration success

    Authenticated --> ChatInterface: Default view
    Authenticated --> Analytics: User navigates

    ChatInterface --> FirstQuery: User submits query (count=0)
    FirstQuery --> ChatInterface: Display answer

    ChatInterface --> SecondQuery: User submits query (count=1)
    SecondQuery --> ComparisonView: Show 3 models
    ComparisonView --> ChatInterface: User selects model

    Analytics --> ChatInterface: User navigates back

    Authenticated --> Unauthenticated: Logout
    Authenticated --> Unauthenticated: Session expired
```

## LocalStorage State Machine

```mermaid
stateDiagram-v2
    [*] --> Empty: App first load

    Empty --> HasCredentials: User logs in
    HasCredentials --> HasChatState: User sends query
    HasChatState --> HasComparison: 2nd query triggers comparison

    HasCredentials --> Empty: Logout
    HasChatState --> Empty: Logout
    HasComparison --> Empty: Logout

    HasCredentials --> Empty: Session expired
    HasChatState --> Empty: Session expired
    HasComparison --> Empty: Session expired

    HasChatState --> HasCredentials: Reset clicked
    HasComparison --> HasCredentials: Reset clicked
```

## API Request Patterns

### Normal Chat Request
```http
POST /api/chat HTTP/1.1
Authorization: Bearer xY9Kp2mN5vT8wQ3rL6zA1bC4eD7fG0hJ
Content-Type: application/json

{
  "query": "What is the exam policy?",
  "model_id": "openai/gpt-4o-mini"
}
```

### Comparison Request
```http
POST /api/chat/compare HTTP/1.1
Authorization: Bearer xY9Kp2mN5vT8wQ3rL6zA1bC4eD7fG0hJ
Content-Type: application/json

{
  "query": "What is the grade appeal process?"
}
```

### Model Selection Recording
```http
POST /api/chat/comparison/select HTTP/1.1
Authorization: Bearer xY9Kp2mN5vT8wQ3rL6zA1bC4eD7fG0hJ
Content-Type: application/json

{
  "query": "What is the grade appeal process?",
  "model_id": "google/gemma-3n-e2b-it:free",
  "answer": "To appeal a grade...",
  "citation_count": 3,
  "retrieval_count": 8,
  "latency_ms": 2847.5
}
```

## Technologies

- **Framework**: React 18.2.0 with Hooks (useState, useEffect)
- **Build Tool**: Vite 5.0.0 (ES modules, HMR)
- **Styling**: Tailwind CSS 3.3.6 + Custom CSS Variables
- **HTTP Client**: Axios 1.6.0 (async/await patterns)
- **Routing**: Client-side state management (no react-router)
- **Markdown**: react-markdown 9.0.0 for answer formatting
- **Production Server**: Nginx (Alpine) with API proxying
- **Deployment**: Multi-stage Docker build
