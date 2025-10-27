"""
Extraction Service: Consumes DocumentDiscovered events, extracts text
and metadata from PDFs, stores them to disk, and publishes DocumentExtracted events.
"""
import json
import uuid
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import pdfplumber
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from common.events import create_document_extracted_event

logger = logging.getLogger(__name__)

class ExtractionService:
    """
    Extraction Service that:
    1. Consumes DocumentDiscovered events
    2. Downloads/reads PDF
    3. Extracts text (per-page) + metadata
    4. Saves pages.jsonl + metadata.json to disk
    5. Publishes DocumentExtracted event with references
    """

    def __init__(self, event_broker=None, storage_path: str = "./storage/extracted"):
        """
        Initialize the Extraction Service.
        
        Args:
            event_broker: Message broker instance for publishing events
            storage_path: Base path for storing extracted content
        """
        self.event_broker = event_broker
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.extraction_method = "pdfplumber"
        logger.info(f"Extraction service initialized. Storage: {self.storage_path}")

    def extract_document(self, document_discovered_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract text and metadata from a PDF document.
        
        Args:
            document_discovered_event: The DocumentDiscovered event
        
        Returns:
            document_extracted_event: The DocumentExtracted event to publish
        """
        payload = document_discovered_event.get("payload", {})
        document_id = payload.get("documentId")
        url = payload.get("url")
        title = payload.get("title", "Unknown")
        correlation_id = document_discovered_event.get("correlationId")

        try:
            logger.info(f"Starting extraction for document: {document_id}")
            
            # Extract text and metadata from PDF
            extracted_data = self._extract_pdf_content(url)
            
            # Save extracted content to disk
            storage_refs = self._save_extracted_content(
                document_id=document_id,
                title=title,
                url=url,
                extracted_data=extracted_data
            )
            
            # Build the DocumentExtracted event with storage references
            document_extracted_event = self._build_document_extracted_event(
                document_id=document_id,
                correlation_id=correlation_id,
                extracted_data=extracted_data,
                storage_refs=storage_refs
            )
            
            logger.info(f"Successfully extracted document: {document_id}")
            return document_extracted_event
            
        except Exception as e:
            logger.error(f"Failed to extract document {document_id}: {str(e)}")
            raise

    def _extract_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text and metadata from a PDF file using pdfplumber.
        
        Args:
            pdf_path: Path or URL to the PDF file
        
        Returns:
            Dictionary containing extracted content and metadata
        """
        extracted_data = {
            "text_extracted": False,
            "page_count": 0,
            "metadata": {},
            "pages": [],  # List of {page: int, text: str}
            "extraction_method": self.extraction_method
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract PDF metadata
                pdf_meta = pdf.metadata or {}
                extracted_data["metadata"] = {
                    "title": pdf_meta.get("Title", "Unknown"),
                    "author": pdf_meta.get("Author", "Unknown"),
                    "subject": pdf_meta.get("Subject", ""),
                    "creator": pdf_meta.get("Creator", ""),
                    "producer": pdf_meta.get("Producer", ""),
                    "creation_date": pdf_meta.get("CreationDate", ""),
                }
                
                # Extract year from metadata
                extracted_data["metadata"]["year"] = self._extract_year(
                    extracted_data["metadata"]
                )
                
                # Extract page count
                extracted_data["page_count"] = len(pdf.pages)
                
                # Extract text from each page
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            extracted_data["pages"].append({
                                "page": page_num,
                                "text": page_text.strip()
                            })
                        else:
                            # Mark pages with no text (might be scanned/images)
                            logger.warning(f"No text found on page {page_num}")
                            extracted_data["pages"].append({
                                "page": page_num,
                                "text": "",
                                "note": "No extractable text (might be scanned image)"
                            })
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num}: {e}")
                        extracted_data["pages"].append({
                            "page": page_num,
                            "text": "",
                            "error": str(e)
                        })
                
                extracted_data["text_extracted"] = any(
                    p.get("text") for p in extracted_data["pages"]
                )
                
        except Exception as e:
            logger.error(f"Error opening or reading PDF: {e}")
            raise
        
        return extracted_data

    def _extract_year(self, metadata: Dict[str, Any]) -> int:
        """Extract year from metadata, fallback to current year."""
        try:
            creation_date = metadata.get("creation_date", "")
            if isinstance(creation_date, str) and len(creation_date) >= 5:
                # PDF dates are often like "D:20250122..."
                year_str = creation_date[2:6] if creation_date.startswith("D:") else creation_date[:4]
                return int(year_str)
        except (ValueError, IndexError):
            pass
        
        return datetime.now(timezone.utc).year

    def _save_extracted_content(
        self,
        document_id: str,
        title: str,
        url: str,
        extracted_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Save extracted content to disk as pages.jsonl and metadata.json.
        
        Args:
            document_id: Document identifier
            title: Document title
            url: Source URL
            extracted_data: Extracted content
        
        Returns:
            Dictionary with paths to saved files
        """
        # Create document-specific directory
        doc_dir = self.storage_path / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata.json
        metadata_path = doc_dir / "metadata.json"
        metadata = {
            "documentId": document_id,
            "title": title,
            "url": url,
            "pageCount": extracted_data["page_count"],
            "extractedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "extractionMethod": extracted_data["extraction_method"],
            "textExtracted": extracted_data["text_extracted"],
            "metadata": extracted_data["metadata"]
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved metadata to: {metadata_path}")
        
        # Save pages.jsonl (one JSON object per line)
        pages_path = doc_dir / "pages.jsonl"
        with open(pages_path, 'w', encoding='utf-8') as f:
            for page_data in extracted_data["pages"]:
                page_record = {
                    "documentId": document_id,
                    **page_data
                }
                f.write(json.dumps(page_record, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(extracted_data['pages'])} pages to: {pages_path}")
        
        return {
            "metadataRef": str(metadata_path.absolute()),
            "textRef": str(pages_path.absolute())
        }
        
    def _build_document_extracted_event(
        self,
        document_id: str,
        correlation_id: str,
        extracted_data: Dict[str, Any],
        storage_refs: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Build the DocumentExtracted event using the common helper function.
        """
        # Use the helper function from common.events!
        return create_document_extracted_event(
            document_id=document_id,
            correlation_id=correlation_id,
            page_count=extracted_data["page_count"],
            text_extracted=extracted_data["text_extracted"],
            metadata=extracted_data["metadata"],
            metadata_ref=storage_refs["metadataRef"],
            text_ref=storage_refs["textRef"],
            extraction_method=extracted_data["extraction_method"]
        )

    def publish_event(self, event: Dict[str, Any]) -> bool:
        """
        Publish a DocumentExtracted event to the message broker.
        
        Args:
            event: The DocumentExtracted event
        
        Returns:
            True if published successfully
        """
        if not self.event_broker:
            logger.warning("Event broker not configured. Event not published.")
            return False
        
        try:
            self.event_broker.publish(
                routing_key="documents.extracted",
                message=json.dumps(event),
                exchange="events"
            )
            logger.info(f"Published DocumentExtracted event: {event['eventId']}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    def handle_document_discovered_event(
        self, 
        event: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Main handler for DocumentDiscovered events.
        This is called by the worker when consuming from RabbitMQ.
        
        Args:
            event: The DocumentDiscovered event
        
        Returns:
            The DocumentExtracted event if successful, None otherwise
        """
        try:
            document_extracted_event = self.extract_document(event)
            self.publish_event(document_extracted_event)
            return document_extracted_event
        except Exception as e:
            logger.error(f"Error handling DocumentDiscovered event: {e}")
            return None


if __name__ == "__main__":
    # Quick local test without RabbitMQ
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test with a sample event
    sample_event = {
        "eventType": "DocumentDiscovered",
        "eventId": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "correlationId": "test-123",
        "source": "test",
        "version": "1.0",
        "payload": {
            "documentId": "test-doc",
            "title": "Test Document",
            "url": "./test-pdfs/sample.pdf",  # Put a test PDF here
            "discoveredAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "fileSize": 12345
        }
    }
    
    service = ExtractionService()
    result = service.extract_document(sample_event)
    print(json.dumps(result, indent=2))