"""
Indexing Service - Converts extracted text into searchable vector embeddings

Process:
1. Receive extracted text from PDFs
2. Chunk text into ~200 tokens with 50 token overlap
3. Generate embeddings using all-MiniLM-L6-v2 (384 dimensions)
4. Store vectors in Qdrant with metadata for citations
"""

import json
import logging
import os
import time
from typing import Any, Dict, List

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from common.events import (
    ROUTING_KEY_INDEXED,
    ROUTING_KEY_INDEXING_FAILED,
    create_chunks_indexed_event,
    create_indexing_failed_event,
)
from common.mq import RabbitMQEventBroker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class IndexingService:
    """Handles document chunking, embedding generation, and vector storage in Qdrant"""

    def __init__(self):
        """Initialize event broker, load embedding model, and connect to Qdrant"""
        logger.info("Initializing Indexing Service...")

        # RabbitMQ configuration
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        self.rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
        self.storage_path = os.getenv("STORAGE_PATH", "/app/storage/extracted")

        # Connect to RabbitMQ
        self.event_broker = RabbitMQEventBroker(
            host=self.rabbitmq_host, port=self.rabbitmq_port, username=self.rabbitmq_user, password=self.rabbitmq_password
        )

        # Load embedding model (all-MiniLM-L6-v2 creates 384-dimensional vectors)
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded successfully")

        # Connect to Qdrant with retry logic
        qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        logger.info(f"Connecting to Qdrant at {qdrant_host}:{qdrant_port}")
        max_retries = 10
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
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

        self.collection_name = "marp-documents"
        self.vector_size = 384
        self._setup_qdrant_collection()

        logger.info("Indexing Service initialized successfully")

    def _setup_qdrant_collection(self):
        """Create Qdrant collection with 384-dimensional vectors and cosine similarity"""
        try:
            logger.info(f"Creating collection '{self.collection_name}'")
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
            logger.info(f"Collection '{self.collection_name}' created successfully")
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"Collection '{self.collection_name}' already exists")
            else:
                logger.warning(f"Qdrant collection setup warning: {str(e)}")

    def handle_document_extracted_event(self, event: Dict[str, Any]):
        """
        Process DocumentExtracted event: read pages, chunk, embed, store in Qdrant, and publish success event
        Publishes IndexingFailed event if errors occur
        """
        try:
            document_id = event["payload"]["documentId"]
            correlation_id = event["correlationId"]
            logger.info(f"Processing DocumentExtracted event for document {document_id}")

            # Read extracted pages from disk
            pages = self._read_pages(document_id)

            # Get metadata from event
            doc_metadata = event["payload"]["metadata"]
            doc_title = doc_metadata.get("title", "Unknown")
            doc_url = event["payload"].get("url", "")

            # Chunk each page
            all_chunks = []
            for page in pages:
                page_num = page.get("page", 0)
                page_text = page.get("text", "")

                chunk_metadata = {
                    "title": doc_title,
                    "page": page_num,
                    "url": doc_url,
                    "document_id": document_id,
                }

                page_chunks = self.chunk_document(page_text, chunk_metadata)
                all_chunks.extend(page_chunks)

            logger.info(f"Total chunks created: {len(all_chunks)}")

            # Generate embeddings for all chunks
            chunk_texts = [chunk["text"] for chunk in all_chunks]
            embeddings = self.generate_embeddings(chunk_texts)

            # Store in Qdrant
            self.store_chunks_in_qdrant(all_chunks, embeddings, document_id)

            # Save chunks to disk for debugging
            self._save_chunks(document_id, all_chunks)

            # Publish success event
            self.publish_chunks_indexed_event(document_id, correlation_id, len(all_chunks))

            logger.info(f"Successfully indexed document {document_id}")

        except Exception as e:
            logger.error(f"Error processing DocumentExtracted event: {str(e)}", exc_info=True)
            self._publish_indexing_failed_event(event, str(e))

    def chunk_document(
        self, text: str, metadata: dict, max_tokens: int = 200, overlap_tokens: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks using tokenizer
        - max_tokens: 200 (stays under model's 256 limit)
        - overlap_tokens: 50 (25% overlap to preserve context)
        """
        tokenizer = self.model.tokenizer
        tokens = tokenizer.encode(text, add_special_tokens=False)

        chunks = []
        start_idx = 0

        while start_idx < len(tokens):
            end_idx = min(start_idx + max_tokens, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True).strip()

            if chunk_text:
                chunks.append({"text": chunk_text, "metadata": metadata.copy()})

            start_idx += max_tokens - overlap_tokens

        logger.info(f"Chunked document into {len(chunks)} overlapping chunks")
        return chunks

    def _read_pages(self, document_id: str) -> List[Dict[str, Any]]:
        """Read extracted pages from storage/extracted/{documentId}/pages.jsonl (JSONL format)"""
        pages_file = os.path.join(self.storage_path, document_id, "pages.jsonl")
        logger.info(f"Reading pages from {pages_file}")

        pages = []
        with open(pages_file, "r", encoding="utf-8") as f:
            for line in f:
                page_data = json.loads(line.strip())
                pages.append(page_data)

        logger.info(f"Read {len(pages)} pages from {pages_file}")
        return pages

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate 384-dimensional embeddings for text chunks using all-MiniLM-L6-v2"""
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=False)
        logger.info(f"Generated embeddings with shape {embeddings.shape}")
        return embeddings

    def store_chunks_in_qdrant(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray, document_id: str):
        """Store chunks with vectors and metadata (text, title, page, url) in Qdrant"""
        logger.info(f"Storing {len(chunks)} chunks in Qdrant for document {document_id}")

        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id_str = f"{document_id}_{idx}"
            point_id = hash(point_id_str) % (2**63)

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={
                        "text": chunk["text"],
                        "document_id": document_id,
                        "chunk_index": idx,
                        "title": chunk["metadata"].get("title", ""),
                        "page": chunk["metadata"].get("page", 0),
                        "url": chunk["metadata"].get("url", ""),
                    },
                )
            )

        self.qdrant.upsert(collection_name=self.collection_name, points=points)
        logger.info(f"Successfully stored {len(points)} points in Qdrant")

    def _save_chunks(self, document_id: str, chunks: List[Dict[str, Any]]):
        """Save chunks to storage/extracted/{documentId}/chunks.json for debugging"""
        chunks_file = os.path.join(self.storage_path, document_id, "chunks.json")
        logger.info(f"Saving {len(chunks)} chunks to {chunks_file}")

        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        logger.info(f"Chunks saved to {chunks_file}")

    def publish_chunks_indexed_event(self, document_id: str, correlation_id: str, chunk_count: int):
        """Publish ChunksIndexed event to RabbitMQ (routing_key: documents.indexed)"""
        logger.info(f"Publishing ChunksIndexed event for document {document_id}")

        event = create_chunks_indexed_event(
            document_id=document_id,
            correlation_id=correlation_id,
            chunk_count=chunk_count,
            embedding_model="all-MiniLM-L6-v2",
            vector_dim=self.vector_size,
            index_name=self.collection_name,
        )

        self._save_event(document_id, event, "indexed.json")
        self.event_broker.publish(routing_key=ROUTING_KEY_INDEXED, message=json.dumps(event))

        logger.info(f"ChunksIndexed event published for document {document_id}")

    def _publish_indexing_failed_event(self, original_event: Dict[str, Any], error_message: str):
        """Publish IndexingFailed event to RabbitMQ (routing_key: documents.indexing.failed)"""
        try:
            document_id = original_event["payload"]["documentId"]
            correlation_id = original_event["correlationId"]
            logger.info(f"Publishing IndexingFailed event for document {document_id}")

            event = create_indexing_failed_event(
                document_id=document_id, correlation_id=correlation_id, error_message=error_message, error_type="IndexingError"
            )

            self.event_broker.publish(routing_key=ROUTING_KEY_INDEXING_FAILED, message=json.dumps(event))
            logger.info(f"IndexingFailed event published for document {document_id}")

        except Exception as e:
            logger.error(f"Error publishing IndexingFailed event: {str(e)}", exc_info=True)

    def _save_event(self, document_id: str, event: Dict[str, Any], filename: str):
        """Save event to storage/extracted/{documentId}/{filename} for event sourcing and audit trail"""
        event_file = os.path.join(self.storage_path, document_id, filename)
        logger.info(f"Saving event to {event_file}")

        with open(event_file, "w", encoding="utf-8") as f:
            json.dump(event, f, indent=2, ensure_ascii=False)

        logger.info(f"Event saved to {event_file}")

    def close(self):
        """Close RabbitMQ connection gracefully"""
        logger.info("Closing Indexing Service")
        if self.event_broker:
            self.event_broker.close()
        logger.info("Indexing Service closed")
