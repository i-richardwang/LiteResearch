# backend/literesearch/embedding_service.py
import os
from langchain_core.embeddings import Embeddings
from utils.llm_tools import init_embeddings


class Memory:
    """Memory class for managing and retrieving embedding models"""

    def __init__(self, **kwargs):
        """
        Initialize Memory class with OpenAI embeddings
        
        :param kwargs: Optional parameters (kept for compatibility)
        """
        # Configure official batch size via OpenAIEmbeddings chunk_size
        chunk_size = int(os.environ.get("EMBEDDING_MAX_BATCH_SIZE", "64"))
        self._embeddings = init_embeddings(chunk_size=chunk_size)

    def get_embeddings(self) -> Embeddings:
        """
        Get embedding model

        :return: Embedding model instance
        """
        return self._embeddings
