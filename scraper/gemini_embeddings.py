"""
Custom Gemini Embeddings wrapper for llama-index.
"""
from typing import List
from llama_index.core.embeddings import BaseEmbedding
import google.generativeai as genai
from config import Config


class GeminiEmbedding(BaseEmbedding):
    """
    Custom embedding class using Google Gemini API.
    """

    def __init__(
        self,
        model_name: str = "models/text-embedding-004",
        api_key: str = None,
        **kwargs
    ):
        """
        Initialize Gemini embeddings.

        Args:
            model_name: The embedding model to use
            api_key: Google API key
        """
        super().__init__(**kwargs)
        self.model_name = model_name
        api_key = api_key or Config.GEMINI_API_KEY
        genai.configure(api_key=api_key)

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for a query string."""
        return self._get_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a text string."""
        return self._get_embedding(text)

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        return [self._get_embedding(text) for text in texts]

    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text using Gemini API.

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document",
            )
            return result["embedding"]
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero embedding on error
            return [0.0] * 768

    def _get_query_embeddings(self, queries: List[str]) -> List[List[float]]:
        """Get embeddings for multiple queries."""
        return [self._get_embedding(query) for query in queries]

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """Async get embedding for a query."""
        return self._get_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Async get embedding for text."""
        return self._get_embedding(text)
