# Service Name: Authentication Service

## Responsibility

Manages user registration, login, session management, and user preferences for the MARP-Guide AI system.

## Data Owned

- User accounts (stored in PostgreSQL: `users` table)
- Password reset tokens (stored in PostgreSQL: `password_resets` table)
- User model preferences (stored in PostgreSQL: `user_preferences` table)
- Active sessions (stored in Redis with 24-hour TTL)

## API Endpoints

- [POST] /auth/register - Register new user account
- [POST] /auth/login - Authenticate user and create session
- [POST] /auth/logout - Invalidate session token
- [GET] /auth/validate - Validate session token (internal use)
- [POST] /auth/preferences/model - Save user's preferred LLM model
- [GET] /auth/preferences/model - Retrieve user's preferred LLM model
- [GET] /health - Health check endpoint

## Authentication Service API

### POST /auth/register

Register a new user account

**Request Body:**

```json
{
  "email": "student@example.com",
  "password": "securepassword123"
}
```

**Validation:**
- Email must be valid format
- Password minimum 8 characters

**Response: 201 Created**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "message": "Registration successful"
}
```

**Errors:**
- 400 Bad Request - Invalid email format or password too short
- 400 Bad Request - Email already registered
- 500 Internal Server Error - Registration failed

---

### POST /auth/login

Authenticate user and create session

**Request Body:**

```json
{
  "email": "student@example.com",
  "password": "securepassword123"
}
```

**Response: 200 OK**

```json
{
  "session_token": "xY9Kp2mN5vT8wQ3rL6zA1bC4eD7fG0hJ",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "is_admin": false,
  "expires_at": "2025-12-11T10:30:00Z"
}
```

**Errors:**
- 401 Unauthorized - Invalid email or password
- 500 Internal Server Error - Login failed

**Session Details:**
- Token stored in Redis with 24-hour TTL
- Token is cryptographically secure random string (32 bytes)
- Session automatically expires after 24 hours

---

### POST /auth/logout

Invalidate session token

**Headers:**
```
Authorization: Bearer <session_token>
```

**Response: 200 OK**

```json
{
  "message": "Logout successful"
}
```

**Errors:**
- 401 Unauthorized - Missing or invalid authorization header
- 500 Internal Server Error - Logout failed

**Behavior:**
- Deletes session token from Redis
- Session immediately invalidated

---

### GET /auth/validate

Validate session token and retrieve user information (used internally by other services)

**Headers:**
```
Authorization: Bearer <session_token>
```

**Response: 200 OK**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "is_admin": false,
  "valid": true
}
```

**Errors:**
- 401 Unauthorized - Invalid or expired session
- 401 Unauthorized - Missing authorization header

**Usage:**
- Called by Chat Service and Analytics Service to validate user sessions
- Returns user metadata for request authorization

---

### POST /auth/preferences/model

Save user's preferred LLM model

**Headers:**
```
Authorization: Bearer <session_token>
```

**Query Parameters:**
- `model_id` (required) - Model identifier (e.g., "google/gemma-3n-e2b-it:free")

**Response: 200 OK**

```json
{
  "message": "Model preference saved",
  "model_id": "google/gemma-3n-e2b-it:free"
}
```

**Errors:**
- 401 Unauthorized - Invalid or expired session
- 500 Internal Server Error - Failed to save preference

**Behavior:**
- Upserts preference in `user_preferences` table
- Persists across sessions

---

### GET /auth/preferences/model

Retrieve user's preferred LLM model

**Headers:**
```
Authorization: Bearer <session_token>
```

**Response: 200 OK (preference exists)**

```json
{
  "model_id": "google/gemma-3n-e2b-it:free"
}
```

**Response: 200 OK (no preference set)**

```json
{
  "model_id": null
}
```

**Errors:**
- 401 Unauthorized - Invalid or expired session
- 500 Internal Server Error - Failed to retrieve preference

---

### GET /health

Health check endpoint

**Response: 200 OK**

```json
{
  "status": "ok",
  "service": "auth-service"
}
```

**Response: 503 Service Unavailable**

Service unhealthy (database or Redis connection failed)

**Checks:**
- PostgreSQL connectivity
- Redis connectivity

---

## Database Schema

### PostgreSQL Tables

**users:**
```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

### Redis Storage

**Sessions:**
```
Key: session:{token}
Value: JSON {"user_id": "...", "email": "...", "is_admin": false}
TTL: 24 hours (86400 seconds)
```

---

## Technical Details

**Password Security:**
- Hashing algorithm: bcrypt
- Password hashed before storage
- Plaintext passwords never stored or logged

**Session Management:**
- Token generation: `secrets.token_urlsafe(32)` (cryptographically secure)
- Storage: Redis with automatic expiration
- Validation: Check token exists in Redis
- Invalidation: Delete from Redis on logout

**Admin User:**
- Default admin created on startup
- Email: `admin@example.com`
- Password: `admin`
- Can access global analytics data

**CORS Configuration:**
- Allows all origins (development mode)
- Should be restricted in production

**Dependencies:**
- PostgreSQL for persistent user data
- Redis for session storage
- bcrypt for password hashing
- psycopg2 for PostgreSQL connection
- FastAPI for REST API framework

---

## Service Integration

**Called By:**
- Chat Service (session validation via `/auth/validate`)
- Analytics Service (admin check via `/auth/validate`)
- Web UI (all endpoints)

**Depends On:**
- PostgreSQL (user storage)
- Redis (session storage)

**Network Communication:**
- HTTP REST API on port 8004
- No message queue integration
