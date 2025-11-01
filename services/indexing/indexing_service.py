"""
Indexing Service - Chunks documents and generates embeddings for vector search

This service consumes DocumentExtracted events, performs semantic chunking,
generates embeddings, and stores vectors in Qdrant for retrieval.
"""

import os
import json
import logging
import time
from typing import List, Dict, Any
from datetime import datetime

import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from common.events import create_chunks_indexed_event, create_indexing_failed_event
from common.mq import RabbitMQEventBroker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def chunk_document(text: str, metadata: dict, max_tokens: int = 400) -> List[Dict[str, Any]]:
    """
    Semantic paragraph chunking following professor's Slide 8 algorithm.

    This strategy preserves MARP regulation structure by respecting paragraph
    boundaries. Regulations are organized as paragraphs, so this maintains
    semantic meaning and regulation boundaries.

    Args:
        text: Full document text to chunk
        metadata: Document metadata (title, page, url) to attach to each chunk
        max_tokens: Maximum tokens per chunk (default 400, range 200-500)

    Returns:
        List of chunks, each with text and metadata
    """
    # Split document into paragraphs
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # Skip empty paragraphs
        if not para.strip():
            continue

        # Estimate token count (rough approximation: 1 token ≈ 4 characters)
        para_tokens = len(para) // 4
        current_tokens = len(current_chunk) // 4

        # If adding this paragraph exceeds limit and we have content, save current chunk
        if current_tokens + para_tokens > max_tokens and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": metadata.copy()
            })
            current_chunk = para
        else:
            # Add paragraph to current chunk
            current_chunk += "\n\n" + para if current_chunk else para

    # Don't forget the last chunk!
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "metadata": metadata.copy()
        })

    logger.info(f"Chunked document into {len(chunks)} semantic chunks")
    return chunks


class IndexingService:
    """
    Indexing Service - Handles document chunking, embedding, and vector storage.

    Responsibilities:
    - Chunk documents using semantic paragraph-based strategy
    - Generate embeddings using sentence-transformers
    - Store vectors with metadata in Qdrant
    - Publish ChunksIndexed events
    """

    def __init__(self):
        """Initialize the indexing service with embedding model and Qdrant client."""
        logger.info("Initializing Indexing Service...")

        # RabbitMQ configuration
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        self.rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")

        # Storage configuration
        self.storage_path = os.getenv("STORAGE_PATH", "/app/storage/extracted")

        # Initialize event broker
        self.event_broker = RabbitMQEventBroker(
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            username=self.rabbitmq_user,
            password=self.rabbitmq_password
        )

        # Load embedding model (sentence-transformers/all-MiniLM-L6-v2)
        # This model provides 384-dimensional embeddings
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded successfully")

        # Initialize Qdrant client with retry logic
        qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        logger.info(f"Connecting to Qdrant at {qdrant_host}:{qdrant_port}")

        # Retry connection to Qdrant (it may not be ready immediately)
        max_retries = 10
        retry_delay = 2  # seconds
        for attempt in range(max_retries):
            try:
                self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
                # Test connection by getting collections
                self.qdrant.get_collections()
                logger.info("Successfully connected to Qdrant")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Qdrant not ready (attempt {attempt + 1}/{max_retries}): {e}")
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to connect to Qdrant after {max_retries} attempts")
                    raise

        # Collection configuration
        self.collection_name = "marp-documents"
        self.vector_size = 384  # all-MiniLM-L6-v2 dimensions

        # Setup Qdrant collection
        self._setup_qdrant_collection()

        logger.info("Indexing Service initialized successfully")

    def _setup_qdrant_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        try:
            # Try to create collection (simpler approach)
            logger.info(f"Creating collection '{self.collection_name}'")
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Collection '{self.collection_name}' created successfully")
        except Exception as e:
            # Collection likely already exists, which is fine
            if "already exists" in str(e):
                logger.info(f"Collection '{self.collection_name}' already exists")
            else:
                # Re-raise if it's a different error
                logger.warning(f"Qdrant collection setup warning: {str(e)}")
                logger.info(f"Continuing anyway - collection should be usable")

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of text chunks.

        Args:
            texts: List of text strings to embed

        Returns:
            Numpy array of embeddings (shape: num_texts x 384)
        """
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=False)
        logger.info(f"Generated embeddings with shape {embeddings.shape}")
        return embeddings

    def store_chunks_in_qdrant(self, chunks: List[Dict[str, Any]],
                               embeddings: np.ndarray, document_id: str):
        """
        Store chunks with their embeddings in Qdrant.

        Args:
            chunks: List of chunks with text and metadata
            embeddings: Numpy array of embeddings
            document_id: Unique document identifier
        """
        logger.info(f"Storing {len(chunks)} chunks in Qdrant for document {document_id}")

        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Create unique point ID
            point_id_str = f"{document_id}_{idx}"
            point_id = hash(point_id_str) % (2**63)  # Ensure positive 64-bit integer

            # Create point with vector and payload
            points.append(PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload={
                    "text": chunk["text"],
                    "document_id": document_id,
                    "chunk_index": idx,
                    "title": chunk["metadata"].get("title", ""),
                    "page": chunk["metadata"].get("page", 0),
                    "url": chunk["metadata"].get("url", "")
                }
            ))

        # Upsert points to Qdrant
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Successfully stored {len(points)} points in Qdrant")

    def _read_pages(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Read pages from storage/extracted/{documentId}/pages.jsonl

        Args:
            document_id: Document identifier

        Returns:
            List of page dictionaries with page number and text
        """
        pages_file = os.path.join(self.storage_path, document_id, "pages.jsonl")
        logger.info(f"Reading pages from {pages_file}")

        pages = []
        with open(pages_file, 'r', encoding='utf-8') as f:
            for line in f:
                page_data = json.loads(line.strip())
                pages.append(page_data)

        logger.info(f"Read {len(pages)} pages from {pages_file}")
        return pages

    def _save_chunks(self, document_id: str, chunks: List[Dict[str, Any]]):
        """
        Save chunks to storage/extracted/{documentId}/chunks.json for debugging.

        Args:
            document_id: Document identifier
            chunks: List of chunks to save
        """
        chunks_file = os.path.join(self.storage_path, document_id, "chunks.json")
        logger.info(f"Saving {len(chunks)} chunks to {chunks_file}")

        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        logger.info(f"Chunks saved to {chunks_file}")

    def _save_event(self, document_id: str, event: Dict[str, Any], filename: str):
        """
        Save event to storage (event sourcing pattern).

        Args:
            document_id: Document identifier
            event: Event dictionary
            filename: Output filename (e.g., "indexed.json")
        """
        event_file = os.path.join(self.storage_path, document_id, filename)
        logger.info(f"Saving event to {event_file}")

        with open(event_file, 'w', encoding='utf-8') as f:
            json.dump(event, f, indent=2, ensure_ascii=False)

        logger.info(f"Event saved to {event_file}")

    def handle_document_extracted_event(self, event: Dict[str, Any]):
        """
        Handle DocumentExtracted event - chunk, embed, and index the document.

        Args:
            event: DocumentExtracted event dictionary
        """
        try:
            document_id = event["payload"]["documentId"]
            correlation_id = event["correlationId"]

            logger.info(f"Processing DocumentExtracted event for document {document_id}")

            # Read pages from storage
            pages = self._read_pages(document_id)

            # Get document metadata from event
            doc_metadata = event["payload"]["metadata"]
            doc_title = doc_metadata.get("title", "Unknown")
            doc_url = doc_metadata.get("url", "")

            # Chunk each page with metadata preservation
            all_chunks = []
            for page in pages:
                page_num = page.get("page", 0)
                page_text = page.get("text", "")

                # Create metadata for this page's chunks
                chunk_metadata = {
                    "title": doc_title,
                    "page": page_num,
                    "url": doc_url,
                    "document_id": document_id
                }

                # Chunk the page text
                page_chunks = chunk_document(page_text, chunk_metadata)
                all_chunks.extend(page_chunks)

            logger.info(f"Total chunks created: {len(all_chunks)}")

            # Generate embeddings for all chunks
            chunk_texts = [chunk["text"] for chunk in all_chunks]
            embeddings = self.generate_embeddings(chunk_texts)

            # Store in Qdrant
            self.store_chunks_in_qdrant(all_chunks, embeddings, document_id)

            # Save chunks to disk for debugging
            self._save_chunks(document_id, all_chunks)

            # Publish ChunksIndexed event
            self.publish_chunks_indexed_event(document_id, correlation_id, len(all_chunks))

            logger.info(f"Successfully indexed document {document_id}")

        except Exception as e:
            logger.error(f"Error processing DocumentExtracted event: {str(e)}", exc_info=True)
            # Publish IndexingFailed event
            self._publish_indexing_failed_event(event, str(e))

    def publish_chunks_indexed_event(self, document_id: str, correlation_id: str,
                                     chunk_count: int):
        """
        Publish ChunksIndexed event to RabbitMQ.

        Args:
            document_id: Document identifier
            correlation_id: Correlation ID from original event
            chunk_count: Number of chunks indexed
        """
        logger.info(f"Publishing ChunksIndexed event for document {document_id}")

        # Create ChunksIndexed event using common helper
        event = create_chunks_indexed_event(
            document_id=document_id,
            correlation_id=correlation_id,
            chunk_count=chunk_count,
            embedding_model="all-MiniLM-L6-v2",
            vector_dim=self.vector_size,
            index_name=self.collection_name
        )

        # Save event to storage (event sourcing)
        self._save_event(document_id, event, "indexed.json")

        # Publish to RabbitMQ
        self.event_broker.publish(
            routing_key="documents.indexed",
            message=json.dumps(event)
        )

        logger.info(f"ChunksIndexed event published for document {document_id}")

    def _publish_indexing_failed_event(self, original_event: Dict[str, Any], error_message: str):
        """
        Publish IndexingFailed event when processing fails.

        Args:
            original_event: The original DocumentExtracted event
            error_message: Error description
        """
        try:
            document_id = original_event["payload"]["documentId"]
            correlation_id = original_event["correlationId"]

            logger.info(f"Publishing IndexingFailed event for document {document_id}")

            # Create IndexingFailed event using common helper
            event = create_indexing_failed_event(
                document_id=document_id,
                correlation_id=correlation_id,
                error_message=error_message,
                error_type="IndexingError"
            )

            # Publish to RabbitMQ
            self.event_broker.publish(
                routing_key="documents.indexing.failed",
                message=json.dumps(event)
            )

            logger.info(f"IndexingFailed event published for document {document_id}")

        except Exception as e:
            logger.error(f"Error publishing IndexingFailed event: {str(e)}", exc_info=True)

    def close(self):
        """Clean up resources."""
        logger.info("Closing Indexing Service")
        if self.event_broker:
            self.event_broker.close()
        logger.info("Indexing Service closed")
