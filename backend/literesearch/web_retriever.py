# backend/literesearch/web_retriever.py

import os
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from tavily import TavilyClient
from duckduckgo_search import DDGS

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


class TavilyAPIError(Exception):
    """Tavily API related error"""
    pass


class ScrapingError(Exception):
    """Web scraping related error"""
    pass


class TavilySearch:
    """Tavily Search API"""

    def __init__(
        self, query: str, headers: Dict[str, str] = None, topic: str = "general"
    ):
        self.query = query
        self.headers = headers or {}
        self.client = TavilyClient(api_key=self._get_api_key())
        self.topic = topic

    def _get_api_key(self) -> str:
        """
        Get Tavily API key

        :return: API key
        :raises TavilyAPIError: If API key is not found
        """
        api_key = self.headers.get("tavily_api_key") or os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise TavilyAPIError("Tavily API key not found. Please set TAVILY_API_KEY environment variable.")
        return api_key

    def search(self, max_results: int = 7) -> List[Dict[str, str]]:
        """
        Execute search

        :param max_results: Maximum number of results
        :return: List of search results
        """
        try:
            results = self.client.search(
                self.query,
                search_depth="basic",
                max_results=max_results,
                topic=self.topic,
            )
            sources = results.get("results", [])
            if not sources:
                raise TavilyAPIError("Tavily API search found no results.")
            return [{"href": obj["url"], "body": obj["content"]} for obj in sources]
        except TavilyAPIError:
            raise  # Re-raise Tavily-specific errors
        except Exception as e:
            print(f"Tavily search error: {e}. Falling back to DuckDuckGo search API...")
            try:
                ddg = DDGS()
                results = list(
                    ddg.text(self.query, region="wt-wt", max_results=max_results)
                )
                if not results:
                    print("DuckDuckGo search also found no results.")
                return results
            except Exception as ddg_error:
                print(f"DuckDuckGo search error: {ddg_error}. Failed to retrieve sources. Returning empty response.")
                return []


def get_retriever(retriever: str):
    """
    Get retriever

    :param retriever: Retriever name
    :return: Retriever class
    """
    return TavilySearch if retriever == "tavily" else TavilySearch


def get_default_retriever():
    """
    Get default retriever

    :return: Default retriever class
    """
    return TavilySearch


class BeautifulSoupScraper:
    """Web scraper using BeautifulSoup"""

    def __init__(self, link: str, session: requests.Session = None, config=None):
        """
        Initialize scraper

        :param link: URL to scrape
        :param session: Request session
        :param config: Configuration object
        """
        self.link = link
        self.session = session or requests.Session()
        self.config = config

    def scrape(self) -> str:
        """
        Scrape web content

        :return: Scraped content
        :raises ScrapingError: Raised when scraping fails
        """
        try:
            timeout = self.config.DEFAULT_TIMEOUT if self.config else 4
            response = self.session.get(self.link, timeout=timeout)
            response.raise_for_status()  # Check for HTTP errors
            # Skip PDF or non-HTML resources if encountered
            content_type = response.headers.get("Content-Type", "").lower()
            if "application/pdf" in content_type:
                return ""
            
            soup = BeautifulSoup(
                response.content, "lxml", from_encoding=response.encoding
            )

            for script_or_style in soup(["script", "style"]):
                script_or_style.extract()

            raw_content = self._get_content_from_url(soup)
            lines = (line.strip() for line in raw_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return "\n".join(chunk for chunk in chunks if chunk)

        except requests.exceptions.RequestException as e:
            print(f"Network request error {self.link}: {str(e)}")
            return ""
        except Exception as e:
            print(f"Error scraping {self.link}: {str(e)}")
            return ""

    def _get_content_from_url(self, soup: BeautifulSoup) -> str:
        """
        Extract content from BeautifulSoup object

        :param soup: BeautifulSoup object
        :return: Extracted text content
        """
        text = ""
        tags = ["p", "h1", "h2", "h3", "h4", "h5"]
        for element in soup.find_all(tags):
            text += element.text + "\n"
        return text


class Scraper:
    """Web scraper"""

    def __init__(
        self, urls: List[str], user_agent: str, config=None, scraper_class=BeautifulSoupScraper
    ):
        """
        Initialize scraper

        :param urls: List of URLs to scrape
        :param user_agent: User agent string
        :param config: Configuration object
        :param scraper_class: Scraper class to use
        """
        self.urls = urls
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.scraper_class = scraper_class
        self.config = config

    def run(self) -> List[Dict[str, Any]]:
        """
        Execute scraping tasks

        :return: List of scraping results
        """
        partial_extract = partial(self._extract_data_from_link, session=self.session)
        max_workers = self.config.DEFAULT_MAX_WORKERS if self.config else 20
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            contents = executor.map(partial_extract, self.urls)
        return [content for content in contents if content["raw_content"] is not None]

    def _extract_data_from_link(
        self, link: str, session: requests.Session
    ) -> Dict[str, Any]:
        """
        Extract data from link

        :param link: URL to scrape
        :param session: Request session
        :return: Dictionary containing scraping results
        """
        try:
            scraper = self.scraper_class(link, session, self.config)
            content = scraper.scrape()

            min_length = self.config.MIN_CONTENT_LENGTH if self.config else 100
            if len(content) < min_length:
                return {"url": link, "raw_content": None}
            return {"url": link, "raw_content": content}
        except Exception as e:
            print(f"Error extracting data from {link}: {str(e)}")
            return {"url": link, "raw_content": None}


def scrape_urls(urls: List[str], cfg: Any) -> List[Dict[str, Any]]:
    """
    Scrape multiple URLs

    :param urls: List of URLs to scrape
    :param cfg: Configuration object
    :return: List of scraping results
    """
    scraper = Scraper(urls, cfg.user_agent, cfg)
    return scraper.run()


class SearchAPIRetriever(BaseRetriever):
    """Search API retriever"""

    pages: List[Dict[str, Any]] = []

    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Get relevant documents

        :param query: Query string
        :return: List of relevant documents
        """
        return [
            Document(
                page_content=page.get("raw_content", ""),
                metadata={
                    "title": page.get("title", ""),
                    "source": page.get("url", ""),
                },
            )
            for page in self.pages
        ]


class ContextCompressor:
    """Context compressor"""

    def __init__(
        self,
        documents: List[Dict[str, Any]],
        embeddings: Any,
        max_results: int = 5,
        **kwargs,
    ):
        """
        Initialize context compressor

        :param documents: List of documents
        :param embeddings: Embedding model
        :param max_results: Maximum number of results
        :param kwargs: Other parameters
        """
        self.max_results = max_results
        self.documents = documents
        self.kwargs = kwargs
        self.embeddings = embeddings
        self.similarity_threshold = float(os.environ.get("SIMILARITY_THRESHOLD", 0.38))

    def get_contextual_retriever(self) -> ContextualCompressionRetriever:
        """
        Get contextual compression retriever

        :return: Contextual compression retriever
        """
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        relevance_filter = EmbeddingsFilter(
            embeddings=self.embeddings, similarity_threshold=self.similarity_threshold
        )
        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[splitter, relevance_filter]
        )
        base_retriever = SearchAPIRetriever()
        base_retriever.pages = self.documents
        return ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=base_retriever
        )

    def pretty_print_docs(self, docs: List[Document], top_n: int) -> str:
        """
        Pretty print documents

        :param docs: List of documents
        :param top_n: Number of top documents to print
        :return: Formatted document string
        """
        return "\n".join(
            f"Source: {d.metadata.get('source')}\n"
            f"Title: {d.metadata.get('title')}\n"
            f"Content: {d.page_content}\n"
            for i, d in enumerate(docs)
            if i < top_n
        )

    async def get_context(self, query: str, max_results: int = 5) -> str:
        """
        Get context for query

        :param query: Query string
        :param max_results: Maximum number of results
        :return: Compressed context string
        """
        compressed_docs = self.get_contextual_retriever()
        relevant_docs = compressed_docs.invoke(query)
        return self.pretty_print_docs(relevant_docs, max_results)
