"""
Chat Service - RAG-powered question answering
Implements the 4-step RAG pipeline: Retrieval → Augmentation → Generation → Citation
"""
import os, time, json, logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import config
from retrieval_client import RetrievalClient
from openrouter_client import OpenRouterClient
from prompt_templates import create_rag_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI setup
app = FastAPI(title="Chat Service", version="1.0.0")

# Initialize clients
retrieval_client = RetrievalClient()
openrouter_client = OpenRouterClient()

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

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    RAG-powered chat endpoint
    Steps: 1. Retrieval → 2. Augmentation → 3. Generation → 4. Citation
    """
    start_time = time.time()
    
    try:
        # Step 1: Retrieval - Get relevant chunks
        logger.info(f"🔍 Step 1: Retrieving chunks for query: {req.query[:50]}...")
        chunks = retrieval_client.search(req.query, req.top_k)
        
        if not chunks:
            logger.warning("⚠️ No chunks retrieved for query")
            return ChatResponse(
                query=req.query,
                answer="I couldn't find any relevant information in the MARP documents to answer your question. Please try rephrasing your query.",
                citations=[]
            )
        
        logger.info(f"✅ Retrieved {len(chunks)} chunks")
        
        # Step 2: Augmentation - Build RAG prompt
        logger.info("📝 Step 2: Building RAG prompt")
        prompt = create_rag_prompt(req.query, chunks)
        
        # Step 3: Generation - Generate answer using LLM
        logger.info("🤖 Step 3: Generating answer with LLM")
        answer = openrouter_client.generate_answer(prompt)
        
        # Step 4: Citation - Extract citations from chunks
        logger.info("📚 Step 4: Extracting citations")
        citations = []
        seen_citations = set()
        
        for chunk in chunks:
            citation_key = (chunk.get("title", ""), chunk.get("page", 0))
            if citation_key not in seen_citations and citation_key[0] and citation_key[1]:
                citations.append(Citation(
                    title=chunk.get("title", "Unknown"),
                    page=chunk.get("page", 0),
                    url=chunk.get("url", "")
                ))
                seen_citations.add(citation_key)
        
        latency = round((time.time() - start_time) * 1000, 2)
        logger.info(f"✅ Chat completed in {latency}ms | Citations: {len(citations)}")
        
        return ChatResponse(
            query=req.query,
            answer=answer,
            citations=citations
        )
        
    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )
