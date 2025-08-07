# backend/literesearch/embedding_service.py
from typing import Optional
from langchain.embeddings.base import Embeddings
from utils.llm_tools import init_embeddings


class Memory:
    """Memory class for managing and retrieving embedding models"""

    def __init__(self, **kwargs):
        """
        Initialize Memory class with OpenAI embeddings
        
        :param kwargs: Optional parameters (kept for compatibility)
        """
        # Use the same OPENAI_API_KEY and OPENAI_BASE_URL as the LLM
        self._embeddings = init_embeddings()

    def get_embeddings(self) -> Embeddings:
        """
        Get embedding model

        :return: Embedding model instance
        """
        return self._embeddings
