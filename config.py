"""
Configuration management for the scraper module.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for the web scraper and vector store."""

    # API Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")

    # ChromaDB settings
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

    # Scraper settings
    SCRAPER_USER_AGENT: str = os.getenv(
        "SCRAPER_USER_AGENT", "TaoReserve-Bot/1.0"
    )
    SCRAPER_TIMEOUT: int = int(os.getenv("SCRAPER_TIMEOUT", "30"))
    SCRAPER_MAX_PAGES: int = int(os.getenv("SCRAPER_MAX_PAGES", "100"))

    # Embedding settings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    EMBEDDING_DIMENSION: int = 3072  # Gemini embedding dimension

    # Chunking settings
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 128

    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is required. Set it in .env file or environment variable.\n"
                "Get one from: https://makersuite.google.com/app/apikey"
            )

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        Path(cls.CHROMA_PERSIST_DIR).parent.mkdir(parents=True, exist_ok=True)
        Path(cls.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
