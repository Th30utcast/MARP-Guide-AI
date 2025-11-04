"""
Chat Service - RAG-powered question answering
Implements the 4-step RAG pipeline: Retrieval → Augmentation → Generation → Citation
"""
import os, time, json, logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI setup
app = FastAPI(title="Chat Service", version="1.0.0")

# Schemas
class Citation(BaseModel):
    title: str
    page: int
    url: str

class ChatRequest(BaseModel):
    query: str = Field(..., description="User's question about MARP")
    top_k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve")

class ChatResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]

# Health check
@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "ChatService",
        "retrieval_url": config.RETRIEVAL_URL,
        "openrouter_configured": bool(config.OPENROUTER_API_KEY),
        "model": config.OPENROUTER_MODEL
    }

# Chat endpoint (placeholder - will be implemented)
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    RAG-powered chat endpoint
    Steps: 1. Retrieval → 2. Augmentation → 3. Generation → 4. Citation
    """
    # TODO: Implement 
    raise HTTPException(status_code=501, detail="Chat endpoint not yet implemented.")
