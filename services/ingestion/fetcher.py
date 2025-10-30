import logging
import requests
import hashlib
from pathlib import Path
from typing import Optional, Dict

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
        Download a PDF from the given URL. Returns a dictionary with file information.
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
