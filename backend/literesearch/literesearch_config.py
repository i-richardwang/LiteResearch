# literesearch_config.py

import os
from typing import Optional

# Initialize Langfuse
import langfuse

# Import constants
from backend.literesearch.constants import (
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TEMPERATURE,
    DEFAULT_USER_AGENT,
    DEFAULT_MAX_SEARCH_RESULTS_PER_QUERY,
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
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", str(DEFAULT_SIMILARITY_THRESHOLD)))
        self.temperature = float(os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE)))
        self.user_agent = os.getenv("USER_AGENT", DEFAULT_USER_AGENT)
        self.max_search_results_per_query = int(
            os.getenv("MAX_SEARCH_RESULTS_PER_QUERY", str(DEFAULT_MAX_SEARCH_RESULTS_PER_QUERY))
        )
        self.total_words = int(os.getenv("TOTAL_WORDS", str(DEFAULT_TOTAL_WORDS)))
        self.report_format = os.getenv("REPORT_FORMAT", DEFAULT_REPORT_FORMAT)
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", str(DEFAULT_MAX_ITERATIONS)))
        self.scraper = os.getenv("SCRAPER", DEFAULT_SCRAPER)
        self.max_subtopics = int(os.getenv("MAX_SUBTOPICS", str(DEFAULT_MAX_SUBTOPICS)))
        self.llm_kwargs = {}

        # Constants definition
        self.DEFAULT_CONCURRENCY_LIMIT = DEFAULT_CONCURRENCY_LIMIT
        self.MIN_CONTENT_LENGTH = MIN_CONTENT_LENGTH
        self.DEFAULT_TIMEOUT = DEFAULT_TIMEOUT
        self.DEFAULT_MAX_WORKERS = DEFAULT_MAX_WORKERS

        # Initialize langfuse
        self._init_langfuse()



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
