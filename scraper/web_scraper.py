"""
Web scraper for extracting content from websites.
"""
import re
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from scraper.document_processor import DocumentProcessor
from config import Config


class WebScraper:
    """Scraper for extracting and processing web content."""

    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout: Optional[int] = None,
        max_pages: Optional[int] = None,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
    ):
        """
        Initialize the web scraper.

        Args:
            user_agent: User agent string for requests
            timeout: Request timeout in seconds
            max_pages: Maximum number of pages to scrape
            chunk_size: Text chunk size for processing
            chunk_overlap: Overlap between chunks
        """
        self.user_agent = user_agent or Config.SCRAPER_USER_AGENT
        self.timeout = timeout or Config.SCRAPER_TIMEOUT
        self.max_pages = max_pages or Config.SCRAPER_MAX_PAGES
        self.processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Session for persistent connections
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

        # Track visited URLs to avoid duplicates
        self.visited_urls: Set[str] = set()

    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """
        Check if URL is valid and belongs to the same domain.

        Args:
            url: URL to check
            base_domain: Base domain to match against

        Returns:
            True if URL should be scraped
        """
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_domain)

            # Must be http/https
            if parsed.scheme not in ["http", "https"]:
                return False

            # Must be same domain (or subdomain)
            if (
                parsed.netloc != base_parsed.netloc
                and not parsed.netloc.endswith(f".{base_parsed.netloc}")
            ):
                return False

            # Skip common file extensions
            skip_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".zip", ".exe"}
            if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
                return False

            return True
        except Exception:
            return False

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract all links from HTML content.

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links

        Returns:
            List of absolute URLs
        """
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)

        return links

    def scrape_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single page.

        Args:
            url: URL to scrape

        Returns:
            Dictionary with url, title, and html_content, or None if failed
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_tag = soup.find("title")
            title = title_tag.get_text() if title_tag else url

            # Get HTML content
            html_content = str(soup)

            return {
                "url": url,
                "title": title.strip(),
                "html_content": html_content,
            }

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def scrape_url(
        self,
        url: str,
        recursive: bool = False,
        max_depth: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Scrape a URL (optionally recursively).

        Args:
            url: URL to scrape
            recursive: Whether to follow links recursively
            max_depth: Maximum depth for recursive scraping

        Returns:
            List of processed document chunks
        """
        print(f"Scraping: {url}")

        all_chunks = []
        pages_to_scrape = [(url, 0)]  # (url, depth)
        self.visited_urls.clear()

        base_domain = url

        with tqdm(total=self.max_pages, desc="Scraping pages") as pbar:
            while pages_to_scrape and len(self.visited_urls) < self.max_pages:
                current_url, depth = pages_to_scrape.pop(0)

                # Skip if already visited or invalid
                if current_url in self.visited_urls:
                    continue

                if not self.is_valid_url(current_url, base_domain):
                    continue

                # Mark as visited
                self.visited_urls.add(current_url)

                # Scrape the page
                page_data = self.scrape_page(current_url)
                if not page_data:
                    pbar.update(1)
                    continue

                # Process the document
                chunks = self.processor.process_document(
                    html_content=page_data["html_content"],
                    url=page_data["url"],
                    title=page_data["title"],
                    depth=depth,
                )

                all_chunks.extend(chunks)
                pbar.update(1)
                pbar.set_postfix({"chunks": len(all_chunks), "url": current_url[:40]})

                # Follow links if recursive
                if recursive and depth < max_depth:
                    links = self.extract_links(page_data["html_content"], current_url)
                    for link in links:
                        if link not in self.visited_urls:
                            pages_to_scrape.append((link, depth + 1))

        print(f"\nScraped {len(self.visited_urls)} pages, generated {len(all_chunks)} chunks")
        return all_chunks

    def scrape_multiple_urls(
        self,
        urls: List[str],
        recursive: bool = False,
        max_depth: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs.

        Args:
            urls: List of URLs to scrape
            recursive: Whether to follow links recursively
            max_depth: Maximum depth for recursive scraping

        Returns:
            List of all processed document chunks
        """
        all_chunks = []

        for url in urls:
            # Clear visited URLs for each new base URL
            self.visited_urls.clear()
            chunks = self.scrape_url(url, recursive=recursive, max_depth=max_depth)
            all_chunks.extend(chunks)

        return all_chunks

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
