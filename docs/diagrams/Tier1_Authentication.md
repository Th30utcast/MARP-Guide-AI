# Tier 1: User Authentication & Session Management

**Status**: 🚧 **Planned Implementation**

## Feature Scope

- Open user registration (email and password)
- Login/Logout functionality
- Session handling (token-based, Redis, 24h TTL)
- Password reset via email
- Temporary chat storage (no persistence, deleted on logout)
- User-specific chat isolation (each user only sees their own chat)
- Chat recovery on page refresh (within same session)

## Authentication Flow

``` mermaid
sequenceDiagram
  participant U as Web UI
  participant A as Auth Service
  participant R as Redis
  participant P as PostgreSQL

  Note over U: Registration

  U->>A: POST /auth/register<br/>{email, password}
  A->>A: Validate & hash password
  A->>P: Store user
  A-->>U: {user_id}

  Note over U: Login

  U->>A: POST /auth/login<br/>{email, password}
  A->>P: Verify credentials
  A->>A: Generate session token
  A->>R: Store session (24h TTL)
  A-->>U: {session_token, user_id}

  Note over U: Logout

  U->>A: POST /auth/logout<br/>Headers: {session_token}
  A->>R: Delete session
  A->>R: Delete chat history
  A-->>U: Success
```

## Chat Isolation Flow

``` mermaid
sequenceDiagram
  participant U as Web UI
  participant C as Chat Service
  participant A as Auth Service
  participant R as Redis
  participant Ret as Retrieval Service

  Note over U: Page Load/Refresh

  U->>C: GET /chat/history<br/>Headers: {session_token}
  C->>A: GET /auth/validate
  A->>R: Check session exists
  A-->>C: {user_id, email}
  C->>R: Get chat:{user_id}
  C-->>U: [{messages...}]

  Note over U: Send Message

  U->>C: POST /chat/message<br/>Headers: {session_token}<br/>{message: "What are exam rules?"}
  C->>A: Validate session
  A-->>C: {user_id}
  C->>R: Get chat:{user_id}
  C->>R: Append user message
  C->>Ret: Search documents
  Ret-->>C: {chunks, metadata}
  C->>C: Call OpenRouter LLM
  C->>R: Append assistant response

  Note over C: Chat stored in Redis<br/>with user_id isolation<br/>24h TTL

  C-->>U: {answer, citations}
```

## Database Schema

```sql
-- PostgreSQL Tables
CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE password_resets (
  reset_token UUID PRIMARY KEY,
  user_id UUID REFERENCES users(user_id),
  expires_at TIMESTAMP NOT NULL,
  used BOOLEAN DEFAULT FALSE
);
```

**Redis Structure:**
```
-- Sessions
Key: session:{token}
Value: JSON {user_id, email}
TTL: 24 hours

-- Chat Messages (Temporary)
Key: chat:{user_id}
Value: JSON [{role, content, metadata, timestamp}, ...]
TTL: 24 hours
```

## API Endpoints

**Auth Service:**
```
POST /auth/register       - Register new user
POST /auth/login          - Login and get session token
POST /auth/logout         - Logout and invalidate session
GET  /auth/validate       - Validate session (internal)
POST /auth/reset-request  - Request password reset
POST /auth/reset-password - Reset password with token
```

**Chat Service:**
```
GET    /chat/history      - Get chat history for current session
POST   /chat/message      - Send message and get response
DELETE /chat/clear        - Clear chat history
```

## Technologies

- **Password Hashing**: bcrypt
- **Session Storage**: Redis (24h TTL)
- **Tokens**: Random hex strings (sessions), UUID (password reset)
- **Email**: SMTP (password reset)
- **Chat Storage**: Redis (temporary, no persistence)

---

## 1. Architecture Overview

**New Services:**
- **Auth Service**: Registration, login, logout, session validation, password reset
- **Chat Service**: Temporary chat storage per session (no persistence)
- **PostgreSQL**: Store users and password reset tokens only
- **Redis**: Store active session tokens and temporary chat messages

**Network Communication:**
- Frontend → Auth Service (HTTP: register, login, logout, password reset)
- Frontend → Chat Service (HTTP: send message, get current session chat)
- Chat Service → Auth Service (HTTP: validate session token)
- Chat Service → Retrieval Service (HTTP: search documents)
- Auth Service → PostgreSQL, Redis
- Chat Service → Redis only (no database)

## 2. Auth Service

**Responsibilities:**
- User registration with email and password
- Login credential verification
- Session token generation and storage
- Session validation for other services
- Logout and token invalidation
- Password reset token generation
- Password reset verification and update

**POST /auth/register**
- Accept email and password
- Validate email format
- Hash password using bcrypt
- Store user in database
- Return user_id

**POST /auth/login**
- Accept email and password
- Verify credentials against database
- Generate random session token
- Store token in Redis with user info and 24h TTL
- Return session_token and user_id

**POST /auth/logout**
- Accept session token from Authorization header
- Delete session token from Redis
- Delete chat history for user from Redis (chat:{user_id})
- Return success confirmation

**GET /auth/validate**
- Accept session token from Authorization header
- Check if token exists in Redis
- Return user_id and email if valid
- Used internally by Chat Service

**POST /auth/reset-request**
- Accept email address
- Generate unique reset token (UUID)
- Store token in password_resets table with 1-hour expiration
- Send reset link to email (token embedded in URL)
- Return success message

**POST /auth/reset-password**
- Accept reset token and new password
- Verify token exists, not expired, not used
- Hash new password
- Update user password
- Mark token as used
- Invalidate all existing sessions for that user in Redis
- Delete all chat history for that user from Redis
- Return success confirmation

**Implementation Details:**
- Password hashing: bcrypt with default rounds
- Session token: 32-byte random hex string
- Reset token: UUID v4
- Direct connections to PostgreSQL and Redis
- On logout or password reset, cleanup both session and chat data

## 3. Chat Service

**Responsibilities:**
- Store temporary chat messages in Redis per user session
- Retrieve current session chat history
- Orchestrate retrieval and LLM response generation
- Enforce user isolation
- No persistent storage - all data ephemeral

**GET /chat/history**
- Accept session token from Authorization header
- Call Auth Service to validate token and get user_id
- Retrieve chat:{user_id} from Redis
- Return messages array or empty array if no history
- Enables chat recovery on page refresh

**POST /chat/message**
- Accept session token and user message
- Call Auth Service to validate token and get user_id
- Retrieve existing chat history from Redis (chat:{user_id})
- Append user message to array
- Store updated array in Redis with 24h TTL
- Call Retrieval Service with message as query
- Receive document chunks with metadata
- Call OpenRouter API with system prompt, retrieved context, and user message
- Parse LLM response and extract citations
- Append assistant message to array
- Store updated array in Redis with 24h TTL
- Return assistant message with citations

**DELETE /chat/clear**
- Accept session token from Authorization header
- Call Auth Service to validate token and get user_id
- Delete chat:{user_id} from Redis
- Return success confirmation
- Allows user to clear current conversation and start fresh

**User Isolation Strategy:**
- Every endpoint validates session token with Auth Service first
- Redis keys namespaced by user_id (chat:{user_id})
- No user can access another user's temporary chat

**Chat Lifecycle:**
- Created on first message after login
- Exists only in Redis with 24h TTL
- Deleted on logout (Auth Service deletes it)
- Deleted on session expiration (Redis TTL)
- Deleted on password reset (Auth Service deletes it)
- Recovered on page refresh if session still valid

**Implementation Details:**
- No PostgreSQL connection needed
- Only Redis for temporary storage
- Makes HTTP calls to Auth Service for validation
- Makes HTTP calls to Retrieval Service for document search
- Makes HTTP calls to OpenRouter for LLM responses
- Message array stored as JSON in Redis

## 4. Session Management

**Session Creation (Login):**
- Generate cryptographically random token
- Store in Redis with key pattern session:{token}
- Store user_id and email as value
- Set 24-hour expiration (Redis TTL)
- No need to initialize empty chat (created on first message)

**Session Validation:**
- Extract token from Authorization header (Bearer format)
- Check if key exists in Redis
- Return associated user information
- Session automatically expires after 24 hours

**Session Termination (Logout):**
- Delete session:{token} from Redis
- Delete chat:{user_id} from Redis
- All user data removed from system (except user account)

**Password Reset Session Invalidation:**
- When user resets password, delete all session:{token} keys for that user_id
- Delete chat:{user_id} from Redis
- Forces re-login on all devices with fresh chat

**Page Refresh Behavior:**
- Frontend checks localStorage for session_token
- If token exists, includes it in Authorization header
- Calls Chat Service history endpoint
- Loads existing chat from Redis
- If session expired (24h), returns 401
- Frontend clears localStorage and redirects to login

## 5. Frontend Integration

**Pages Required:**
- Registration page (email, password inputs)
- Login page (email, password inputs)
- Password reset request page (email input)
- Password reset page (new password input, token from URL)
- Chat page (message input, history display, logout button, clear chat button)

**Registration Flow:**
- User fills registration form (email and password only)
- Call Auth Service register endpoint
- On success, redirect to login page

**Login Flow:**
- User enters credentials
- Call Auth Service login endpoint
- Store returned session_token in localStorage
- Redirect to chat page

**Chat Page Load Flow:**
- Check for session_token in localStorage
- If missing, redirect to login
- If present, call Chat Service history endpoint with token
- Load existing messages into UI state if any exist
- If 401 response, clear localStorage and redirect to login

**Chat Flow:**
- Include token in Authorization header for all requests
- Send message calls Chat Service message endpoint
- Display assistant response with citations
- Messages persist in Redis during session
- Survive page refresh as long as session valid

**Logout Flow:**
- Call Auth Service logout endpoint with token
- Clear localStorage
- Redirect to login page
- Chat history deleted on backend

**Clear Chat Flow:**
- Call Chat Service clear endpoint
- Clear messages from UI state
- Starts fresh conversation in same session

**Password Reset Flow:**
- User enters email on reset request page
- Call Auth Service reset-request endpoint
- User receives email with reset link
- User clicks link, opens reset password page with token in URL
- User enters new password
- Call Auth Service reset-password endpoint
- Redirect to login page

**Error Handling:**
- On 401 Unauthorized response (expired/invalid session)
- Clear localStorage and redirect to login
- Chat lost when session expires

**Token Management:**
- Store in localStorage with key "session_token"
- Include in every API request as Authorization: Bearer {token}
- React context for auth state (logged in/out)
- React state for chat messages (loaded from history endpoint)

## 6. Email Service Integration

**Implementation:**
- Use standard SMTP protocol in Auth Service
- Configure via environment variables
- Can work with any SMTP provider (Gmail, Outlook, etc.)
- Simple send email function for password reset

**Email Template:**
- Subject: Password Reset Request
- Body: Link to frontend reset page with token as query parameter
- Link format: https://frontend-url/reset-password?token={reset_token}
- Include expiration time (1 hour) in email text
- Plain text email sufficient for university project

**Configuration:**
- SMTP server host and credentials in environment variables
- No email verification needed on registration
- Only used for password reset functionality

## 7. Security Considerations

**Password Security:**
- Hash all passwords with bcrypt before storage
- Never store or log plaintext passwords
- No password complexity requirements (simple for university project)

**Session Security:**
- Tokens generated using cryptographically secure random function
- Tokens transmitted via HTTPS only in production
- Stored in Redis with automatic expiration
- Logout deletes token and chat immediately

**Password Reset Security:**
- Reset tokens are single-use (marked as used after consumption)
- Tokens expire after 1 hour
- Successful reset invalidates all existing sessions and chats
- Reset tokens are UUIDs (unguessable)

**API Security:**
- All endpoints validate session token except register, login, reset endpoints
- User isolation enforced at Redis key level (namespaced by user_id)
- Input validation for email format

**Database Security:**
- Use parameterized queries to prevent SQL injection
- Database connection credentials in environment variables
- Minimum required permissions for database user

**Chat Data Privacy:**
- No persistent chat storage
- Chats automatically deleted on logout
- Chats expire after 24h if forgotten
- No chat history recovery after logout

## 8. Data Isolation

**User Chat Isolation:**
- Redis keys namespaced per user: chat:{user_id}
- Session validation returns user_id used for key construction
- No cross-user data access possible
- Each user only sees their own temporary chat

**Implementation Pattern:**
- Extract token from request header
- Call Auth Service validate endpoint
- Receive user_id in response
- Use user_id to construct Redis key
- Return 401 if token invalid

## 9. Service Dependencies

**Auth Service depends on:**
- PostgreSQL (users, password_resets tables)
- Redis (session storage and chat cleanup)
- SMTP server (password reset emails)

**Chat Service depends on:**
- Redis (temporary chat storage)
- Auth Service (session validation)
- Retrieval Service (document search)
- OpenRouter API (LLM responses)

**Startup Order:**
- PostgreSQL and Redis first
- Auth Service second
- Retrieval Service (already exists)
- Chat Service last
- Frontend connects to Auth and Chat services

## 10. Environment Configuration

**Auth Service Environment Variables:**
- POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
- REDIS_HOST
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
- FRONTEND_URL (for password reset links)

**Chat Service Environment Variables:**
- REDIS_HOST
- AUTH_SERVICE_URL
- RETRIEVAL_SERVICE_URL
- OPENROUTER_API_KEY
