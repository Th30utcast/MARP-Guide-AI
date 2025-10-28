import logging
import requests
import hashlib
from pathlib import Path
from typing import Optional, Dict
import PyPDF2

logger = logging.getLogger(__name__)


class PDFFetcher:
    """Fetcher for downloading PDF files."""

    def __init__(self, output_dir: str = "/app/pdfs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_pdf(self, url: str, document_id: str) -> Optional[dict]:
        """
        Download a PDF from the given URL.

        Args:
            url: URL of the PDF to download
            document_id: Unique identifier for the document

        Returns:
            Dictionary with file info:
            {
                'file_path': '/app/pdfs/doc-123.pdf',
                'file_size': 1024567,
                'checksum': 'abc123...'
            }
            Returns None if download fails.
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

            # Extract PDF metadata
            pdf_metadata = self.extract_pdf_metadata(file_path)
            
            return {
                'file_path': str(file_path),
                'file_size': file_size,
                'checksum': checksum,
                'metadata': pdf_metadata
            }

        except requests.RequestException as e:
            logger.error(f"Error downloading PDF from {url}: {str(e)}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error downloading PDF: {str(e)}")
            return None

    def extract_pdf_metadata(self, file_path: str) -> Dict:
        """Extract metadata from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                return {
                    'title': metadata.get('/Title', 'Unknown') if metadata else 'Unknown',
                    'author': metadata.get('/Author', 'Unknown') if metadata else 'Unknown',
                    'subject': metadata.get('/Subject', 'Unknown') if metadata else 'Unknown',
                    'creator': metadata.get('/Creator', 'Unknown') if metadata else 'Unknown',
                    'producer': metadata.get('/Producer', 'Unknown') if metadata else 'Unknown',
                    'creation_date': str(metadata.get('/CreationDate', 'Unknown')) if metadata else 'Unknown',
                    'modification_date': str(metadata.get('/ModDate', 'Unknown')) if metadata else 'Unknown',
                    'page_count': len(pdf_reader.pages)
                }
        except Exception as e:
            logger.error(f"Error extracting PDF metadata from {file_path}: {e}")
            return {
                'title': 'Unknown',
                'author': 'Unknown', 
                'subject': 'Unknown',
                'creator': 'Unknown',
                'producer': 'Unknown',
                'creation_date': 'Unknown',
                'modification_date': 'Unknown',
                'page_count': 0
            }

    def file_exists(self, document_id: str) -> bool:
        """Check if PDF already exists locally."""
        filename = f"{document_id}.pdf"
        file_path = self.output_dir / filename
        return file_path.exists()
