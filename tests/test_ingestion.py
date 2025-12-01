"""
Tests for Ingestion Service.

What this tests:
- PDF scraping logic works
- Document ID extraction from URLs
- Event creation and publishing
- File download logic
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services" / "ingestion"))

from ingestion_service import IngestionService, MARPScraper, PDFFetcher


class TestMARPScraper:
    """Test the web scraping functionality."""

    @patch("ingestion_service.requests.Session")
    def test_discover_pdfs_success(self, mock_session):
        """Test successful PDF discovery."""
        # Mock HTML response
        mock_response = Mock()
        mock_response.content = b"""
        <html>
            <body>
                <a href="https://example.com/test.pdf">Test PDF</a>
                <a href="/relative/path.pdf">Another PDF</a>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()

        mock_session.return_value.get.return_value = mock_response

        scraper = MARPScraper("https://example.com/marp")
        pdfs = scraper.discover_pdfs()

        # Should find 2 PDFs
        assert len(pdfs) == 2
        assert pdfs[0]["title"] == "Test PDF"
        assert "test.pdf" in pdfs[0]["url"]

    @patch("ingestion_service.requests.Session")
    def test_discover_pdfs_handles_errors(self, mock_session):
        """Test error handling during scraping."""
        mock_session.return_value.get.side_effect = Exception("Network error")

        scraper = MARPScraper("https://example.com/marp")

        with pytest.raises(Exception):
            scraper.discover_pdfs()


class TestPDFFetcher:
    """Test PDF downloading functionality."""

    @patch("ingestion_service.requests.Session")
    @patch("builtins.open", new_callable=mock_open)
    @patch("ingestion_service.Path.mkdir")
    def test_fetch_pdf_success(self, mock_mkdir, mock_file, mock_session):
        """Test successful PDF download."""
        # Mock PDF content
        pdf_content = b"%PDF-1.4 fake pdf content"
        mock_response = Mock()
        mock_response.iter_content.return_value = [pdf_content]
        mock_response.raise_for_status = Mock()

        mock_session.return_value.get.return_value = mock_response

        fetcher = PDFFetcher("/tmp/pdfs")
        result = fetcher.fetch_pdf("https://example.com/test.pdf", "test-doc")

        # Should return file info
        assert result is not None
        assert "file_path" in result
        assert "file_size" in result
        assert "checksum" in result
        assert result["file_size"] == len(pdf_content)

    @patch("ingestion_service.Path.exists")
    def test_file_exists_check(self, mock_exists):
        """Test checking if PDF already exists."""
        mock_exists.return_value = True

        fetcher = PDFFetcher("/tmp/pdfs")
        exists = fetcher.file_exists("test-doc")

        assert exists is True


class TestIngestionService:
    """Test the main ingestion service."""

    def test_extract_document_id_from_url(self):
        """Test document ID extraction from URL."""
        mock_broker = Mock()

        service = IngestionService(
            event_broker=mock_broker, base_url="https://example.com", pdf_output_dir="/tmp/pdfs", storage_path="/tmp/storage"
        )

        # Test various URL formats
        doc_id = service._extract_document_id_from_url("https://example.com/docs/Academic-Appeals.pdf")
        assert doc_id == "Academic-Appeals"

        doc_id = service._extract_document_id_from_url("https://example.com/General-Regs.pdf")
        assert doc_id == "General-Regs"

    @patch("builtins.open", new_callable=mock_open)
    @patch("ingestion_service.Path.mkdir")
    def test_save_discovered_event(self, mock_mkdir, mock_file):
        """Test saving discovered event to disk."""
        mock_broker = Mock()

        service = IngestionService(
            event_broker=mock_broker, base_url="https://example.com", pdf_output_dir="/tmp/pdfs", storage_path="/tmp/storage"
        )

        event = {"eventType": "DocumentDiscovered", "payload": {"documentId": "test-doc"}}

        service._save_discovered_event("test-doc", event)

        # Should write to file
        mock_file.assert_called()

    @patch("ingestion_service.IngestionService._process_pdf")
    @patch("ingestion_service.MARPScraper.discover_pdfs")
    def test_run_ingestion_success(self, mock_discover, mock_process):
        """Test successful ingestion run."""
        mock_broker = Mock()

        # Mock discovered PDFs
        mock_discover.return_value = [{"title": "Test PDF", "url": "https://example.com/test.pdf"}]

        # Mock successful processing
        mock_process.return_value = {"status": "published", "document_id": "test-doc", "title": "Test PDF"}

        service = IngestionService(
            event_broker=mock_broker, base_url="https://example.com", pdf_output_dir="/tmp/pdfs", storage_path="/tmp/storage"
        )

        result = service.run_ingestion()

        assert result["status"] == "completed"
        assert result["discovered"] == 1
        assert result["published"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
