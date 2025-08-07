# backend/literesearch/literesearcher.py

import asyncio
from typing import List, Dict, Any, Optional, Callable

from backend.literesearch.literesearch_config import Config
from backend.literesearch.research_enums import ReportType, ReportSource, Tone
from backend.literesearch.web_retriever import (
    get_retriever,
    get_default_retriever,
    scrape_urls,
    ContextCompressor,
)
from backend.literesearch.embedding_service import Memory
from backend.literesearch.literesearch_agent import (
    choose_agent,
    get_sub_queries,
    construct_subtopics,
    generate_report,
    get_report_introduction,
)
from utils.langfuse_tools import generate_session_id


class LiteResearcher:
    """Lite Research class"""

    def __init__(
        self,
        query: str,
        report_type: str = ReportType.ResearchReport.value,
        report_source: str = ReportSource.Web.value,
        tone: Tone = Tone.Objective,
        config_path: Optional[str] = None,
        websocket: Any = None,
        agent: Optional[str] = None,
        role: Optional[str] = None,
        verbose: bool = True,
        verbose_callback: Optional[Callable[[str], None]] = None,
        max_iterations: Optional[int] = None,
        max_subtopics: Optional[int] = None,
        max_search_results_per_query: Optional[int] = None,
    ):
        """
        Initialize Lite Research

        :param query: Research query
        :param report_type: Report type
        :param report_source: Report source
        :param tone: Report tone
        :param config_path: Configuration file path (optional)
        :param websocket: WebSocket object (optional)
        :param agent: Specified agent (optional)
        :param role: Specified role (optional)
        :param verbose: Whether to output verbosely
        :param verbose_callback: Verbose output callback function (optional)
        :param max_iterations: Maximum number of iterations (optional)
        :param max_subtopics: Maximum number of subtopics (optional)
        :param max_search_results_per_query: Maximum search results per query (optional)
        """
        # Input validation
        if not query or not query.strip():
            raise ValueError("Query content cannot be empty")
        
        self.query = query.strip()
        self.report_type = report_type
        self.report_source = report_source
        self.tone = tone
        self.cfg = Config(config_path)
        self.websocket = websocket
        self.agent = agent
        self.role = role
        self.verbose = verbose
        self.verbose_callback = verbose_callback
        self.context: List[str] = []
        self.memory = Memory()
        
        # Generate unique session ID for organizing the entire research workflow
        self.session_id = generate_session_id()

        # Update configuration
        if max_iterations is not None:
            self.cfg.max_iterations = max_iterations
        if max_subtopics is not None:
            self.cfg.max_subtopics = max_subtopics
        if max_search_results_per_query is not None:
            self.cfg.max_search_results_per_query = max_search_results_per_query

    def log(self, message: str) -> None:
        """
        Log information

        :param message: Message to log
        """
        if self.verbose:
            print(message)
            if self.verbose_callback:
                self.verbose_callback(message)

    async def process_sub_query(self, sub_query: str, index: int, total: int) -> str:
        """
        Process sub-query

        :param sub_query: Sub-query
        :param index: Current sub-query index
        :param total: Total number of sub-queries
        :return: Compressed context
        """
        self.log(f"Processing sub-query {index}/{total}: {sub_query}")

        retriever_class = get_retriever(self.cfg.retriever) or get_default_retriever()
        retriever = retriever_class(sub_query)
        self.log(f"Using retriever: {retriever.__class__.__name__}")

        search_results = retriever.search(
            max_results=self.cfg.max_search_results_per_query
        )

        urls = [result["href"] for result in search_results]
        self.log(f"Scraping {len(urls)} URLs for sub-query...")

        scraped_content = scrape_urls(urls, self.cfg)

        context_compressor = ContextCompressor(
            scraped_content, self.memory.get_embeddings()
        )
        self.log(f"Compressing context for sub-query...")

        compressed_context = await context_compressor.get_context(sub_query)
        self.log(f"Context compression completed for sub-query {index}/{total}.")

        return compressed_context

    async def conduct_research(self) -> List[str]:
        """
        Conduct research task

        :return: List of research contexts
        """
        self.log(f"🔎 Starting research task for '{self.query}'...")
        self.log(f"🎯 Research session ID: {self.session_id}")

        if not (self.agent and self.role):
            self.agent, self.role = await choose_agent(self.query, self.cfg, session_id=self.session_id)
        self.log(f"Selected agent: {self.agent}")

        sub_queries = await get_sub_queries(
            self.query, self.role, self.cfg, None, self.report_type, session_id=self.session_id
        )
        self.log(f"Generated sub-queries: {sub_queries}")

        self.log(f"Starting search and scraping for {len(sub_queries)} sub-queries...")

        # Use concurrency limit constant from configuration
        semaphore = asyncio.Semaphore(self.cfg.DEFAULT_CONCURRENCY_LIMIT)

        async def limited_process_sub_query(*args):
            async with semaphore:
                return await self.process_sub_query(*args)

        tasks = [
            limited_process_sub_query(sub_query, i + 1, len(sub_queries))
            for i, sub_query in enumerate(sub_queries)
        ]
        self.context = await asyncio.gather(*tasks)

        self.log(f"Research phase completed. Total contexts collected: {len(self.context)}")

        return self.context

    async def generate_report(self) -> str:
        """
        Generate research report

        :return: Generated report content
        """
        self.log("Starting report generation...")

        full_context = "\n".join(self.context)
        self.log(f"Merged context length: {len(full_context)} characters")

        if self.report_type == ReportType.DetailedReport.value:
            self.log("Generating detailed report...")

            self.log("Building subtopics...")
            subtopics = await construct_subtopics(self.query, full_context, self.cfg, session_id=self.session_id)
            self.log(f"Generated {len(subtopics)} subtopics")

            self.log("Generating report introduction...")
            introduction = await get_report_introduction(
                self.query, full_context, self.role, self.cfg, session_id=self.session_id
            )
            self.log("Introduction generated successfully")

            subtopic_reports = []
            for i, subtopic in enumerate(subtopics, 1):
                self.log(
                    f"Generating report for subtopic {i}/{len(subtopics)}: '{subtopic['task']}'"
                )
                subtopic_report = await generate_report(
                    subtopic["task"],
                    full_context,
                    self.role,
                    "subtopic_report",
                    self.tone,
                    self.report_source,
                    self.cfg,
                    main_topic=self.query,
                    existing_headers=[s["task"] for s in subtopics],
                    session_id=self.session_id,
                )
                subtopic_reports.append(subtopic_report)
                self.log(f"Report for subtopic {i} generated successfully")

            full_report = f"{introduction}\n\n" + "\n\n".join(subtopic_reports)
            self.log("Detailed report compilation completed")
        else:
            self.log(f"Generating {self.report_type} report...")
            full_report = await generate_report(
                self.query,
                full_context,
                self.role,
                self.report_type,
                self.tone,
                self.report_source,
                self.cfg,
                session_id=self.session_id,
            )
            self.log("Report generation completed")

        self.log(f"Final report length: {len(full_report)} characters")
        return full_report

    async def run(self) -> str:
        """
        Run Lite Research

        :return: Generated research report
        """
        await self.conduct_research()
        report = await self.generate_report()
        return report
