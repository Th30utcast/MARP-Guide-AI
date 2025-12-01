import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pdfplumber

from common.events import (
    ROUTING_KEY_EXTRACTED,
    ROUTING_KEY_EXTRACTION_FAILED,
    create_document_extracted_event,
    create_extraction_failed_event,
)

logger = logging.getLogger(__name__)


class ExtractionService:
    def __init__(self, event_broker=None, storage_path: str = None):
        self.event_broker = event_broker
        # Use env var with fallback to absolute path
        storage_path = storage_path or os.getenv("STORAGE_PATH", "/app/storage/extracted")
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.extraction_method = "pdfplumber"
        logger.info(f"✅ Extraction service initialized. Storage: {self.storage_path}")

    def extract_document(self, document_discovered_event: Dict[str, Any]) -> Dict[str, Any]:
        payload = document_discovered_event.get("payload", {})
        document_id = payload.get("documentId")
        url = payload.get("url")
        title = payload.get("title", "Unknown")
        original_url = payload.get("originalUrl", "")
        correlation_id = document_discovered_event.get("correlationId")
        try:
            logger.info(f"🔄 Starting extraction for document: {document_id}")
            # Extract PDF content
            extracted_data = self._extract_pdf_content(url)
            # Save extracted content to disk (event-sourced)
            pages_ref = self._save_extracted_content(document_id=document_id, extracted_data=extracted_data)
            # Build DocumentExtracted event using common helper
            document_extracted_event = create_document_extracted_event(
                document_id=document_id,
                correlation_id=correlation_id,
                page_count=extracted_data["page_count"],
                text_extracted=extracted_data["text_extracted"],
                pdf_metadata=extracted_data["metadata"],
                extraction_method=extracted_data["extraction_method"],
                url=original_url,
                pages_ref=pages_ref,
            )
            # Save the event to disk (event sourcing)
            self._save_event(document_id, document_extracted_event, "extracted.json")
            logger.info(f"✅ Successfully extracted document: {document_id}")
            return document_extracted_event
        except Exception as e:
            logger.error(f"❌ Failed to extract document {document_id}: {str(e)}")
            raise

    def _extract_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        # Extract text and metadata from a PDF file using pdfplumber.
        # Returns a dictionary containing the content and metadata that was extracted
        extracted_data = {
            "text_extracted": False,
            "page_count": 0,
            "metadata": {},
            "pages": [],
            "extraction_method": self.extraction_method,
        }
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pdf_meta = pdf.metadata or {}
                extracted_data["metadata"] = {
                    "title": pdf_meta.get("Title", "Unknown"),
                    "author": pdf_meta.get("Author", "Unknown"),
                    "subject": pdf_meta.get("Subject", ""),
                    "creator": pdf_meta.get("Creator", ""),
                    "producer": pdf_meta.get("Producer", ""),
                    "creation_date": pdf_meta.get("CreationDate", ""),
                }

                extracted_data["metadata"]["year"] = self._extract_year(extracted_data["metadata"])

                extracted_data["page_count"] = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            extracted_data["pages"].append({"page": page_num, "text": page_text.strip()})
                        else:
                            #! NOTE: Mark pages with no text (might be scanned/images)
                            logger.warning(f"⚠️ No text found on page {page_num}")
                            extracted_data["pages"].append(
                                {"page": page_num, "text": "", "note": "No extractable text (might be scanned image)"}
                            )
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to extract text from page {page_num}: {e}")
                        extracted_data["pages"].append({"page": page_num, "text": "", "error": str(e)})
                extracted_data["text_extracted"] = any(p.get("text") for p in extracted_data["pages"])
        except Exception as e:
            logger.error(f"❌ Error opening or reading PDF: {e}")
            raise
        return extracted_data

    def _extract_year(self, metadata: Dict[str, Any]) -> int:
        # !Extract year from metadata, fallback to current year
        try:
            creation_date = metadata.get("creation_date", "")
            if isinstance(creation_date, str) and len(creation_date) >= 5:
                #! NOTE: PDF dates are often like "D:20250122..."
                year_str = creation_date[2:6] if creation_date.startswith("D:") else creation_date[:4]
                return int(year_str)
        except (ValueError, IndexError):
            pass

        return datetime.now(timezone.utc).year

    def _save_extracted_content(self, document_id: str, extracted_data: Dict[str, Any]) -> str:
        # Document directory should already exist (created by Ingestion)
        doc_dir = self.storage_path / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        # Read discovered.json to get original discovery metadata (optional, for logging)
        discovered_path = doc_dir / "discovered.json"
        try:
            with open(discovered_path, "r", encoding="utf-8") as f:
                discovered_event = json.load(f)
            logger.info(f"📖 Read DocumentDiscovered event from: {discovered_path}")
        except FileNotFoundError:
            logger.warning(f"⚠️ discovered.json not found for {document_id}")
        pages_path = doc_dir / "pages.jsonl"
        # Save pages.jsonl (one JSON object per line)
        with open(pages_path, "w", encoding="utf-8") as f:
            for page_data in extracted_data["pages"]:
                page_record = {"documentId": document_id, **page_data}
                f.write(json.dumps(page_record, ensure_ascii=False) + "\n")
        logger.info(f"📄 Saved {len(extracted_data['pages'])} pages to: {pages_path}")
        return str(pages_path.absolute())

    def _save_event(self, document_id: str, event: Dict[str, Any], filename: str):
        doc_dir = self.storage_path / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        event_file = doc_dir / filename
        with open(event_file, "w", encoding="utf-8") as f:
            json.dump(event, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Saved event to: {event_file}")

    def publish_event(self, event: Dict[str, Any]) -> bool:
        if not self.event_broker:
            logger.warning("⚠️ Event broker not configured. Event not published.")
            return False
        try:
            self.event_broker.publish(routing_key=ROUTING_KEY_EXTRACTED, message=json.dumps(event), exchange="events")
            logger.info(f"✅ Published DocumentExtracted event: {event['eventId']}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to publish event: {e}")
            return False

    def _publish_extraction_failed_event(
        # Publish ExtractionFailed event for monitoring failed extractions
        self,
        document_id: str,
        correlation_id: str,
        error_message: str,
        error_type: str = "ExtractionError",
    ) -> bool:
        if not self.event_broker:
            logger.warning("⚠️ Event broker not configured. ExtractionFailed event not published.")
            return False
        try:
            logger.info(f"📤 Publishing ExtractionFailed event for document {document_id}")
            # Create ExtractionFailed event using common helper
            event = create_extraction_failed_event(
                document_id=document_id, correlation_id=correlation_id, error_message=error_message, error_type=error_type
            )
            # Publish to RabbitMQ
            self.event_broker.publish(routing_key=ROUTING_KEY_EXTRACTION_FAILED, message=json.dumps(event), exchange="events")
            logger.info(f"✅ ExtractionFailed event published for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error publishing ExtractionFailed event: {str(e)}", exc_info=True)
            return False

    def handle_document_discovered_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            document_extracted_event = self.extract_document(event)
            self.publish_event(document_extracted_event)
            return document_extracted_event
        except Exception as e:
            logger.error(f"❌ Error handling DocumentDiscovered event: {e}")

            # Publish ExtractionFailed event for monitoring
            payload = event.get("payload", {})
            document_id = payload.get("documentId", "unknown")
            correlation_id = event.get("correlationId", "unknown")
            self._publish_extraction_failed_event(
                document_id=document_id, correlation_id=correlation_id, error_message=str(e), error_type=type(e).__name__
            )
            return None

    def close(self):
        """Clean up resources."""
        logger.info("🔒 Closing Extraction Service")
        if self.event_broker:
            self.event_broker.close()
        logger.info("✅ Extraction Service closed")
