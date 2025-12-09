"""
Authentication Service - User registration, login, and session management
"""

import json
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import psycopg2
import redis
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Authentication Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    """Get PostgreSQL database connection."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "marp_user"),
        password=os.getenv("POSTGRES_PASSWORD", "marp_password"),
        database=os.getenv("POSTGRES_DB", "marp_db"),
    )


# Redis connection
def get_redis_client():
    """Get Redis client connection."""
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0,
        decode_responses=True,
    )


# Initialize database tables
def init_db():
    """Initialize database tables if they don't exist."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create password_resets table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                reset_token UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cur.close()
        conn.close()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")


# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database on service startup."""
    init_db()


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    message: str


class LoginResponse(BaseModel):
    session_token: str
    user_id: str
    email: str
    expires_at: str


class ValidateResponse(BaseModel):
    user_id: str
    email: str
    valid: bool


# Helper Functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)


# API Endpoints
@app.post("/auth/register", response_model=RegisterResponse)
def register(request: RegisterRequest):
    """Register a new user."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if user already exists
        cur.execute("SELECT user_id FROM users WHERE email = %s", (request.email,))
        if cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password and create user
        password_hash = hash_password(request.password)
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING user_id",
            (request.email, password_hash),
        )
        user_id = str(cur.fetchone()[0])
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"✅ User registered: {request.email}")
        return RegisterResponse(
            user_id=user_id, email=request.email, message="Registration successful"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """Login and create session."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get user from database
        cur.execute(
            "SELECT user_id, password_hash FROM users WHERE email = %s", (request.email,)
        )
        result = cur.fetchone()
        
        if not result:
            cur.close()
            conn.close()
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user_id, password_hash = result
        
        # Verify password
        if not verify_password(request.password, password_hash):
            cur.close()
            conn.close()
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Generate session token
        session_token = generate_session_token()
        
        # Store session in Redis (24 hour TTL)
        redis_client = get_redis_client()
        session_data = {"user_id": str(user_id), "email": request.email}
        redis_client.setex(
            f"session:{session_token}",
            86400,  # 24 hours
            json.dumps(session_data),
        )
        
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        
        cur.close()
        conn.close()
        
        logger.info(f"✅ User logged in: {request.email}")
        return LoginResponse(
            session_token=session_token,
            user_id=str(user_id),
            email=request.email,
            expires_at=expires_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@app.post("/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    """Logout and invalidate session."""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        session_token = authorization.replace("Bearer ", "")
        redis_client = get_redis_client()
        
        # Get session data to find user_id
        session_data = redis_client.get(f"session:{session_token}")
        if session_data:
            # Delete session
            redis_client.delete(f"session:{session_token}")
            
            # Delete chat history if exists
            # Note: We'll need user_id from session, but for now just delete session
            logger.info(f"✅ Session invalidated: {session_token[:10]}...")
        
        return {"message": "Logout successful"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")


@app.get("/auth/validate", response_model=ValidateResponse)
def validate_session(authorization: Optional[str] = Header(None)):
    """Validate session token (internal endpoint for other services)."""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        session_token = authorization.replace("Bearer ", "")
        redis_client = get_redis_client()
        
        session_data = redis_client.get(f"session:{session_token}")
        if not session_data:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Parse session data (stored as JSON)
        session_dict = json.loads(session_data)
        
        return ValidateResponse(
            user_id=session_dict["user_id"],
            email=session_dict["email"],
            valid=True,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=401, detail="Session validation failed")


@app.get("/health")
def health():
    """Health check endpoint."""
    try:
        # Test database connection
        conn = get_db_connection()
        conn.close()
        
        # Test Redis connection
        redis_client = get_redis_client()
        redis_client.ping()
        
        return {"status": "ok", "service": "auth-service"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

