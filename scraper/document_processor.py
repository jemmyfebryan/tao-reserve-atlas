"""
Document processing utilities for cleaning and chunking web content.
"""
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import html2text


class DocumentProcessor:
    """Process and clean scraped web content."""

    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 128):
        """
        Initialize the document processor.

        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0  # Don't wrap lines

    def clean_html(self, html_content: str) -> str:
        """
        Clean HTML content and convert to markdown.

        Args:
            html_content: Raw HTML content

        Returns:
            Cleaned markdown text
        """
        # Parse with BeautifulSoup to remove scripts, styles, etc.
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Convert to markdown
        cleaned_content = self.html_converter.handle(str(soup))

        # Remove excessive whitespace
        cleaned_content = re.sub(r"\n\s*\n", "\n\n", cleaned_content)
        cleaned_content = cleaned_content.strip()

        return cleaned_content

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap.

        Args:
            text: The text to chunk
            metadata: Metadata to attach to each chunk

        Returns:
            List of document chunks with metadata
        """
        if not text or len(text) <= self.chunk_size:
            return [{"text": text, "metadata": metadata}]

        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                sentence_end = text.rfind(". ", start, end)
                if sentence_end == -1:
                    sentence_end = text.rfind("\n", start, end)
                if sentence_end != -1 and sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 2

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_id": chunk_id,
                    "start_char": start,
                    "end_char": end,
                })

                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })
                chunk_id += 1

            start = end - self.chunk_overlap

        return chunks

    def process_document(
        self,
        html_content: str,
        url: str,
        title: str = "",
        **additional_metadata
    ) -> List[Dict[str, Any]]:
        """
        Process a document: clean HTML and chunk content.

        Args:
            html_content: Raw HTML content
            url: URL of the document
            title: Document title
            **additional_metadata: Additional metadata to attach

        Returns:
            List of document chunks
        """
        # Clean HTML
        cleaned_text = self.clean_html(html_content)

        if not cleaned_text:
            return []

        # Prepare metadata
        metadata = {
            "url": url,
            "title": title or url,
            "source": "web_scraper",
        }
        metadata.update(additional_metadata)

        # Chunk the text
        chunks = self.chunk_text(cleaned_text, metadata)

        return chunks
