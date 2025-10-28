import os
import logging
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from scraper import MARPScraper
from fetcher import PDFFetcher
from event_broker import RabbitMQEventBroker

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
        event_broker.connect()
        logger.info("✅ Connected to RabbitMQ")
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


def create_document_discovered_event(document_id: str, title: str, url: str,
                                     file_path: str, file_size: int, metadata: dict = None) -> dict:
    """Create a DocumentDiscovered event matching the expected schema."""
    return {
        "eventType": "DocumentDiscovered",
        "eventId": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "correlationId": str(uuid.uuid4()),
        "source": "ingestion-service",
        "version": "1.0",
        "payload": {
            "documentId": document_id,
            "title": title,
            "url": file_path,  # Local file path for Extraction to read
            "originalUrl": url,  # Original web URL for reference
            "discoveredAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "fileSize": file_size,
            "metadata": metadata or {}
        }
    }


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
                # Generate document ID from URL
                document_id = f"marp-{uuid.uuid5(uuid.NAMESPACE_URL, pdf_info['url'])}"

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

                # Publish DocumentDiscovered event
                event = create_document_discovered_event(
                    document_id=document_id,
                    title=pdf_info['title'],
                    url=pdf_info['url'],
                    file_path=fetch_result['file_path'],
                    file_size=fetch_result['file_size'],
                    metadata=fetch_result.get('metadata', {})
                )

                event_broker.publish(
                    routing_key="documents.discovered",
                    message=event,
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

        # Step 2 & 3: Fetch PDFs and publish events
        fetched_count = 0
        published_count = 0

        for pdf_info in discovered_pdfs:
            try:
                # Generate document ID from URL
                document_id = f"marp-{uuid.uuid5(uuid.NAMESPACE_URL, pdf_info['url'])}"

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

                # Publish DocumentDiscovered event
                event = create_document_discovered_event(
                    document_id=document_id,
                    title=pdf_info['title'],
                    url=pdf_info['url'],
                    file_path=fetch_result['file_path'],
                    file_size=fetch_result['file_size'],
                    metadata=fetch_result.get('metadata', {})
                )

                event_broker.publish(
                    routing_key="documents.discovered",
                    message=event,
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
