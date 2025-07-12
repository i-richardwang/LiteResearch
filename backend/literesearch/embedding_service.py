# backend/literesearch/embedding_service.py
import os
from typing import List, Optional
from langchain.embeddings.base import Embeddings
from utils.llm_tools import CustomEmbeddings


class Memory:
    """Memory class for managing and retrieving embedding models"""

    def __init__(
        self, embedding_provider: str, headers: Optional[dict] = None, **kwargs
    ):
        """
        Initialize Memory class

        :param embedding_provider: Name of the embedding provider
        :param headers: Optional HTTP headers
        :param kwargs: Other optional parameters
        :raises ValueError: Raised when embedding provider is not supported
        """
        self._embeddings = None
        headers = headers or {}

        if embedding_provider == "openai":
            self._embeddings = CustomEmbeddings(
                api_key=os.getenv("EMBEDDING_API_KEY", ""),
                api_url=os.getenv("EMBEDDING_API_BASE", ""),
                model=os.getenv("EMBEDDING_MODEL", ""),
            )
        else:
            raise ValueError("Unsupported embedding provider.")

    def get_embeddings(self) -> Embeddings:
        """
        Get embedding model

        :return: Embedding model instance
        """
        return self._embeddings
