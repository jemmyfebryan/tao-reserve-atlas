"""
Web scraper and vector store module for building RAG knowledge bases.

This module provides tools to scrape websites, process content, and store
embeddings in a local vector database for retrieval-augmented generation.

Example usage as a library:
    from scraper import WebScraper, VectorStore

    # Scrape a website
    scraper = WebScraper()
    documents = scraper.scrape_url("https://example.com")

    # Store in vector database
    store = VectorStore(collection_name="my_knowledge")
    store.add_documents(documents)

    # Query
    results = store.query("What is this about?")
"""
from scraper.web_scraper import WebScraper
from scraper.vector_store import VectorStore
from scraper.document_processor import DocumentProcessor

__all__ = ["WebScraper", "VectorStore", "DocumentProcessor"]
