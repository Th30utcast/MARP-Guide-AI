"""
Ingestion Service - PDF Discovery and Fetching Service

This service discovers PDFs from the MARP website, downloads them,
and publishes DocumentDiscovered events for downstream processing.

Architecture:
    - Microservice: Runs as a standalone worker process
    - Communication: Event-driven via RabbitMQ message broker
    - Storage: Event-sourced (saves events to disk as source of truth)

Pipeline Position:
    [Ingestion Service] → DocumentDiscovered → Extraction Service
"""

import json
import logging
import hashlib
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup

from common.events import create_document_discovered_event

logger = logging.getLogger(__name__)


class MARPScraper:
    """Web scraper for discovering PDF links on the MARP website."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def discover_pdfs(self) -> List[Dict[str, str]]:
        """
        Scrape the MARP website and discover all PDF links.

        Returns:
            List of dictionaries containing PDF metadata (title, url, description)
        """
        try:
            logger.info(f"Scraping MARP website: {self.base_url}")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')
            pdf_links = []

            # Find all links that point to PDFs
            for link in soup.find_all('a', href=True):
                href = link['href']

                # Check if link points to a PDF
                if href.lower().endswith('.pdf'):
                    absolute_url = urljoin(self.base_url, href)

                    # Extract title from link text or nearby elements
                    title = link.get_text(strip=True)

                    # If link text is empty, try to find title in parent elements
                    if not title:
                        parent = link.parent
                        if parent:
                            title = parent.get_text(strip=True)

                    # Fallback to filename if no title found
                    if not title:
                        title = href.split('/')[-1].replace('.pdf', '').replace('-', ' ').title()

                    description = ""
                    parent = link.parent
                    if parent:
                        desc_elem = parent.find_next('p')
                        if desc_elem:
                            description = desc_elem.get_text(strip=True)

                    pdf_info = {
                        'title': title,
                        'url': absolute_url,
                        'description': description
                    }

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
    """Fetcher for downloading PDF files."""

    def __init__(self, output_dir: str = "/app/pdfs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_pdf(self, url: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Download a PDF from the given URL.

        Args:
            url: URL to download PDF from
            document_id: Unique identifier for the document

        Returns:
            Dictionary with file information or None if failed
        """
        try:
            logger.info(f"Fetching PDF from: {url}")

            # Download PDF
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()

            # Generate filename
            filename = f"{document_id}.pdf"
            file_path = self.output_dir / filename

            # Save PDF and calculate checksum
            hash_md5 = hashlib.md5()
            file_size = 0

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        hash_md5.update(chunk)
                        file_size += len(chunk)

            checksum = hash_md5.hexdigest()

            logger.info(f"PDF downloaded successfully: {file_path} ({file_size} bytes)")

            return {
                'file_path': str(file_path),
                'file_size': file_size,
                'checksum': checksum
            }

        except requests.RequestException as e:
            logger.error(f"Error downloading PDF from {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading PDF: {str(e)}")
            return None

    def file_exists(self, document_id: str) -> bool:
        """Check if PDF already exists locally."""
        filename = f"{document_id}.pdf"
        file_path = self.output_dir / filename
        return file_path.exists()


class IngestionService:
    """
    Ingestion Service that:
    1. Discovers PDFs from MARP website (via scraper)
    2. Downloads PDFs (via fetcher)
    3. Creates DocumentDiscovered events
    4. Saves events to disk (event sourcing)
    5. Publishes events to RabbitMQ
    """

    def __init__(
        self,
        event_broker,
        base_url: str,
        pdf_output_dir: str = "/app/pdfs",
        storage_path: str = "/app/storage/extracted"
    ):
        """
        Initialize the Ingestion Service.

        Args:
            event_broker: RabbitMQEventBroker instance
            base_url: MARP website URL to scrape
            pdf_output_dir: Directory to store downloaded PDFs
            storage_path: Path to storage directory for events
        """
        self.event_broker = event_broker
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize scraper and fetcher
        self.scraper = MARPScraper(base_url=base_url)
        self.fetcher = PDFFetcher(output_dir=pdf_output_dir)

        logger.info(f"Ingestion service initialized. Storage: {self.storage_path}")

    def _extract_document_id_from_url(self, url: str) -> str:
        """
        Extract the document ID from the PDF URL by using its original filename.

        Args:
            url: PDF URL

        Returns:
            Document ID (filename without .pdf extension)
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

        # Fallback if somehow we got an empty filename
        if not document_id:
            import uuid
            document_id = f"document-{uuid.uuid4().hex[:8]}"

        return document_id

    def _save_discovered_event(self, document_id: str, event: Dict[str, Any]):
        """
        Save the DocumentDiscovered event to discovered.json (event sourcing pattern).
        Saves the exact same event that will be published to RabbitMQ.

        Args:
            document_id: Document identifier
            event: The complete event dictionary to save
        """
        try:
            # Create document directory in storage
            doc_dir = self.storage_path / document_id
            doc_dir.mkdir(parents=True, exist_ok=True)

            # Save discovered.json (event-sourced)
            discovered_path = doc_dir / "discovered.json"
            with open(discovered_path, 'w', encoding='utf-8') as f:
                json.dump(event, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved DocumentDiscovered event to: {discovered_path}")

        except Exception as e:
            logger.error(f"Failed to save discovered event for {document_id}: {str(e)}")
            raise

    def _process_pdf(self, pdf_info: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Process a single PDF: fetch, create event, save, and publish.

        Args:
            pdf_info: Dictionary with 'url' and 'title' keys

        Returns:
            Processing result dictionary or None if failed
        """
        try:
            # Extract document ID from the PDF filename
            document_id = self._extract_document_id_from_url(pdf_info['url'])

            # Check if already fetched
            if self.fetcher.file_exists(document_id):
                logger.info(f"⏭️ PDF already exists: {pdf_info['title']}")
                return {
                    "status": "skipped",
                    "document_id": document_id,
                    "title": pdf_info['title']
                }

            # Fetch PDF
            logger.info(f"📥 Fetching: {pdf_info['title']}")
            fetch_result = self.fetcher.fetch_pdf(pdf_info['url'], document_id)

            if not fetch_result:
                logger.error(f"❌ Failed to fetch: {pdf_info['title']}")
                return None

            # Create DocumentDiscovered event using helper function
            event = create_document_discovered_event(
                document_id=document_id,
                title=pdf_info['title'],
                url=fetch_result['file_path'],  # Local file path for Extraction
                file_size=fetch_result['file_size'],
                original_url=pdf_info['url']  # Original web URL for reference
            )

            # Save DocumentDiscovered event to discovered.json (event-sourced)
            self._save_discovered_event(document_id, event)

            # Publish event to RabbitMQ
            self.event_broker.publish(
                routing_key="documents.discovered",
                message=json.dumps(event),
                exchange="events"
            )

            logger.info(f"✅ Published event for: {pdf_info['title']}")

            return {
                "status": "published",
                "document_id": document_id,
                "title": pdf_info['title'],
                "event": event
            }

        except Exception as e:
            logger.error(f"Error processing {pdf_info['title']}: {str(e)}")
            return None

    def run_ingestion(self) -> Dict[str, Any]:
        """
        Run the complete ingestion process:
        1. Discover PDFs from MARP website
        2. Fetch each PDF
        3. Publish DocumentDiscovered events

        Returns:
            Dictionary with ingestion statistics
        """
        try:
            logger.info("🚀 Starting ingestion process...")

            # Step 1: Discover PDFs
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
                    "skipped": 0
                }

            logger.info(f"✅ Discovered {len(discovered_pdfs)} PDFs")

            # Step 2 & 3: Fetch PDFs and publish events
            fetched_count = 0
            published_count = 0
            skipped_count = 0

            for pdf_info in discovered_pdfs:
                result = self._process_pdf(pdf_info)

                if result:
                    if result["status"] == "published":
                        fetched_count += 1
                        published_count += 1
                    elif result["status"] == "skipped":
                        skipped_count += 1

            logger.info(
                f"🎉 Ingestion completed: {fetched_count} fetched, "
                f"{published_count} events published, {skipped_count} skipped"
            )

            return {
                "status": "completed",
                "message": "Ingestion process completed successfully",
                "discovered": len(discovered_pdfs),
                "fetched": fetched_count,
                "published": published_count,
                "skipped": skipped_count
            }

        except Exception as e:
            logger.error(f"Error during ingestion: {str(e)}")
            raise

    def close(self):
        """Clean up resources."""
        logger.info("Closing Ingestion Service")
        if self.event_broker:
            self.event_broker.close()
        logger.info("Ingestion Service closed")
