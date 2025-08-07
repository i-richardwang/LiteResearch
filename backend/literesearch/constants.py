"""
Lite Research Constants
Contains all constants and magic numbers used in the project
"""

# Network request related constants
DEFAULT_TIMEOUT = 4
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"

# Concurrency and performance related constants
DEFAULT_CONCURRENCY_LIMIT = 5
DEFAULT_MAX_WORKERS = 20
MIN_CONTENT_LENGTH = 100

# Model and token related constants
DEFAULT_TEMPERATURE = 0.55

# Search and retrieval related constants
DEFAULT_MAX_SEARCH_RESULTS_PER_QUERY = 5
DEFAULT_MAX_ITERATIONS = 5
DEFAULT_MAX_SUBTOPICS = 5
DEFAULT_SIMILARITY_THRESHOLD = 0.38
DEFAULT_TOTAL_WORDS = 800

# Text processing constants
MIN_QUERY_LENGTH = 3

# Report format constants
DEFAULT_REPORT_FORMAT = "APA"

# Retriever related constants
DEFAULT_RETRIEVER = "tavily"
DEFAULT_SCRAPER = "bs"

# Langfuse related constants
DEFAULT_LANGFUSE_HOST = "https://cloud.langfuse.com"

# Validation limit constants
MAX_ITERATIONS_LIMIT = 10
MAX_SUBTOPICS_LIMIT = 10
MAX_SEARCH_RESULTS_LIMIT = 20
MIN_ITERATIONS = 1
MIN_SUBTOPICS = 1
MIN_SEARCH_RESULTS = 1 