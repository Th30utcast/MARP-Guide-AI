"""
Retrieval Client Module
Handles communication with the Retrieval Service
"""
import logging
import httpx
from typing import List, Dict
import config

logger = logging.getLogger(__name__)

class RetrievalClient:
    """
    Client for the Retrieval Service
    Handles semantic search requests
    """

    def __init__(self, retrieval_url: str = None):
        """
        Initialize Retrieval client

        Args:
            retrieval_url: URL of the Retrieval Service (defaults to config)
        """
        self.retrieval_url = retrieval_url or config.RETRIEVAL_URL
        self.search_endpoint = f"{self.retrieval_url}/search"

        logger.info(f"✅ Retrieval client initialized | URL: {self.retrieval_url}")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant chunks using the Retrieval Service

        Args:
            query: User's question
            top_k: Number of chunks to retrieve

        Returns:
            List of chunks with metadata (text, title, page, url, score, etc.)

        Raises:
            Exception: If retrieval service fails
        """
        try:
            logger.info(f"🔍 Calling Retrieval Service | Query: {query[:50]}... | top_k: {top_k}")

            # Call retrieval service
            response = httpx.post(
                self.search_endpoint,
                json={"query": query, "top_k": top_k},
                timeout=30.0
            )
            response.raise_for_status()

            # Parse response
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
