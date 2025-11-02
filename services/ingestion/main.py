import os
import logging
import uuid
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from urllib.parse import urlparse, unquote

# Add parent directory to path for common imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scraper import MARPScraper
from fetcher import PDFFetcher
from common.mq import RabbitMQEventBroker
from common.events import create_document_discovered_event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
MARP_URL = os.getenv(
    "MARP_URL",
    "https://www.lancaster.ac.uk/academic-standards-and-quality/regulations-and-policies/manual-of-academic-regulations-and-procedures/"
)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", "/app/pdfs")
STORAGE_PATH = os.getenv("STORAGE_PATH", "/app/storage/extracted")

# Global instances
event_broker = None
scraper = None
fetcher = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    global event_broker, scraper, fetcher

    # Startup
    logger.info("Starting Ingestion Service...")

    try:
        event_broker = RabbitMQEventBroker(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            username=RABBITMQ_USER,
            password=RABBITMQ_PASS
        )
        # Common broker auto-connects in __init__
        logger.info("✅ Connected to RabbitMQ")

        # Declare queues and exchange
        event_broker.declare_queue("documents.discovered")

        if event_broker.channel:
            event_broker.channel.exchange_declare(
                exchange="events",
                exchange_type="topic",
                durable=True
            )
            event_broker.channel.queue_bind(
                exchange="events",
                queue="documents.discovered",
                routing_key="documents.discovered"
            )
        logger.info("✅ Queues and exchange configured")

    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {str(e)}")
        raise

    scraper = MARPScraper(base_url=MARP_URL)
    fetcher = PDFFetcher(output_dir=PDF_OUTPUT_DIR)

    # Automatically start ingestion on startup
    logger.info("🚀 Starting automatic ingestion...")
    try:
        # Run ingestion in background
        import asyncio
        asyncio.create_task(trigger_ingestion_auto())
    except Exception as e:
        logger.error(f"Failed to start automatic ingestion: {e}")

    logger.info("✅ Ingestion Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Ingestion Service...")
    if event_broker:
        event_broker.close()


app = FastAPI(
    title="MARP Ingestion Service",
    description="Service for discovering and fetching MARP PDFs",
    version="1.0.0",
    lifespan=lifespan
)


def extract_document_id_from_url(url: str) -> str:
    """
    Extract the document ID from the PDF URL by using its original filename.
    Retursn the document ID (filename without .pdf extension)
    """

    # Parse the URL and get the path
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path)  # Decode any URL-encoded characters

    # Extract the filename (last part of the path)
    filename = path.split('/')[-1]

    # Remove the .pdf extension
    if filename.lower().endswith('.pdf'):
        document_id = filename[:-4]
    else:
        document_id = filename

    #! Fallback if somehow we got an empty filename
    if not document_id:
        document_id = f"document-{uuid.uuid4().hex[:8]}"

    return document_id


def save_discovered_event(document_id: str, event: dict):
    """
    Save the DocumentDiscovered event to discovered.json (event sourcing pattern).
    Saves the exact same event that will be published to RabbitMQ.

    Args:
        document_id: Document identifier
        event: The complete event dictionary to save
    """
    try:
        # Create document directory in storage
        storage_path = Path(STORAGE_PATH)
        doc_dir = storage_path / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)

        # Save discovered.json (event-sourced)
        discovered_path = doc_dir / "discovered.json"
        with open(discovered_path, 'w', encoding='utf-8') as f:
            json.dump(event, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Saved DocumentDiscovered event to: {discovered_path}")

    except Exception as e:
        logger.error(f"Failed to save discovered event for {document_id}: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "MARP Ingestion Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "service": "ingestion-service",
        "rabbitmq": "connected" if event_broker and event_broker.channel else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    if health_status["rabbitmq"] == "disconnected":
        return JSONResponse(status_code=503, content=health_status)

    return health_status


async def trigger_ingestion_auto():
    """Automatic ingestion triggered on startup."""
    if not event_broker or not scraper or not fetcher:
        logger.error("Service not initialized for automatic ingestion")
        return

    try:
        logger.info("🚀 Starting automatic ingestion process...")

        # Step 1: Discover PDFs
        logger.info("📡 Discovering PDFs from MARP website...")
        discovered_pdfs = scraper.discover_pdfs()

        if not discovered_pdfs:
            logger.warning("⚠️ No PDFs discovered")
            return

        logger.info(f"✅ Discovered {len(discovered_pdfs)} PDFs")

        # Step 2 & 3: Fetch PDFs and publish events
        fetched_count = 0
        published_count = 0

        for pdf_info in discovered_pdfs:
            try:
                # Extract document ID from the PDF filename
                document_id = extract_document_id_from_url(pdf_info['url'])

                # Check if already fetched
                if fetcher.file_exists(document_id):
                    logger.info(f"⏭️ PDF already exists: {pdf_info['title']}")
                    continue

                # Fetch PDF
                logger.info(f"📥 Fetching: {pdf_info['title']}")
                fetch_result = fetcher.fetch_pdf(pdf_info['url'], document_id)

                if not fetch_result:
                    logger.error(f"❌ Failed to fetch: {pdf_info['title']}")
                    continue

                fetched_count += 1

                # Create DocumentDiscovered event using helper function
                event = create_document_discovered_event(
                    document_id=document_id,
                    title=pdf_info['title'],
                    url=fetch_result['file_path'],  # Local file path for Extraction
                    file_size=fetch_result['file_size'],
                    original_url=pdf_info['url']  # Original web URL for reference
                )

                # Save DocumentDiscovered event to discovered.json (event-sourced)
                save_discovered_event(document_id, event)

                event_broker.publish(
                    routing_key="documents.discovered",
                    message=json.dumps(event),
                    exchange="events"
                )

                published_count += 1
                logger.info(f"✅ Published event for: {pdf_info['title']}")

            except Exception as e:
                logger.error(f"Error processing {pdf_info['title']}: {str(e)}")
                continue

        logger.info(f"🎉 Automatic ingestion completed: {fetched_count} fetched, {published_count} events published")

    except Exception as e:
        logger.error(f"Error during automatic ingestion: {str(e)}")


@app.post("/ingest")
async def trigger_ingestion():
    """
    Trigger the ingestion process:
    1. Discover PDFs from MARP website
    2. Fetch/download PDFs
    3. Publish DocumentDiscovered events
    """
    if not event_broker or not scraper or not fetcher:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        logger.info("🚀 Starting ingestion process...")

        # Step 1: Discover PDFs
        logger.info("📡 Discovering PDFs from MARP website...")
        discovered_pdfs = scraper.discover_pdfs()

        if not discovered_pdfs:
            logger.warning("⚠️ No PDFs discovered")
            return {
                "status": "completed",
                "message": "No PDFs found",
                "discovered": 0,
                "fetched": 0,
                "published": 0
            }

        logger.info(f"✅ Discovered {len(discovered_pdfs)} PDFs")

        # Step 2 and 3: Fetch PDFs and publish events
        fetched_count = 0
        published_count = 0

        for pdf_info in discovered_pdfs:
            try:
                # Extract document ID from the PDF filename
                document_id = extract_document_id_from_url(pdf_info['url'])

                # Check if already fetched
                if fetcher.file_exists(document_id):
                    logger.info(f"⏭️ PDF already exists: {pdf_info['title']}")
                    continue

                # Fetch PDF
                logger.info(f"📥 Fetching: {pdf_info['title']}")
                fetch_result = fetcher.fetch_pdf(pdf_info['url'], document_id)

                if not fetch_result:
                    logger.error(f"❌ Failed to fetch: {pdf_info['title']}")
                    continue

                fetched_count += 1

                # Create DocumentDiscovered event using helper function
                event = create_document_discovered_event(
                    document_id=document_id,
                    title=pdf_info['title'],
                    url=fetch_result['file_path'],  # Local file path for Extraction
                    file_size=fetch_result['file_size'],
                    original_url=pdf_info['url']  # Original web URL for reference
                )

                # Save DocumentDiscovered event to discovered.json (event-sourced)
                save_discovered_event(document_id, event)

                event_broker.publish(
                    routing_key="documents.discovered",
                    message=json.dumps(event),
                    exchange="events"
                )

                published_count += 1
                logger.info(f"✅ Published event for: {pdf_info['title']}")

            except Exception as e:
                logger.error(f"Error processing {pdf_info['title']}: {str(e)}")
                continue

        logger.info(f"🎉 Ingestion completed: {fetched_count} fetched, {published_count} events published")

        return {
            "status": "completed",
            "message": "Ingestion process completed successfully",
            "discovered": len(discovered_pdfs),
            "fetched": fetched_count,
            "published": published_count
        }

    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get ingestion statistics."""
    if not fetcher:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Count PDFs in output directory
    pdf_count = len(list(fetcher.output_dir.glob("*.pdf")))

    return {
        "total_pdfs_stored": pdf_count,
        "output_directory": str(fetcher.output_dir),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
