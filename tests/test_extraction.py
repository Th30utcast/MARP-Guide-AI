"""
Tests for Extraction Service.

What this tests:
- PDF text extraction works
- Metadata extraction from PDFs
- Event handling and publishing
- Error handling for corrupted PDFs
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services" / "extraction"))

from extraction_service import ExtractionService


class TestExtractionService:
    """Test PDF extraction functionality."""

    @patch("extraction_service.pdfplumber.open")
    @patch("builtins.open", new_callable=mock_open)
    @patch("extraction_service.Path.mkdir")
    def test_extract_pdf_content_success(self, mock_mkdir, mock_file, mock_pdfplumber):
        """Test successful PDF content extraction."""
        # Mock PDF with 2 pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"

        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"

        mock_pdf = Mock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.metadata = {"Title": "Test Document", "Author": "Test Author", "CreationDate": "D:20250101120000Z"}
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)

        mock_pdfplumber.return_value = mock_pdf

        service = ExtractionService(storage_path="/tmp/storage")
        result = service._extract_pdf_content("/tmp/test.pdf")

        assert result["text_extracted"] is True
        assert result["page_count"] == 2
        assert len(result["pages"]) == 2
        assert result["pages"][0]["text"] == "Page 1 content"
        assert result["metadata"]["title"] == "Test Document"

    @patch("extraction_service.pdfplumber.open")
    def test_extract_pdf_handles_empty_pages(self, mock_pdfplumber):
        """Test handling of pages with no extractable text."""
        # Mock page with no text
        mock_page = Mock()
        mock_page.extract_text.return_value = ""

        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = {}
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)

        mock_pdfplumber.return_value = mock_pdf

        service = ExtractionService(storage_path="/tmp/storage")
        result = service._extract_pdf_content("/tmp/test.pdf")

        # Should mark text_extracted as False
        assert result["text_extracted"] is False
        assert "note" in result["pages"][0]

    def test_extract_year_from_metadata(self):
        """Test year extraction from PDF metadata."""
        service = ExtractionService(storage_path="/tmp/storage")

        # Test PDF date format
        year = service._extract_year({"creation_date": "D:20250122103045Z"})
        assert year == 2025

        # Test fallback to current year
        year = service._extract_year({"creation_date": "invalid"})
        assert year > 2020  # Should be current year

    @patch("extraction_service.ExtractionService._extract_pdf_content")
    @patch("extraction_service.ExtractionService._save_extracted_content")
    @patch("extraction_service.ExtractionService._save_event")
    @patch("builtins.open", new_callable=mock_open, read_data='{"payload": {"documentId": "test"}}')
    def test_extract_document_success(self, mock_file, mock_save_event, mock_save_content, mock_extract):
        """Test complete document extraction process."""
        mock_broker = Mock()

        # Mock extraction result
        mock_extract.return_value = {
            "text_extracted": True,
            "page_count": 10,
            "pages": [{"page": 1, "text": "content"}],
            "metadata": {"title": "Test", "author": "Author"},
            "extraction_method": "pdfplumber",
        }

        mock_save_content.return_value = "/tmp/storage/test/pages.jsonl"

        service = ExtractionService(event_broker=mock_broker, storage_path="/tmp/storage")

        event = {
            "correlationId": "corr-123",
            "payload": {
                "documentId": "test-doc",
                "url": "/app/pdfs/test.pdf",
                "title": "Test Document",
                "originalUrl": "https://example.com/test.pdf",
            },
        }

        result = service.extract_document(event)

        # Should return DocumentExtracted event
        assert result["eventType"] == "DocumentExtracted"
        assert result["payload"]["documentId"] == "test-doc"
        assert result["payload"]["pageCount"] == 10

    @patch("extraction_service.ExtractionService._extract_pdf_content")
    def test_handle_document_discovered_event_error(self, mock_extract):
        """Test error handling during extraction."""
        mock_broker = Mock()
        mock_extract.side_effect = Exception("PDF corrupted")

        service = ExtractionService(event_broker=mock_broker, storage_path="/tmp/storage")

        event = {
            "correlationId": "corr-123",
            "payload": {"documentId": "test-doc", "url": "/app/pdfs/test.pdf", "title": "Test Document"},
        }

        result = service.handle_document_discovered_event(event)

        # Should return None on error
        assert result is None
        # Should publish failure event
        assert mock_broker.publish.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
