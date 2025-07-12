# literesearch_config.py

import os
from typing import Optional

# Initialize Langfuse
import langfuse

# Import constants
from backend.literesearch.constants import (
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_FAST_TOKEN_LIMIT,
    DEFAULT_SMART_TOKEN_LIMIT,
    DEFAULT_BROWSE_CHUNK_MAX_LENGTH,
    DEFAULT_SUMMARY_TOKEN_LIMIT,
    DEFAULT_TEMPERATURE,
    DEFAULT_USER_AGENT,
    DEFAULT_MAX_SEARCH_RESULTS_PER_QUERY,
    DEFAULT_MEMORY_BACKEND,
    DEFAULT_TOTAL_WORDS,
    DEFAULT_REPORT_FORMAT,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MAX_SUBTOPICS,
    DEFAULT_RETRIEVER,
    DEFAULT_SCRAPER,
    DEFAULT_LANGFUSE_HOST,
    DEFAULT_CONCURRENCY_LIMIT,
    MIN_CONTENT_LENGTH,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_WORKERS,
    DEFAULT_EMBEDDING_PROVIDER
)


class Config:
    """Lite Research configuration class"""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration

        :param config_file: Optional configuration file path
        :raises EnvironmentError: If required environment variables are not set
        """

        self.retriever = os.getenv("RETRIEVER", DEFAULT_RETRIEVER)
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", DEFAULT_EMBEDDING_PROVIDER)
        self.embedding_api_key = os.getenv("EMBEDDING_API_KEY", "")
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", str(DEFAULT_SIMILARITY_THRESHOLD)))
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4-1106-preview")
        self.fast_token_limit = int(os.getenv("FAST_TOKEN_LIMIT", str(DEFAULT_FAST_TOKEN_LIMIT)))
        self.smart_token_limit = int(os.getenv("SMART_TOKEN_LIMIT", str(DEFAULT_SMART_TOKEN_LIMIT)))
        self.browse_chunk_max_length = int(os.getenv("BROWSE_CHUNK_MAX_LENGTH", str(DEFAULT_BROWSE_CHUNK_MAX_LENGTH)))
        self.summary_token_limit = int(os.getenv("SUMMARY_TOKEN_LIMIT", str(DEFAULT_SUMMARY_TOKEN_LIMIT)))
        self.temperature = float(os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE)))
        self.user_agent = os.getenv("USER_AGENT", DEFAULT_USER_AGENT)
        self.max_search_results_per_query = int(
            os.getenv("MAX_SEARCH_RESULTS_PER_QUERY", str(DEFAULT_MAX_SEARCH_RESULTS_PER_QUERY))
        )
        self.memory_backend = os.getenv("MEMORY_BACKEND", DEFAULT_MEMORY_BACKEND)
        self.total_words = int(os.getenv("TOTAL_WORDS", str(DEFAULT_TOTAL_WORDS)))
        self.report_format = os.getenv("REPORT_FORMAT", DEFAULT_REPORT_FORMAT)
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", str(DEFAULT_MAX_ITERATIONS)))
        self.agent_role = os.getenv("AGENT_ROLE")
        self.scraper = os.getenv("SCRAPER", DEFAULT_SCRAPER)
        self.max_subtopics = int(os.getenv("MAX_SUBTOPICS", str(DEFAULT_MAX_SUBTOPICS)))
        self.doc_path = os.getenv("DOC_PATH", "")
        self.llm_kwargs = {}
        
        # Constants definition
        self.DEFAULT_CONCURRENCY_LIMIT = DEFAULT_CONCURRENCY_LIMIT
        self.MIN_CONTENT_LENGTH = MIN_CONTENT_LENGTH
        self.DEFAULT_TIMEOUT = DEFAULT_TIMEOUT
        self.DEFAULT_MAX_WORKERS = DEFAULT_MAX_WORKERS

        if self.doc_path:
            self.validate_doc_path()
            
        # Initialize langfuse
        self._init_langfuse()

    def validate_doc_path(self):
        """Validate and create document path"""
        os.makedirs(self.doc_path, exist_ok=True)

    def _init_langfuse(self):
        """
        Initialize Langfuse configuration
        """
        try:
            langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            langfuse_host = os.getenv("LANGFUSE_HOST", DEFAULT_LANGFUSE_HOST)
            
            if langfuse_secret_key and langfuse_public_key:
                langfuse.configure(
                    secret_key=langfuse_secret_key,
                    public_key=langfuse_public_key,
                    host=langfuse_host
                )
                print(f"✅ Langfuse initialized successfully with host: {langfuse_host}")
            else:
                print("⚠️  Langfuse keys not found in environment variables. Monitoring will be disabled.")
        except Exception as e:
            print(f"❌ Failed to initialize Langfuse: {e}")
