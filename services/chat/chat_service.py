# Module docstring describing a RAG-powered chat service with a 4-step pipeline.
"""
Chat Service - RAG-powered question answering
Implements the 4-step RAG pipeline: Retrieval → Augmentation → Generation → Citation
"""

# Imports standard libraries and project modules: FastAPI for the web API, Pydantic for data validation, 
# logging, and custom clients for retrieval and LLM calls.
import os, time, json, logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import config
from retrieval_client import RetrievalClient
from openrouter_client import OpenRouterClient
from prompt_templates import create_rag_prompt

# Sets logging to INFO and creates a logger for this module.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI setup: Creates the FastAPI application instance with a title and version.
app = FastAPI(title="Chat Service", version="1.0.0")

# Initialize clients: Creates instances of RetrievalClient and OpenRouterClient for later use.
retrieval_client = RetrievalClient()
openrouter_client = OpenRouterClient()

# Schemas: 

#Defines a Pydantic model for citations with title, page, and URL.
class Citation(BaseModel):
    title: str
    page: int
    url: str

#Defines the request model: required query string and optional top_k (1-20, default 5).
class ChatRequest(BaseModel):
    query: str = Field(..., description="User's question about MARP")
    top_k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve")

#Defines the response model: query, answer, and a list of citations.
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

# Chat endpoint: POST endpoint that accepts ChatRequest, records start time, and begins the RAG pipeline.
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    RAG-powered chat endpoint
    Steps: 1. Retrieval → 2. Augmentation → 3. Generation → 4. Citation
    """
    start_time = time.time()
    
    try:
        # (Step 1 - Retrieval): Logs and searches for relevant document chunks using the retrieval client.
        logger.info(f"🔍 Step 1: Retrieving chunks for query: {req.query[:50]}...")
        chunks = retrieval_client.search(req.query, req.top_k)
        
        # (No chunks handling): If no chunks are found, returns an error message with empty citations.
        if not chunks:
            logger.warning("⚠️ No chunks retrieved for query")
            return ChatResponse(
                query=req.query,
                answer="I couldn't find any relevant information in the MARP documents to answer your question. Please try rephrasing your query.",
                citations=[]
            )
        
        logger.info(f"✅ Retrieved {len(chunks)} chunks")
        
        # (Step 2 - Augmentation): Builds a RAG prompt by combining the user query with retrieved chunks.
        logger.info("📝 Step 2: Building RAG prompt")
        prompt = create_rag_prompt(req.query, chunks)
        
        # (Step 3 - Generation): Sends the prompt to the LLM via OpenRouter to generate the answer.
        logger.info("🤖 Step 3: Generating answer with LLM")
        answer = openrouter_client.generate_answer(prompt)
        
        # (Step 4 - Citation extraction): Extracts unique citations from chunks, 
        # using a set to avoid duplicates, and only includes citations with valid title and page numbers.
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
        
        # (Latency logging): Calculates and logs how long the request took in milliseconds.
        latency = round((time.time() - start_time) * 1000, 2)
        logger.info(f"✅ Chat completed in {latency}ms | Citations: {len(citations)}")
        
        # (Success response): Returns the ChatResponse with the query, generated answer, and citations.
        return ChatResponse(
            query=req.query,
            answer=answer,
            citations=citations
        )
        
        #(Error handling): Catches exceptions, logs errors, and returns a 500 HTTP error with details.
    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )
