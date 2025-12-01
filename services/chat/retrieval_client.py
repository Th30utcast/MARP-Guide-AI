"""
RETRIEVAL CLIENT

Client for communicating with the Retrieval Service. Sends search queries and gets
back relevant document chunks from the vector database for RAG.

Purpose: Fetches context (relevant text snippets) to include in the LLM prompt.
"""

import logging
from typing import Dict, List

import config
import httpx

logger = logging.getLogger(__name__)


class RetrievalClient:
    def __init__(self, retrieval_url: str = None):
        # Load Retrieval Service URL from config or use provided value
        self.retrieval_url = retrieval_url or config.RETRIEVAL_URL
        self.search_endpoint = f"{self.retrieval_url}/search"

        logger.info(f"✅ Retrieval client initialized | URL: {self.retrieval_url}")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        # Search for relevant chunks: sends query, gets back top_k results with metadata
        try:
            logger.info(f"🔍 Calling Retrieval Service | Query: {query[:50]}... | top_k: {top_k}")

            # Send POST request to Retrieval Service
            response = httpx.post(self.search_endpoint, json={"query": query, "top_k": top_k}, timeout=30.0)
            response.raise_for_status()  # Raise error if HTTP request failed

            # Extract results from response
            data = response.json()
            chunks = data.get("results", [])

            logger.info(f"✅ Retrieved {len(chunks)} chunks from Retrieval Service")

            return chunks

        except httpx.HTTPError as e:
            logger.error(f"❌ Retrieval Service HTTP error: {e}")
            raise Exception(f"Failed to retrieve chunks: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Retrieval Service error: {e}")
            raise Exception(f"Failed to retrieve chunks: {str(e)}")
