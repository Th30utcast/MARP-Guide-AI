"""
INGESTION SERVICE

Core logic for discovering and fetching MARP PDFs. Contains three main classes:

1. MARPScraper - Scrapes the MARP website to find PDF links
2. PDFFetcher - Downloads PDFs from discovered URLs
3. IngestionService - Orchestrates the entire ingestion process

Process: Scrape website -> Extract PDF URLs -> Download PDFs -> Save events -> Publish to RabbitMQ
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Import event creation helpers and routing keys for Event-Driven Architecture
from common.events import (
    ROUTING_KEY_DISCOVERED,
    ROUTING_KEY_INGESTION_FAILED,
    create_document_discovered_event,
    create_ingestion_failed_event,
)

logger = logging.getLogger(__name__)


# CLASS 1: Scrapes the MARP website to find all PDF links
class MARPScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        # Set user agent to avoid being blocked
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})

    # Main method: discovers all PDFs from the MARP webpage
    def discover_pdfs(self) -> List[Dict[str, str]]:
        try:
            logger.info(f"Scraping MARP website: {self.base_url}")
            # Step 1: Fetch the webpage
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()

            # Step 2: Parse HTML content
            soup = BeautifulSoup(response.content, "lxml")
            pdf_links = []

            # Step 3: Find all links that end with .pdf
            for link in soup.find_all("a", href=True):
                href = link["href"]

                if href.lower().endswith(".pdf"):
                    # Convert to absolute URL
                    absolute_url = urljoin(self.base_url, href)

                    # Extract title from link text
                    title = link.get_text(strip=True)

                    # Try parent element if no title
                    if not title:
                        parent = link.parent
                        if parent:
                            title = parent.get_text(strip=True)

                    # Fallback: use filename as title
                    if not title:
                        title = href.split("/")[-1].replace(".pdf", "").replace("-", " ").title()

                    # Try to extract description
                    description = ""
                    parent = link.parent
                    if parent:
                        desc_elem = parent.find_next("p")
                        if desc_elem:
                            description = desc_elem.get_text(strip=True)

                    # Store PDF metadata
                    pdf_info = {"title": title, "url": absolute_url, "description": description}

                    pdf_links.append(pdf_info)
                    logger.info(f"Discovered PDF: {title} - {absolute_url}")

            logger.info(f"Total PDFs discovered: {len(pdf_links)}")
            return pdf_links

        except requests.RequestException as e:
            logger.error(f"Error scraping MARP website: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during scraping: {str(e)}")
            raise


# CLASS 2: Downloads PDFs from discovered URLs
class PDFFetcher:
    def __init__(self, output_dir: str = "/app/pdfs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})

    # Downloads a PDF and calculates checksum for integrity
    def fetch_pdf(self, url: str, document_id: str) -> Optional[Dict[str, Any]]:
        try:
            logger.info(f"Fetching PDF from: {url}")

            # Download PDF with streaming
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()

            # Prepare file path
            filename = f"{document_id}.pdf"
            file_path = self.output_dir / filename

            # Save file and calculate MD5 checksum
            hash_md5 = hashlib.md5()
            file_size = 0

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        hash_md5.update(chunk)
                        file_size += len(chunk)

            checksum = hash_md5.hexdigest()

            logger.info(f"PDF downloaded successfully: {file_path} ({file_size} bytes)")

            # Return file metadata
            return {"file_path": str(file_path), "file_size": file_size, "checksum": checksum}

        except requests.RequestException as e:
            logger.error(f"Error downloading PDF from {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading PDF: {str(e)}")
            return None

    # Check if PDF already exists locally (avoid re-downloading)
    def file_exists(self, document_id: str) -> bool:
        filename = f"{document_id}.pdf"
        file_path = self.output_dir / filename
        return file_path.exists()


# CLASS 3: Main Ingestion Service - orchestrates scraping, downloading, and event publishing
class IngestionService:
    def __init__(self, event_broker, base_url: str, pdf_output_dir: str = None, storage_path: str = None):
        import os

        # RabbitMQ broker for publishing events (EDA)
        self.event_broker = event_broker

        # Setup directories from environment variables or defaults
        storage_path = storage_path or os.getenv("STORAGE_PATH", "/app/storage/extracted")
        pdf_output_dir = pdf_output_dir or os.getenv("PDF_OUTPUT_DIR", "/app/pdfs")

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize scraper and fetcher components
        self.scraper = MARPScraper(base_url=base_url)
        self.fetcher = PDFFetcher(output_dir=pdf_output_dir)

        logger.info(f"✅ Ingestion service initialized. Storage: {self.storage_path}")

    # Extract document ID from PDF URL (uses filename)
    def _extract_document_id_from_url(self, url: str) -> str:
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)

        # Get filename from URL path
        filename = path.split("/")[-1]

        # Remove .pdf extension
        if filename.lower().endswith(".pdf"):
            document_id = filename[:-4]
        else:
            document_id = filename

        # Fallback: generate random ID if needed
        if not document_id:
            import uuid

            document_id = f"document-{uuid.uuid4().hex[:8]}"

        return document_id

    # Event Sourcing: Save DocumentDiscovered event to disk (discovered.json)
    def _save_discovered_event(self, document_id: str, event: Dict[str, Any]):
        try:
            # Create directory for this document
            doc_dir = self.storage_path / document_id
            doc_dir.mkdir(parents=True, exist_ok=True)

            # Save event as JSON file (event sourcing pattern)
            discovered_path = doc_dir / "discovered.json"
            with open(discovered_path, "w", encoding="utf-8") as f:
                json.dump(event, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved DocumentDiscovered event to: {discovered_path}")

        except Exception as e:
            logger.error(f"Failed to save discovered event for {document_id}: {str(e)}")
            raise

    # EDA: Publish failure event to RabbitMQ for error monitoring
    def _publish_ingestion_failed_event(
        self, document_id: str, correlation_id: str, error_message: str, error_type: str = "IngestionError"
    ) -> bool:
        if not self.event_broker:
            logger.warning("⚠️ Event broker not configured. IngestionFailed event not published.")
            return False

        try:
            logger.info(f"📤 Publishing IngestionFailed event for document {document_id}")

            # Create failure event
            event = create_ingestion_failed_event(
                document_id=document_id, correlation_id=correlation_id, error_message=error_message, error_type=error_type
            )

            # Publish to RabbitMQ (Event-Driven Architecture)
            self.event_broker.publish(routing_key=ROUTING_KEY_INGESTION_FAILED, message=json.dumps(event), exchange="events")

            logger.info(f"✅ IngestionFailed event published for document {document_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error publishing IngestionFailed event: {str(e)}", exc_info=True)
            return False

    # Process a single PDF: download, create event, save, and publish
    def _process_pdf(self, pdf_info: Dict[str, str]) -> Optional[Dict[str, Any]]:
        document_id = None
        correlation_id = None

        try:
            # Step 1: Extract document ID from URL
            document_id = self._extract_document_id_from_url(pdf_info["url"])
            correlation_id = hashlib.md5(document_id.encode()).hexdigest()

            # Step 2: Skip if already downloaded
            if self.fetcher.file_exists(document_id):
                logger.info(f"⏭️ PDF already exists: {pdf_info['title']}")
                return {"status": "skipped", "document_id": document_id, "title": pdf_info["title"]}

            # Step 3: Download PDF
            logger.info(f"📥 Fetching: {pdf_info['title']}")
            fetch_result = self.fetcher.fetch_pdf(pdf_info["url"], document_id)

            # Step 4: Handle download failure
            if not fetch_result:
                logger.error(f"❌ Failed to fetch: {pdf_info['title']}")
                self._publish_ingestion_failed_event(
                    document_id=document_id,
                    correlation_id=correlation_id,
                    error_message=f"Failed to fetch PDF from {pdf_info['url']}",
                    error_type="FetchError",
                )
                return None

            # Step 5: Create DocumentDiscovered event (EDA)
            event = create_document_discovered_event(
                document_id=document_id,
                title=pdf_info["title"],
                url=fetch_result["file_path"],
                file_size=fetch_result["file_size"],
                original_url=pdf_info["url"],
            )

            # Step 6: Save event to disk (Event Sourcing)
            self._save_discovered_event(document_id, event)

            # Step 7: Publish event to RabbitMQ (triggers Extraction Service)
            self.event_broker.publish(routing_key=ROUTING_KEY_DISCOVERED, message=json.dumps(event), exchange="events")

            logger.info(f"✅ Published event for: {pdf_info['title']}")

            return {"status": "published", "document_id": document_id, "title": pdf_info["title"], "event": event}

        except Exception as e:
            logger.error(f"❌ Error processing {pdf_info['title']}: {str(e)}")

            # Publish failure event for monitoring
            if document_id and correlation_id:
                self._publish_ingestion_failed_event(
                    document_id=document_id, correlation_id=correlation_id, error_message=str(e), error_type=type(e).__name__
                )

            return None

    # MAIN METHOD: Runs the complete ingestion pipeline
    def run_ingestion(self) -> Dict[str, Any]:
        try:
            logger.info("🚀 Starting ingestion process...")

            # STEP 1: Discover all PDFs from MARP website
            logger.info("📡 Discovering PDFs from MARP website...")
            discovered_pdfs = self.scraper.discover_pdfs()

            # Handle case where no PDFs found
            if not discovered_pdfs:
                logger.warning("⚠️ No PDFs discovered")
                return {
                    "status": "completed",
                    "message": "No PDFs found",
                    "discovered": 0,
                    "fetched": 0,
                    "published": 0,
                    "skipped": 0,
                }

            logger.info(f"✅ Discovered {len(discovered_pdfs)} PDFs")

            # STEP 2: Process each discovered PDF
            # Counters for statistics
            fetched_count = 0
            published_count = 0
            skipped_count = 0
            failed_count = 0

            # Process each PDF (resilient: continues even if some fail)
            for pdf_info in discovered_pdfs:
                result = self._process_pdf(pdf_info)

                # Update counters based on result
                if result:
                    if result["status"] == "published":
                        fetched_count += 1
                        published_count += 1
                    elif result["status"] == "skipped":
                        skipped_count += 1
                else:
                    failed_count += 1
                    logger.warning(f"⚠️ Failed to process: {pdf_info.get('title', 'Unknown')}")

            logger.info(
                f"🎉 Ingestion completed: {fetched_count} fetched, "
                f"{published_count} events published, {skipped_count} skipped, {failed_count} failed"
            )

            # Return summary statistics
            return {
                "status": "completed",
                "message": "Ingestion process completed successfully",
                "discovered": len(discovered_pdfs),
                "fetched": fetched_count,
                "published": published_count,
                "skipped": skipped_count,
                "failed": failed_count,
            }

        except Exception as e:
            logger.error(f"Error during ingestion: {str(e)}")
            raise

    # Cleanup method: closes connections
    def close(self):
        logger.info("Closing Ingestion Service")
        if self.event_broker:
            self.event_broker.close()
        logger.info("Ingestion Service closed")
