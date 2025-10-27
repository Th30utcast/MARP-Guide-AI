import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import pdfplumber
import logging

logger = logging.getLogger(__name__)


class ExtractionService:
    """
    Extraction Service: Consumes DocumentDiscovered events, extracts text
    and metadata from PDFs, and publishes DocumentExtracted events.
    """

    def __init__(self, event_broker=None):
        """
        Initialize the Extraction Service.
        
        Args:
            event_broker: Message broker instance for publishing events
                         (RabbitMQ, Kafka, etc.)
        """
        self.event_broker = event_broker
        self.extraction_method = "pdfplumber"

    def extract_document(self, document_discovered_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract text and metadata from a PDF document.
        
        Args:
            document_discovered_event: The DocumentDiscovered event containing
                                       document_id, url, title, etc.
        
        Returns:
            document_extracted_event: The DocumentExtracted event to be published
        """
        payload = document_discovered_event.get("payload", {})
        document_id = payload.get("documentId")
        url = payload.get("url")
        title = payload.get("title")
        correlation_id = document_discovered_event.get("correlationId")

        try:
            logger.info(f"Starting extraction for document: {document_id}")
            
            # Extract text and metadata from PDF
            extracted_data = self._extract_pdf_content(url)
            
            # Build the DocumentExtracted event
            document_extracted_event = self._build_document_extracted_event(
                document_id=document_id,
                title=title,
                correlation_id=correlation_id,
                extracted_data=extracted_data
            )
            
            logger.info(f"Successfully extracted document: {document_id}")
            return document_extracted_event
            
        except Exception as e:
            logger.error(f"Failed to extract document {document_id}: {str(e)}")
            raise

    def _extract_pdf_content(self, pdf_url: str) -> Dict[str, Any]:
        """
        Extract text and metadata from a PDF file using pdfplumber.
        
        Args:
            pdf_url: URL or local path to the PDF file
        
        Returns:
            Dictionary containing extracted content and metadata
        """
        extracted_data = {
            "text_extracted": False,
            "page_count": 0,
            "metadata": {},
            "full_text": [],
            "extraction_method": self.extraction_method
        }
        
        try:
            with pdfplumber.open(pdf_url) as pdf:
                # Extract metadata
                extracted_data["metadata"] = {
                    "title": pdf.metadata.get("Title", "Unknown"),
                    "author": pdf.metadata.get("Author", "Unknown"),
                    "subject": pdf.metadata.get("Subject", "Unknown"),
                    "creation_date": pdf.metadata.get("CreationDate", "Unknown"),
                }
                
                # Extract year from metadata or use current year as fallback
                extracted_data["metadata"]["year"] = self._extract_year(
                    extracted_data["metadata"]
                )
                
                # Extract page count
                extracted_data["page_count"] = len(pdf.pages)
                
                # Extract text from each page
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_data["full_text"].append({
                                "page": page_num,
                                "text": page_text.strip()
                            })
                    except Exception as e:
                        logger.warning(
                            f"Failed to extract text from page {page_num}: {str(e)}"
                        )
                
                extracted_data["text_extracted"] = len(extracted_data["full_text"]) > 0
                
        except Exception as e:
            logger.error(f"Error opening or reading PDF: {str(e)}")
            raise
        
        return extracted_data

    def _extract_year(self, metadata: Dict[str, Any]) -> int:
        """
        Extract year from metadata.
        
        Args:
            metadata: Metadata dictionary from PDF
        
        Returns:
            Year as integer, or current year if not found
        """
        try:
            # Try to extract from CreationDate first (usually D:YYYYMMDD...)
            creation_date = metadata.get("creation_date", "")
            if isinstance(creation_date, str) and len(creation_date) >= 5:
                # pdfplumber returns D:YYYYMMDD format
                year_str = creation_date[2:6] if creation_date.startswith("D:") else creation_date[:4]
                return int(year_str)
        except (ValueError, IndexError):
            pass
        
        # Fallback to current year
        return datetime.now(timezone.utc).year

    def _build_document_extracted_event(
        self,
        document_id: str,
        title: str,
        correlation_id: str,
        extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build the DocumentExtracted event according to the event catalogue schema.
        
        Args:
            document_id: Unique identifier for the document
            title: Document title
            correlation_id: Correlation ID from the DocumentDiscovered event
            extracted_data: Extracted content and metadata
        
        Returns:
            DocumentExtracted event object
        """
        event = {
            "eventType": "DocumentExtracted",
            "eventId": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "correlationId": correlation_id,
            "source": "extraction-service",
            "version": "1.0",
            "payload": {
                "documentId": document_id,
                "textExtracted": extracted_data["text_extracted"],
                "pageCount": extracted_data["page_count"],
                "metadata": {
                    "title": title or extracted_data["metadata"].get("title", "Unknown"),
                    "author": extracted_data["metadata"].get("author", "Unknown"),
                    "year": extracted_data["metadata"].get("year"),
                    "subject": extracted_data["metadata"].get("subject", "Unknown")
                },
                "extractedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "extractionMethod": self.extraction_method
            }
        }
        
        return event

    def publish_event(self, event: Dict[str, Any]) -> bool:
        """
        Publish a DocumentExtracted event to the message broker.
        
        Args:
            event: The DocumentExtracted event to publish
        
        Returns:
            True if published successfully, False otherwise
        """
        if not self.event_broker:
            logger.warning("Event broker not configured. Event not published.")
            return False
        
        try:
            self.event_broker.publish(
                routing_key="documents.extracted",
                message=json.dumps(event)
            )
            logger.info(f"Published DocumentExtracted event: {event['eventId']}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")
            return False

    def handle_document_discovered_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Main handler for DocumentDiscovered events.
        
        This is the entry point for the Extraction Service when it consumes
        a DocumentDiscovered event from the message broker.
        
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
            logger.error(f"Error handling DocumentDiscovered event: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    import logging.config
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize service (without event broker for testing)
    extraction_service = ExtractionService()
    
    # Example DocumentDiscovered event
    example_event = {
        "eventType": "DocumentDiscovered",
        "eventId": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2025-10-22T14:30:00Z",
        "correlationId": "abc-123-xyz",
        "source": "ingestion-service",
        "version": "1.0",
        "payload": {
            "documentId": "marp-general-regs-2025",
            "title": "General Regulations",
            "url": "https://lancaster.ac.uk/academic-standards-and-quality/regulations-and-policies/manual-of-academic-regulations-and-procedures/general-regs.pdf",
            "discoveredAt": "2025-10-22T14:30:00Z",
            "fileSize": 2457600
        }
    }
    
    # Extract document
    # result = extraction_service.extract_document(example_event)
    # print(json.dumps(result, indent=2))