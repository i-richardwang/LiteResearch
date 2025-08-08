import os
import time
import logging
import traceback
from typing import Any, Dict, List, Tuple, Optional, Type, Union
import requests

import pandas as pd
from tqdm import tqdm
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def init_language_model(
    temperature: float = 0.0,
    model_name: Optional[str] = None,
    **kwargs: Any,
) -> ChatOpenAI:
    """
    Initialize language model using standard LangChain environment variables.

    Args:
        temperature: Model output temperature, controlling randomness. Default is 0.0.
        model_name: Optional model name, uses LLM_MODEL environment variable if not provided.
        **kwargs: Other optional parameters, passed to model initialization.

    Returns:
        Initialized language model instance.

    Raises:
        ValueError: Raised when OPENAI_API_KEY environment variable is missing.
    """
    model_name = model_name or os.getenv("LLM_MODEL", "gpt-4")
    
    # LangChain will automatically read OPENAI_API_KEY and OPENAI_BASE_URL from environment
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. Please set it in your environment."
        )

    model_params = {
        "model": model_name,
        "temperature": temperature,
        **kwargs,
    }

    return ChatOpenAI(**model_params)


class LanguageModelChain:
    """
    Language model chain for processing input and generating output conforming to specified schema.

    Attributes:
        model_cls: Pydantic model class defining output structure.
        parser: JSON output parser.
        prompt_template: Chat prompt template.
        chain: Complete processing chain.
    """

    def __init__(
        self, model_cls: Type[BaseModel], sys_msg: str, user_msg: str, model: Any
    ):
        """
        Initialize LanguageModelChain instance.

        Args:
            model_cls: Pydantic model class defining output structure.
            sys_msg: System message.
            user_msg: User message.
            model: Language model instance.

        Raises:
            ValueError: Raised when provided parameters are invalid.
        """
        if not issubclass(model_cls, BaseModel):
            raise ValueError("model_cls must be a subclass of Pydantic BaseModel")
        if not isinstance(sys_msg, str) or not isinstance(user_msg, str):
            raise ValueError("sys_msg and user_msg must be string types")
        if not callable(model):
            raise ValueError("model must be callable")

        self.model_cls = model_cls
        self.parser = JsonOutputParser(pydantic_object=model_cls)

        format_instructions = """
Output your answer as a JSON object that conforms to the following schema:
```json
{schema}
```

Important instructions:
1. Ensure your JSON is valid and properly formatted.
2. Do not include the schema definition in your answer.
3. Only output the data instance that matches the schema.
4. Do not include any explanations or comments within the JSON output.
        """

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", sys_msg + format_instructions),
                ("human", user_msg),
            ]
        ).partial(schema=model_cls.model_json_schema())

        self.chain = self.prompt_template | model | self.parser

    def __call__(self) -> Any:
        """
        Call the processing chain.

        Returns:
            Output of the processing chain.
        """
        return self.chain


def init_embeddings(model_name: Optional[str] = None, **kwargs: Any) -> OpenAIEmbeddings:
    """
    Initialize OpenAI embeddings using standard LangChain environment variables.

    Args:
        model_name: Optional model name, uses EMBEDDING_MODEL environment variable if not provided.
        **kwargs: Other optional parameters, passed to embeddings initialization.

    Returns:
        Initialized OpenAI embeddings instance.

    Raises:
        ValueError: Raised when OPENAI_API_KEY environment variable is missing.
    """
    model_name = model_name or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Prefer dedicated embedding credentials/base when provided
    embedding_api_key = os.environ.get("EMBEDDING_API_KEY")
    embedding_api_base = os.environ.get("EMBEDDING_API_BASE") or os.environ.get("EMBEDDING_BASE_URL")

    # If dedicated credentials are not set, fall back to the general OpenAI-style envs
    api_key = embedding_api_key or os.environ.get("OPENAI_API_KEY")
    base_url = embedding_api_base or os.environ.get("OPENAI_BASE_URL")

    if not api_key:
        raise ValueError(
            "Embedding API key is required. Set EMBEDDING_API_KEY or fallback OPENAI_API_KEY."
        )

    # Build params; langchain_openai.OpenAIEmbeddings accepts api_key/base_url kwargs
    embedding_params: Dict[str, Any] = {
        "model": model_name,
        "api_key": api_key,
        **kwargs,
    }
    if base_url:
        embedding_params["base_url"] = base_url

    return OpenAIEmbeddings(**embedding_params)
