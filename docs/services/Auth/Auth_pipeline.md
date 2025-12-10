# Authentication Service Pipeline

Overview of user registration, login, session management, and validation flows.

## Registration Flow

```mermaid
sequenceDiagram
  participant USER as User/Client
  participant AUTH as Auth Service<br/>(FastAPI)
  participant PG as PostgreSQL

  USER->>AUTH: POST /auth/register<br/>{email, password}

  Note over AUTH: Validate email format<br/>Validate password length (min 8)

  AUTH->>PG: Check if email exists
  PG-->>AUTH: Result

  alt Email already exists
    AUTH-->>USER: 400 Bad Request<br/>"Email already registered"
  else Email available
    AUTH->>AUTH: Hash password with bcrypt

    AUTH->>PG: INSERT INTO users<br/>(email, password_hash)
    PG-->>AUTH: {user_id}

    AUTH-->>USER: 201 Created<br/>{user_id, email, message}
  end
```

## Login Flow

```mermaid
sequenceDiagram
  participant USER as User/Client
  participant AUTH as Auth Service<br/>(FastAPI)
  participant PG as PostgreSQL
  participant REDIS as Redis

  USER->>AUTH: POST /auth/login<br/>{email, password}

  AUTH->>PG: SELECT user_id, password_hash, is_admin<br/>WHERE email = ?
  PG-->>AUTH: User record or null

  alt User not found
    AUTH-->>USER: 401 Unauthorized<br/>"Invalid email or password"
  else User found
    AUTH->>AUTH: Verify password with bcrypt

    alt Password incorrect
      AUTH-->>USER: 401 Unauthorized<br/>"Invalid email or password"
    else Password correct
      AUTH->>AUTH: Generate session token<br/>(secrets.token_urlsafe(32))

      AUTH->>REDIS: SETEX session:{token}<br/>{user_id, email, is_admin}<br/>TTL: 24 hours

      AUTH-->>USER: 200 OK<br/>{session_token, user_id,<br/>email, is_admin, expires_at}
    end
  end
```

## Session Validation Flow

```mermaid
sequenceDiagram
  participant SERVICE as Other Service<br/>(Chat/Analytics)
  participant AUTH as Auth Service
  participant REDIS as Redis

  SERVICE->>AUTH: GET /auth/validate<br/>Bearer: {session_token}

  AUTH->>REDIS: GET session:{token}
  REDIS-->>AUTH: Session data or null

  alt Session not found or expired
    AUTH-->>SERVICE: 401 Unauthorized<br/>"Invalid or expired session"
  else Session valid
    AUTH->>AUTH: Parse session data<br/>{user_id, email, is_admin}

    AUTH-->>SERVICE: 200 OK<br/>{user_id, email, is_admin, valid: true}
  end
```

## Logout Flow

```mermaid
sequenceDiagram
  participant USER as User/Client
  participant AUTH as Auth Service<br/>(FastAPI)
  participant REDIS as Redis

  USER->>AUTH: POST /auth/logout<br/>Bearer: {session_token}

  AUTH->>REDIS: GET session:{token}
  REDIS-->>AUTH: Session data or null

  alt Session exists
    AUTH->>REDIS: DELETE session:{token}
    AUTH-->>USER: 200 OK<br/>{"message": "Logout successful"}
  else Session not found
    AUTH-->>USER: 200 OK<br/>{"message": "Logout successful"}
  end

  Note over REDIS: Session deleted,<br/>token now invalid
```

## Model Preference Flow

```mermaid
sequenceDiagram
  participant USER as User/Client
  participant AUTH as Auth Service
  participant REDIS as Redis
  participant PG as PostgreSQL

  Note over USER: Save preferred model

  USER->>AUTH: POST /auth/preferences/model<br/>Bearer: {token}<br/>?model_id=google/gemma-3n-e2b-it:free

  AUTH->>REDIS: Validate session:{token}
  REDIS-->>AUTH: {user_id, email}

  AUTH->>PG: INSERT INTO user_preferences<br/>(user_id, selected_model)<br/>ON CONFLICT UPDATE
  PG-->>AUTH: Success

  AUTH-->>USER: 200 OK<br/>{"message": "Model preference saved",<br/>"model_id": "..."}

  Note over USER: Retrieve preferred model

  USER->>AUTH: GET /auth/preferences/model<br/>Bearer: {token}

  AUTH->>REDIS: Validate session:{token}
  REDIS-->>AUTH: {user_id, email}

  AUTH->>PG: SELECT selected_model<br/>WHERE user_id = ?
  PG-->>AUTH: Model ID or null

  AUTH-->>USER: 200 OK<br/>{"model_id": "..." or null}
```

## Registration Request

```json
{
  "email": "student@example.com",
  "password": "securepassword123"
}
```

## Registration Response

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "message": "Registration successful"
}
```

## Login Request

```json
{
  "email": "student@example.com",
  "password": "securepassword123"
}
```

## Login Response

```json
{
  "session_token": "xY9Kp2mN5vT8wQ3rL6zA1bC4eD7fG0hJ",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "is_admin": false,
  "expires_at": "2025-12-11T10:30:00Z"
}
```

## Validation Response

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "is_admin": false,
  "valid": true
}
```

## Security Features

### Password Hashing
- Algorithm: bcrypt
- Salt: Automatically generated per password
- Password never stored in plaintext
- Password never logged

### Session Tokens
- Generation: `secrets.token_urlsafe(32)` (cryptographically secure)
- Length: 43 characters (base64url-encoded)
- Storage: Redis with automatic expiration
- TTL: 24 hours (86400 seconds)

### Session Data Structure

**Redis Key:** `session:{token}`

**Redis Value (JSON):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "is_admin": false
}
```

**TTL:** 86400 seconds (24 hours)

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### User Preferences Table

```sql
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    selected_model VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Admin User

**Default Admin Account:**
- Email: `admin@example.com`
- Password: `admin`
- Created automatically on service startup
- `is_admin` flag set to `true`

**Admin Capabilities:**
- View global analytics (all users)
- Regular users can only view their own analytics

## Validation Patterns

### Email Validation
- Pydantic `EmailStr` type validation
- Must contain `@` symbol
- Must have domain extension after `@`

### Password Validation
- Minimum length: 8 characters
- Enforced via Pydantic `Field(min_length=8)`
- Additional whitespace check

### Session Token Validation
- Must be present in Authorization header
- Format: `Bearer <token>`
- Must exist in Redis
- Must not be expired

## Error Responses

### 400 Bad Request
- Invalid email format
- Password too short
- Email already registered
- Missing user_id parameter (non-admin users)

### 401 Unauthorized
- Invalid email or password
- Missing authorization header
- Invalid or expired session
- Invalid session format

### 500 Internal Server Error
- Database connection failure
- Redis connection failure
- Unexpected errors

## Technologies

- **Framework**: FastAPI + Pydantic
- **Password Hashing**: bcrypt
- **Session Storage**: Redis (with TTL)
- **User Storage**: PostgreSQL
- **Token Generation**: Python secrets module
- **Validation**: Pydantic models
