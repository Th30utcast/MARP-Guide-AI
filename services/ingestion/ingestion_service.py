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

from common.events import (
    ROUTING_KEY_DISCOVERED,
    ROUTING_KEY_INGESTION_FAILED,
    create_document_discovered_event,
    create_ingestion_failed_event,
)

logger = logging.getLogger(__name__)


class MARPScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})

    def discover_pdfs(self) -> List[Dict[str, str]]:
        """Scrape MARP website and extract PDF links with titles and descriptions"""
        try:
            logger.info(f"Scraping MARP website: {self.base_url}")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")
            pdf_links = []

            for link in soup.find_all("a", href=True):
                href = link["href"]

                if href.lower().endswith(".pdf"):
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

                    # Extract description
                    description = ""
                    parent = link.parent
                    if parent:
                        desc_elem = parent.find_next("p")
                        if desc_elem:
                            description = desc_elem.get_text(strip=True)

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


class PDFFetcher:
    def __init__(self, output_dir: str = "/app/pdfs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})

    def fetch_pdf(self, url: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Download PDF and calculate MD5 checksum, returns file metadata"""
        try:
            logger.info(f"Fetching PDF from: {url}")

            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()

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

            return {"file_path": str(file_path), "file_size": file_size, "checksum": checksum}

        except requests.RequestException as e:
            logger.error(f"Error downloading PDF from {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading PDF: {str(e)}")
            return None

    def file_exists(self, document_id: str) -> bool:
        """Check if PDF already exists locally"""
        filename = f"{document_id}.pdf"
        file_path = self.output_dir / filename
        return file_path.exists()


class IngestionService:
    """Orchestrates PDF discovery, download, and event publishing to RabbitMQ"""

    def __init__(self, event_broker, base_url: str, pdf_output_dir: str = None, storage_path: str = None):
        import os

        self.event_broker = event_broker

        storage_path = storage_path or os.getenv("STORAGE_PATH", "/app/storage/extracted")
        pdf_output_dir = pdf_output_dir or os.getenv("PDF_OUTPUT_DIR", "/app/pdfs")

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.scraper = MARPScraper(base_url=base_url)
        self.fetcher = PDFFetcher(output_dir=pdf_output_dir)

        logger.info(f"✅ Ingestion service initialized. Storage: {self.storage_path}")

    def _extract_document_id_from_url(self, url: str) -> str:
        """Extract document ID from PDF filename in URL"""
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        filename = path.split("/")[-1]

        if filename.lower().endswith(".pdf"):
            document_id = filename[:-4]
        else:
            document_id = filename

        if not document_id:
            import uuid

            document_id = f"document-{uuid.uuid4().hex[:8]}"

        return document_id

    def _save_discovered_event(self, document_id: str, event: Dict[str, Any]):
        """Save DocumentDiscovered event to storage/extracted/{documentId}/discovered.json"""
        try:
            doc_dir = self.storage_path / document_id
            doc_dir.mkdir(parents=True, exist_ok=True)

            discovered_path = doc_dir / "discovered.json"
            with open(discovered_path, "w", encoding="utf-8") as f:
                json.dump(event, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved DocumentDiscovered event to: {discovered_path}")

        except Exception as e:
            logger.error(f"Failed to save discovered event for {document_id}: {str(e)}")
            raise

    def _publish_ingestion_failed_event(
        self, document_id: str, correlation_id: str, error_message: str, error_type: str = "IngestionError"
    ) -> bool:
        """Publish IngestionFailed event to RabbitMQ for error monitoring"""
        if not self.event_broker:
            logger.warning("⚠️ Event broker not configured. IngestionFailed event not published.")
            return False

        try:
            logger.info(f"📤 Publishing IngestionFailed event for document {document_id}")

            event = create_ingestion_failed_event(
                document_id=document_id, correlation_id=correlation_id, error_message=error_message, error_type=error_type
            )

            self.event_broker.publish(routing_key=ROUTING_KEY_INGESTION_FAILED, message=json.dumps(event), exchange="events")

            logger.info(f"✅ IngestionFailed event published for document {document_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error publishing IngestionFailed event: {str(e)}", exc_info=True)
            return False

    def _process_pdf(self, pdf_info: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Process single PDF: download, create event, save to disk, and publish to RabbitMQ"""
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

            logger.info("📡 Discovering PDFs from MARP website...")
            discovered_pdfs = self.scraper.discover_pdfs()

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

            # Process each discovered PDF
            fetched_count = 0
            published_count = 0
            skipped_count = 0
            failed_count = 0

            for pdf_info in discovered_pdfs:
                result = self._process_pdf(pdf_info)

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

    def close(self):
        """Close RabbitMQ connection"""
        logger.info("Closing Ingestion Service")
        if self.event_broker:
            self.event_broker.close()
        logger.info("Ingestion Service closed")
