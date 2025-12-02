"""
Indexing Service - Converts Documents into Searchable Vectors

THE PROCESS:
1. Receives text that was extracted from a PDF
2. Breaks the text into small chunks (~200 tokens each with 50 token overlap)
3. Converts each chunk into a vector
4. Stores these vectors in a database (Qdrant)

WHY WE DO THIS:
- Can't feed entire 100-page document to AI (too big)
- Breaking into chunks lets us find the exact relevant section
- Vectors capture MEANING, not just keywords (understands "car" ≈ "automobile")
- Much faster than reading entire document every time

TECHNICAL DETAILS:
- Uses all-MiniLM-L6-v2 model (converts text → 384 numbers)
- Stores in Qdrant vector database
- Preserves metadata (title, page number, URL) for citations
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

# Set up logging so we can see what's happening
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# INDEXING SERVICE CLASS - The Main Service That Does All The Work
# ============================================================================


class IndexingService:
    """
    The main service that handles document indexing.

    RESPONSIBILITIES:
    1. Load the AI model (happens once when service starts)
    2. Connect to Qdrant database (vector storage)
    3. Process documents: chunk → embed → store
    4. Publish events to notify other services
    """

    # ========================================================================
    # INITIALIZATION - Setup (Runs Once When Service Starts)
    # ========================================================================

    def __init__(self):
        """
        Initialize the indexing service - this runs ONCE when the service starts.

        WHAT HAPPENS HERE:
        1. Connect to RabbitMQ (for sending messages to other services)
        2. Load the AI model (all-MiniLM-L6-v2)
        3. Connect to Qdrant database
        4. Create the database collection if it doesn't exist
        """
        logger.info("Initializing Indexing Service...")

        # Get RabbitMQ connection settings from environment variables
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        self.rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")

        # Get storage path (where we save files)
        self.storage_path = os.getenv("STORAGE_PATH", "/app/storage/extracted")

        # Connect to RabbitMQ (so we can send messages to other services)
        self.event_broker = RabbitMQEventBroker(
            host=self.rabbitmq_host, port=self.rabbitmq_port, username=self.rabbitmq_user, password=self.rabbitmq_password
        )

        # Load the AI embedding model
        # all-MiniLM-L6-v2 creates 384-dimensional vectors (384 numbers per chunk)
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded successfully")

        # Connect to Qdrant
        qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        logger.info(f"Connecting to Qdrant at {qdrant_host}:{qdrant_port}")

        # Retry logic for qdrant
        # Try up to 10 times with 2-second delays between attempts
        max_retries = 10
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                # Create connection to Qdrant
                self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
                # Test the connection by trying to get collections
                self.qdrant.get_collections()
                logger.info("Successfully connected to Qdrant")
                break  # Connection successful, exit the retry loop
            except Exception as e:
                if attempt < max_retries - 1:
                    # Not the last attempt - wait and retry
                    logger.warning(f"Qdrant not ready (attempt {attempt + 1}/{max_retries}): {e}")
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    # Last attempt failed - give up
                    logger.error(f"Failed to connect to Qdrant after {max_retries} attempts")
                    raise  # Re-raise the exception

        # Configure the Qdrant collection
        self.collection_name = "marp-documents"
        self.vector_size = 384  # all-MiniLM-L6-v2 creates 384-dimensional vectors

        # Create the collection if it doesn't exist
        self._setup_qdrant_collection()

        logger.info("Indexing Service initialized successfully")

    def _setup_qdrant_collection(self):
        """
        Create the Qdrant collection (database table) if it doesn't exist.

        PARAMETERS:
        - collection_name: "marp-documents" (where we store all MARP document vectors)
        - vector_size: 384 (must match our embedding model's output)
        - distance: COSINE (how we measure similarity between vectors)
        """
        try:
            # Try to create the collection
            logger.info(f"Creating collection '{self.collection_name}'")
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,  # Vectors are 384 numbers long
                    distance=Distance.COSINE,  # Use cosine similarity for search
                ),
            )
            logger.info(f"Collection '{self.collection_name}' created successfully")
        except Exception as e:
            # Collection might already exist from a previous run
            if "already exists" in str(e):
                logger.info(f"Collection '{self.collection_name}' already exists")
            else:
                # Some other error - log it but continue anyway
                logger.warning(f"Qdrant collection setup warning: {str(e)}")
                logger.info(f"Continuing anyway - collection should be usable")

    # ========================================================================
    # MAIN ENTRY POINT - The Orchestrator Function (Called for Each Document)
    # ========================================================================

    def handle_document_extracted_event(self, event: Dict[str, Any]):
        """
        Main function that processes a document - this is called by worker.py.

        THIS IS THE ORCHESTRATOR! It calls all the other functions in order:
        1. Read the extracted pages from disk
        2. Get metadata from the event (title, URL)
        3. Chunk each page into smaller pieces
        4. Generate embeddings (vectors) for all chunks
        5. Store the vectors in Qdrant database
        6. Save chunks to disk (for debugging)
        7. Publish success event to RabbitMQ

        PARAMETERS:
        - event: Dictionary containing document info (documentId, metadata, etc.)

        ERROR HANDLING:
        If anything goes wrong, we catch the error and publish an "IndexingFailed" event
        so other services know something went wrong.
        """
        try:
            # Extract document ID and correlation ID from the event
            document_id = event["payload"]["documentId"]
            correlation_id = event["correlationId"]

            logger.info(f"Processing DocumentExtracted event for document {document_id}")

            # STEP 1: Read the extracted pages from disk
            # The extraction service already saved the text to:
            # storage/extracted/{documentId}/pages.jsonl
            pages = self._read_pages(document_id)

            # STEP 2: Get metadata from the event (we'll attach this to each chunk)
            doc_metadata = event["payload"]["metadata"]
            doc_title = doc_metadata.get("title", "Unknown")
            doc_url = event["payload"].get("url", "")

            # STEP 3: Chunk each page
            # We loop through each page and break it into chunks
            all_chunks = []
            for page in pages:
                page_num = page.get("page", 0)
                page_text = page.get("text", "")

                # Create metadata for this page's chunks
                # This will be attached to every chunk from this page
                chunk_metadata = {
                    "title": doc_title,  # Document title
                    "page": page_num,  # Page number (for citations!)
                    "url": doc_url,  # URL to the original PDF
                    "document_id": document_id,  # Which document this came from
                }

                # Break this page into chunks using the chunking function
                page_chunks = self.chunk_document(page_text, chunk_metadata)
                all_chunks.extend(page_chunks)  # Add to our list of all chunks

            logger.info(f"Total chunks created: {len(all_chunks)}")

            # STEP 4: Generate embeddings (vectors) for all chunks
            # Extract just the text from each chunk (we'll embed the text)
            chunk_texts = [chunk["text"] for chunk in all_chunks]
            # Convert all texts to vectors using the AI model
            embeddings = self.generate_embeddings(chunk_texts)

            # STEP 5: Store everything in Qdrant
            # This saves the vectors along with the text and metadata
            self.store_chunks_in_qdrant(all_chunks, embeddings, document_id)

            # STEP 6: Save chunks to disk for debugging
            self._save_chunks(document_id, all_chunks)

            # STEP 7: Publish success event
            self.publish_chunks_indexed_event(document_id, correlation_id, len(all_chunks))

            logger.info(f"Successfully indexed document {document_id}")

        except Exception as e:
            # Log the error and publish a failure event
            logger.error(f"Error processing DocumentExtracted event: {str(e)}", exc_info=True)
            # Publish IndexingFailed event so other services know it failed
            self._publish_indexing_failed_event(event, str(e))

    # ========================================================================
    # CORE OPERATIONS - Helper Functions Called by the Main Orchestrator
    # ========================================================================

    def chunk_document(
        self, text: str, metadata: dict, max_tokens: int = 200, overlap_tokens: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Break a document into overlapping chunks using actual token counting.

        WHY WE CHUNK:
        - AI models have token limits (can't process 100-page documents at once)
        - Smaller chunks = more precise search results
        - Overlapping chunks preserve context at boundaries

        HOW IT WORKS:
        1. Tokenize entire text using the model's actual tokenizer
        2. Split tokens into overlapping chunks of max_tokens size
        3. Each chunk overlaps with previous by overlap_tokens (25%)
        4. Decode tokens back to text for each chunk
        5. Attach metadata (title, page, url) to each chunk

        PARAMETERS:
        - text: The full page text to split up
        - metadata: Info about the document (title, page number, url)
        - max_tokens: Maximum size of each chunk (default 200 tokens, stays under model's 256 limit)
        - overlap_tokens: Overlap between chunks (default 50 tokens = 25% overlap)

        RETURNS:
        - List of chunks, each with text and metadata
        """
        # Get the tokenizer from the loaded model
        tokenizer = self.model.tokenizer

        # Tokenize the entire text into token IDs
        tokens = tokenizer.encode(text, add_special_tokens=False)

        chunks = []
        start_idx = 0

        # Sliding window over tokens
        while start_idx < len(tokens):
            # Extract chunk of tokens (up to max_tokens)
            end_idx = min(start_idx + max_tokens, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]

            # Decode tokens back to text
            chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True).strip()

            # Only add non-empty chunks
            if chunk_text:
                chunks.append({"text": chunk_text, "metadata": metadata.copy()})

            # Move window forward by (max_tokens - overlap_tokens)
            # This creates the overlap between consecutive chunks
            start_idx += max_tokens - overlap_tokens

        logger.info(f"Chunked document into {len(chunks)} overlapping chunks")
        return chunks

    def _read_pages(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Read the extracted pages from disk.

        WHERE THE DATA COMES FROM:
        The extraction service already processed the PDF and saved the text to:
        storage/extracted/{documentId}/pages.jsonl

        FILE FORMAT (JSONL):
        Each line is a separate JSON object representing one page:
        {"page": 1, "text": "This is the content of page 1..."}
        {"page": 2, "text": "This is the content of page 2..."}

        RETURNS:
        List of page dictionaries: [{"page": 1, "text": "..."}, {"page": 2, "text": "..."}, ...]
        """
        # Build the path to the pages file
        pages_file = os.path.join(self.storage_path, document_id, "pages.jsonl")
        logger.info(f"Reading pages from {pages_file}")

        # Read the file line by line (each line is one page)
        pages = []
        with open(pages_file, "r", encoding="utf-8") as f:
            for line in f:
                # Parse the JSON on this line
                page_data = json.loads(line.strip())
                pages.append(page_data)

        logger.info(f"Read {len(pages)} pages from {pages_file}")
        return pages

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Convert text chunks into vectors (embeddings) using AI.

        PARAMETERS:
        - texts: List of text strings (our chunks)

        RETURNS:
        - Numpy array of shape (num_chunks, 384)
          Each chunk becomes 384 numbers
        """
        logger.info(f"Generating embeddings for {len(texts)} chunks")

        # Use the AI model to convert all texts to vectors
        embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=False)

        logger.info(f"Generated embeddings with shape {embeddings.shape}")
        return embeddings

    def store_chunks_in_qdrant(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray, document_id: str):
        """
        Store the chunks and their vectors in Qdrant database.

        WHAT WE STORE:
        For each chunk, we store:
        1. The vector (384 numbers representing meaning)
        2. The original text (so we can return it in search results)
        3. Metadata (title, page number, URL for citations)

        PARAMETERS:
        - chunks: List of chunk dictionaries (with text and metadata)
        - embeddings: Numpy array of vectors (one per chunk)
        - document_id: Which document these chunks came from
        """
        logger.info(f"Storing {len(chunks)} chunks in Qdrant for document {document_id}")

        # Build a list of "points" to insert into Qdrant
        # Each point = one chunk with its vector and metadata
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Create a unique ID for this chunk
            # Format: "documentId_0", "documentId_1", etc.
            point_id_str = f"{document_id}_{idx}"
            # Hash it to get a numeric ID (Qdrant requires numeric IDs)
            # % (2**63) ensures it's a positive 64-bit integer
            point_id = hash(point_id_str) % (2**63)

            # Create a point (record) with vector and metadata
            points.append(
                PointStruct(
                    id=point_id,  # Unique numeric ID
                    vector=embedding.tolist(),  # Convert numpy array to list
                    payload={  # Metadata attached to this vector
                        "text": chunk["text"],  # Original text (for display)
                        "document_id": document_id,  # Which document
                        "chunk_index": idx,  # Which chunk number
                        "title": chunk["metadata"].get("title", ""),  # Document title
                        "page": chunk["metadata"].get("page", 0),  # Page number
                        "url": chunk["metadata"].get("url", ""),  # PDF URL
                    },
                )
            )

        # Insert (or update if exists) all points into Qdrant
        # "upsert" = update if exists, insert if new
        self.qdrant.upsert(collection_name=self.collection_name, points=points)
        logger.info(f"Successfully stored {len(points)} points in Qdrant")

    def _save_chunks(self, document_id: str, chunks: List[Dict[str, Any]]):
        """
        Save chunks to disk as JSON for debugging/auditing.

        FILE LOCATION:
        storage/extracted/{documentId}/chunks.json
        """
        chunks_file = os.path.join(self.storage_path, document_id, "chunks.json")
        logger.info(f"Saving {len(chunks)} chunks to {chunks_file}")

        # Write the chunks as pretty-printed JSON
        # indent=2 makes it readable
        # ensure_ascii=False allows non-English characters
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        logger.info(f"Chunks saved to {chunks_file}")

    # ========================================================================
    # EVENT PUBLISHING - Notifying Other Services
    # ========================================================================

    def publish_chunks_indexed_event(self, document_id: str, correlation_id: str, chunk_count: int):
        """
        Publish a success event to RabbitMQ saying "indexing is done!"

        WHAT'S IN THE EVENT:
        - documentId: Which document we indexed
        - chunkCount: How many chunks were created
        - embeddingModel: Which AI model we used
        - vectorDim: Size of vectors (384)
        - indexName: Which collection in Qdrant

        WHERE IT GOES:
        Sent to RabbitMQ with routing_key="documents.indexed"
        Other services listening to this routing key will receive it.
        """
        logger.info(f"Publishing ChunksIndexed event for document {document_id}")

        # Create the event using a helper function (standardizes the format)
        event = create_chunks_indexed_event(
            document_id=document_id,
            correlation_id=correlation_id,
            chunk_count=chunk_count,
            embedding_model="all-MiniLM-L6-v2",
            vector_dim=self.vector_size,
            index_name=self.collection_name,
        )

        # Save the event to disk (event sourcing - keeps a record of what happened)
        self._save_event(document_id, event, "indexed.json")

        # Publish the event to RabbitMQ
        # Other services listening to "documents.indexed" will receive this
        self.event_broker.publish(routing_key=ROUTING_KEY_INDEXED, message=json.dumps(event))

        logger.info(f"ChunksIndexed event published for document {document_id}")

    def _publish_indexing_failed_event(self, original_event: Dict[str, Any], error_message: str):
        """
        Publish a failure event when something goes wrong.

        WHERE IT GOES:
        Sent to RabbitMQ with routing_key="documents.indexing.failed"
        """
        try:
            # Extract info from the original event
            document_id = original_event["payload"]["documentId"]
            correlation_id = original_event["correlationId"]

            logger.info(f"Publishing IndexingFailed event for document {document_id}")

            # Create the failure event
            event = create_indexing_failed_event(
                document_id=document_id, correlation_id=correlation_id, error_message=error_message, error_type="IndexingError"
            )

            # Publish to RabbitMQ
            self.event_broker.publish(routing_key=ROUTING_KEY_INDEXING_FAILED, message=json.dumps(event))

            logger.info(f"IndexingFailed event published for document {document_id}")

        except Exception as e:
            # If even the error publishing fails, just log it
            # (Don't want to crash the whole service because error reporting failed)
            logger.error(f"Error publishing IndexingFailed event: {str(e)}", exc_info=True)

    def _save_event(self, document_id: str, event: Dict[str, Any], filename: str):
        """
        Save an event to disk (event sourcing pattern).

        WHAT IS EVENT SOURCING:
        Instead of just storing the final state, we store every event that happened.
        This creates an audit trail: we can see exactly what happened and when.

        FILES SAVED:
        - indexed.json: When indexing succeeds
        - failed.json: When indexing fails (not currently used but could be added)

        WHY THIS IS USEFUL:
        - Debugging: see exactly what events occurred
        - Auditing: track what documents were processed
        - Recovery: can replay events if needed
        """
        event_file = os.path.join(self.storage_path, document_id, filename)
        logger.info(f"Saving event to {event_file}")

        # Write the event as JSON
        with open(event_file, "w", encoding="utf-8") as f:
            json.dump(event, f, indent=2, ensure_ascii=False)

        logger.info(f"Event saved to {event_file}")

    # ========================================================================
    # CLEANUP - Shutting Down Gracefully
    # ========================================================================

    def close(self):
        """
        Close connections when shutting down.

        WHEN THIS IS CALLED:
        When the service is shutting down (Ctrl+C or Docker stop).

        WHAT IT DOES:
        Closes the RabbitMQ connection cleanly (doesn't leave orphaned connections).
        """
        logger.info("Closing Indexing Service")
        if self.event_broker:
            self.event_broker.close()
        logger.info("Indexing Service closed")
