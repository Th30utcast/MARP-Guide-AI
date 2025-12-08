# Authentication Testing Guide

## Quick Start

### 1. Start All Services

```bash
docker compose up --build
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Auth Service (port 8004)
- All other existing services

### 2. Access the Application

**Web UI (Main Application):**
- URL: http://localhost:8080
- This is where you'll test the login/registration UI

**Auth Service API (Direct Testing):**
- URL: http://localhost:8004
- Interactive Docs: http://localhost:8004/docs
- Health Check: http://localhost:8004/health

## Testing URLs

### Web Application
- **Main App**: http://localhost:8080
- **Login Page**: http://localhost:8080 (shown when not authenticated)
- **Registration Page**: http://localhost:8080 (click "Sign up" link)

### API Endpoints (Direct Testing)
- **Auth Service Docs**: http://localhost:8004/docs
- **Health Check**: http://localhost:8004/health
- **Register**: POST http://localhost:8004/auth/register
- **Login**: POST http://localhost:8004/auth/login
- **Logout**: POST http://localhost:8004/auth/logout
- **Validate**: GET http://localhost:8004/auth/validate

## Manual Testing Steps

### Test 1: Registration Flow

1. **Open the application**: http://localhost:8080
2. **You should see the Login page**
3. **Click "Sign up"** link at the bottom
4. **Fill in registration form**:
   - Email: `test@lancaster.ac.uk` (or any valid email)
   - Password: `testpassword123` (must be at least 8 characters)
   - Confirm Password: `testpassword123`
5. **Click "Create Account"**
6. **Expected**: Success message appears, then redirected to login page
7. **Try registering with the same email again**
8. **Expected**: Error message "Email already registered"

### Test 2: Login Flow

1. **On the login page**, enter credentials:
   - Email: `test@lancaster.ac.uk`
   - Password: `testpassword123`
2. **Click "Sign In"**
3. **Expected**: 
   - Redirected to main chat interface
   - Your email appears in the header
   - "Logout" button visible in header
4. **Try wrong password**
5. **Expected**: Error message "Invalid email or password"

### Test 3: Session Persistence

1. **After logging in**, refresh the page (F5)
2. **Expected**: Still logged in, session persists
3. **Close browser tab and reopen** http://localhost:8080
4. **Expected**: Still logged in (token stored in localStorage)

### Test 4: Logout Flow

1. **While logged in**, click "Logout" button in header
2. **Expected**: 
   - Redirected to login page
   - Session token removed
   - Cannot access chat without logging in again

### Test 5: Form Validation

**Registration Form:**
- Try submitting with empty fields → Error shown
- Try password less than 8 characters → Error shown
- Try mismatched passwords → Error shown
- Try invalid email format → Browser validation

**Login Form:**
- Try submitting with empty fields → Error shown
- Try invalid credentials → Error shown

### Test 6: API Testing (Using Swagger UI)

1. **Open**: http://localhost:8004/docs
2. **Test Registration**:
   - Click on `POST /auth/register`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "email": "api-test@lancaster.ac.uk",
       "password": "testpass123"
     }
     ```
   - Click "Execute"
   - **Expected**: 200 response with user_id and email

3. **Test Login**:
   - Click on `POST /auth/login`
   - Click "Try it out"
   - Enter same credentials
   - Click "Execute"
   - **Expected**: 200 response with session_token, user_id, email, expires_at

4. **Test Validate**:
   - Copy the `session_token` from login response
   - Click on `GET /auth/validate`
   - Click "Try it out"
   - Click "Authorize" button at top
   - Enter: `Bearer <your_session_token>`
   - Click "Authorize" then "Close"
   - Click "Execute"
   - **Expected**: 200 response with user_id, email, valid: true

5. **Test Logout**:
   - Use same authorization token
   - Click on `POST /auth/logout`
   - Click "Execute"
   - **Expected**: 200 response with "Logout successful"
   - Try validating again → Should fail (401)

### Test 7: Error Scenarios

1. **Duplicate Registration**:
   - Register same email twice
   - **Expected**: Error "Email already registered"

2. **Invalid Login**:
   - Try login with wrong password
   - **Expected**: Error "Invalid email or password"

3. **Expired Session**:
   - Login and get token
   - Wait 24 hours (or manually delete from Redis)
   - Try to use token
   - **Expected**: 401 Unauthorized

## Using cURL for Testing

### Register
```bash
curl -X POST http://localhost:8004/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "curl-test@lancaster.ac.uk", "password": "testpass123"}'
```

### Login
```bash
curl -X POST http://localhost:8004/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "curl-test@lancaster.ac.uk", "password": "testpass123"}'
```

### Validate (replace TOKEN with actual token)
```bash
curl -X GET http://localhost:8004/auth/validate \
  -H "Authorization: Bearer TOKEN"
```

### Logout (replace TOKEN with actual token)
```bash
curl -X POST http://localhost:8004/auth/logout \
  -H "Authorization: Bearer TOKEN"
```

## Database Verification

### Check Users Table
```bash
docker compose exec postgres psql -U marp_user -d marp_db -c "SELECT user_id, email, created_at FROM users;"
```

### Check Redis Sessions
```bash
docker compose exec redis redis-cli KEYS "session:*"
```

### View Session Data
```bash
docker compose exec redis redis-cli GET "session:YOUR_TOKEN_HERE"
```

## Troubleshooting

### Services Not Starting
```bash
# Check service status
docker compose ps

# Check logs
docker compose logs auth
docker compose logs postgres
docker compose logs redis
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
docker compose exec postgres psql -U marp_user -d marp_db -c "SELECT 1;"

# Check if tables exist
docker compose exec postgres psql -U marp_user -d marp_db -c "\dt"
```

### Redis Connection Issues
```bash
# Test Redis connection
docker compose exec redis redis-cli PING

# Should return: PONG
```

### UI Not Loading
- Check if UI service is running: `docker compose ps ui`
- Check UI logs: `docker compose logs ui`
- Verify nginx config: Check `services/ui/nginx.conf`
- Try accessing directly: http://localhost:8004/health (auth service)

### CORS Issues
- Auth service has CORS enabled for all origins (development)
- In production, restrict to specific domains

## Expected Behavior Summary

✅ **Registration**:
- Creates user in PostgreSQL
- Returns user_id and email
- Password is hashed (bcrypt)
- Email must be unique

✅ **Login**:
- Validates credentials
- Creates session token
- Stores session in Redis (24h TTL)
- Returns token, user_id, email, expires_at

✅ **Session Validation**:
- Checks Redis for session token
- Returns user info if valid
- Returns 401 if invalid/expired

✅ **Logout**:
- Deletes session from Redis
- Returns success message

✅ **UI**:
- Shows login page when not authenticated
- Shows chat interface when authenticated
- Persists session in localStorage
- Logout button in header
- User email displayed in header

## Security Notes

- Passwords are hashed with bcrypt (never stored in plain text)
- Session tokens are cryptographically random (secrets.token_urlsafe)
- Sessions expire after 24 hours
- No password reset implemented yet (future feature)
- CORS is open for development (restrict in production)

