# backend/literesearch/literesearch_agent.py

import json
import asyncio
from typing import List, Dict, Tuple, Any, Optional
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_fixed

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from backend.literesearch.literesearch_config import Config
from backend.literesearch.research_prompts import (
    auto_agent_instructions,
    generate_search_queries_prompt,
    get_report_by_type,
    generate_report_introduction_prompt,
    generate_subtopics_prompt,
)
from backend.literesearch.web_retriever import (
    get_retriever,
    get_default_retriever,
    scrape_urls,
    ContextCompressor,
)
from backend.literesearch.research_enums import ReportType, ReportSource, Tone
from backend.literesearch.embedding_service import Memory
from utils.llm_tools import init_language_model
from utils.langfuse_tools import get_langfuse_config


class AgentResponse(BaseModel):
    """AI agent response model"""

    server: str = Field(
        ..., description="Server type determined by topic domain, associated with corresponding emoji."
    )
    agent_role_prompt: str = Field(
        ..., description="Specific instructions based on agent role and expertise."
    )


class Subtopic(BaseModel):
    """Subtopic model"""

    task: str = Field(description="Task name", min_length=1)


class Subtopics(BaseModel):
    """Subtopics list model"""

    subtopics: List[Subtopic] = []


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def choose_agent(
    query: str, cfg: Config, session_id: Optional[str] = None
) -> Tuple[str, str]:
    """
    Choose appropriate AI agent for query

    :param query: Query string
    :param cfg: Configuration object
    :param session_id: Optional session ID
    :return: Server type and agent role prompt
    """
    try:
        language_model = init_language_model(temperature=cfg.temperature)
        chat = language_model

        system_message = "{auto_agent_instructions}"
        human_message = "task: {query}"

        parser = JsonOutputParser(pydantic_object=AgentResponse)

        format_instructions = """
Output your answer as a JSON object that conforms to the following schema:
```json
{schema}
```

Important instructions:
1. Wrap your entire response between ```json and ``` tags.
2. Ensure your JSON is valid and properly formatted.
3. Do not include the schema definition in your answer.
4. Only output the data instance that matches the schema.
5. Do not include any explanations or comments within the JSON output.
        """

        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_message + format_instructions),
                ("human", human_message),
            ]
        ).partial(
            auto_agent_instructions=auto_agent_instructions(),
            schema=AgentResponse.model_json_schema(),
        )

        chain = prompt_template | chat | parser

        # Get configuration using langfuse tools
        config = get_langfuse_config(
            trace_name="choose_agent",
            metadata={"query": query},
            session_id=session_id
        )
        
        agent_dict = await chain.ainvoke({"query": query}, config=config)

        return agent_dict["server"], agent_dict["agent_role_prompt"]
    except json.JSONDecodeError:
        print("Error parsing JSON. Using default agent.")
        return "Default Agent", (
            "You are an AI critical thinking research assistant. Your sole purpose is to write well-structured, "
            "critical, and objective reports on given text."
        )


async def get_sub_queries(
    query: str,
    agent_role_prompt: str,
    cfg: Config,
    parent_query: Optional[str],
    report_type: str,
    session_id: Optional[str] = None
) -> List[str]:
    """
    Generate sub-queries

    :param query: Main query
    :param agent_role_prompt: Agent role prompt
    :param cfg: Configuration object
    :param parent_query: Parent query
    :param report_type: Report type
    :param session_id: Optional session ID
    :return: List of sub-queries
    """
    language_model = init_language_model(temperature=cfg.temperature)
    chat = language_model

    system_message = f"{agent_role_prompt}\n\n"

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            (
                "human",
                generate_search_queries_prompt(
                    query, parent_query, report_type, max_iterations=cfg.max_iterations
                ),
            ),
        ]
    )

    messages = prompt.format_messages(question=query)
    
    # Get configuration using langfuse tools
    config = get_langfuse_config(
        trace_name="get_sub_queries",
        metadata={
            "query": query,
            "report_type": report_type,
            "parent_query": parent_query,
            "max_iterations": cfg.max_iterations
        },
        session_id=session_id
    )
    
    response = await chat.ainvoke(messages, config=config)

    try:
        sub_queries = json.loads(response.content)
        return sub_queries
    except json.JSONDecodeError:
        print("Error parsing JSON. Returning original query.")
        return [query]


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def construct_subtopics(
    task: str, data: str, config: Config, subtopics: List[Dict[str, str]] = [], session_id: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Construct subtopics

    :param task: Task
    :param data: Research data
    :param config: Configuration object
    :param subtopics: Existing subtopics list
    :param session_id: Optional session ID
    :return: Constructed subtopics list
    """
    try:
        parser = JsonOutputParser(pydantic_object=Subtopics)

        format_instructions = """
Output your answer as a JSON object that conforms to the following schema:
```json
{schema}
```

Important instructions:
1. Wrap your entire response between ```json and ``` tags.
2. Ensure your JSON is valid and properly formatted.
3. Do not include the schema definition in your answer.
4. Only output the data instance that matches the schema.
5. Do not include any explanations or comments within the JSON output.
        """

        prompt = ChatPromptTemplate.from_template(
            generate_subtopics_prompt() + format_instructions
        ).partial(schema=Subtopics.model_json_schema())

        language_model = init_language_model(temperature=config.temperature)
        chat = language_model

        chain = prompt | chat | parser

        # Get configuration using langfuse tools
        langfuse_config = get_langfuse_config(
            trace_name="construct_subtopics",
            metadata={
                "task": task,
                "max_subtopics": config.max_subtopics,
                "context_length": len(data)
            },
            session_id=session_id
        )

        output = await chain.ainvoke(
            {
                "task": task,
                "data": data,
                "subtopics": subtopics,
                "max_subtopics": config.max_subtopics,
            },
            config=langfuse_config
        )

        return output["subtopics"]

    except Exception as e:
        print("Exception occurred while parsing subtopics:", e)
        return subtopics


async def generate_report(
    query: str,
    context: str,
    agent_role_prompt: str,
    report_type: str,
    tone: Tone,
    report_source: str,
    cfg: Config,
    websocket: Any = None,
    main_topic: str = "",
    existing_headers: List[str] = [],
    session_id: Optional[str] = None,
) -> str:
    """
    Generate report

    :param query: Query
    :param context: Context
    :param agent_role_prompt: Agent role prompt
    :param report_type: Report type
    :param tone: Tone
    :param report_source: Report source
    :param cfg: Configuration object
    :param websocket: WebSocket object (optional)
    :param main_topic: Main topic (optional)
    :param existing_headers: Existing headers list (optional)
    :param session_id: Optional session ID
    :return: Generated report
    """
    generate_prompt = get_report_by_type(report_type)

    if report_type == "subtopic_report":
        content = generate_prompt(
            query,
            existing_headers,
            main_topic,
            context,
            report_format=cfg.report_format,
            total_words=cfg.total_words,
        )
    else:
        content = generate_prompt(
            query,
            context,
            report_source,
            report_format=cfg.report_format,
            total_words=cfg.total_words,
        )

    if tone:
        content += f", tone={tone.value}"

    language_model = init_language_model(temperature=cfg.temperature)
    chat = language_model

    messages = [
        {"role": "system", "content": f"{agent_role_prompt}"},
        {"role": "user", "content": content},
    ]

    # Get configuration using langfuse tools
    config = get_langfuse_config(
        trace_name="generate_report",
        metadata={
            "query": query,
            "report_type": report_type,
            "tone": tone.value if tone else None,
            "main_topic": main_topic,
            "context_length": len(context)
        },
        session_id=session_id
    )

    response = await chat.ainvoke(messages, config=config)

    return response.content


async def get_report_introduction(
    query: str,
    context: str,
    role: str,
    config: Config,
    websocket: Any = None,
    session_id: Optional[str] = None,
) -> str:
    """
    Get report introduction

    :param query: Query
    :param context: Context
    :param role: Role
    :param config: Configuration object
    :param websocket: WebSocket object (optional)
    :param session_id: Optional session ID
    :return: Generated report introduction
    """
    language_model = init_language_model(temperature=config.temperature)
    chat = language_model

    prompt = generate_report_introduction_prompt(query, context)

    messages = [
        {"role": "system", "content": f"{role}"},
        {"role": "user", "content": prompt},
    ]

    # Get configuration using langfuse tools
    langfuse_config = get_langfuse_config(
        trace_name="get_report_introduction",
        metadata={
            "query": query,
            "role": role,
            "context_length": len(context)
        },
        session_id=session_id
    )

    response = await chat.ainvoke(messages, config=langfuse_config)

    return response.content


# Test functions have been moved to separate test files
