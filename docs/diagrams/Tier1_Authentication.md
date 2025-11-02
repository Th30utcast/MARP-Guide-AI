# Tier 1: User Authentication & Session Management

**Status**: 🚧 **Planned Implementation**

## Feature Scope

- Login/Logout functionality
- Session handling (token-based)
- User-specific chat isolation (each user only sees their own chats)

## Authentication Flow

``` mermaid
sequenceDiagram
  participant U as Web UI
  participant A as Auth Service
  participant S as Session Store

  Note over U: Login

  U->>A: POST /auth/login<br/>{email, password}
  A->>A: Verify credentials<br/>Hash password check
  A->>S: Create session
  S-->>A: session_token
  A-->>U: {session_token}

  Note over U: Logout

  U->>A: POST /auth/logout<br/>Headers: {session_token}
  A->>S: Delete session
  A-->>U: Success
```

## Chat Isolation Flow

``` mermaid
sequenceDiagram
  participant U as Web UI
  participant C as Chat Service
  participant S as Session Store

  U->>C: POST /chat<br/>Headers: {session_token}<br/>{message: "What are exam rules?"}

  C->>S: Validate session
  S-->>C: {user_id: "user-123"}

  Note over C: Chat is associated<br/>with user_id

  C-->>U: {answer, citations}
```

## Database Schema

```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
  session_token VARCHAR(255) PRIMARY KEY,
  user_id UUID REFERENCES users(user_id),
  expires_at TIMESTAMP NOT NULL
);
```

## API Endpoints

```
POST /auth/login    - Login and get session token
POST /auth/logout   - Logout and invalidate session
```

## Technologies

- **Password Hashing**: bcrypt
- **Session Storage**: Redis or in-memory
- **Tokens**: JWT or random tokens
