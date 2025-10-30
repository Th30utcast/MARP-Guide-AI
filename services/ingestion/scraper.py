import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class MARPScraper:

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def discover_pdfs(self) -> List[Dict[str, str]]:
        """
        Scrape the MARP website and discover all PDF links. Returns dictionary containing PDF metadata.
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
