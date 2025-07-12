import os
import time
import logging
import traceback
from typing import Any, Dict, List, Tuple, Optional, Type, Union
import requests

import pandas as pd
from tqdm import tqdm
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.embeddings.base import Embeddings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def init_language_model(
    temperature: float = 0.0,
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs: Any,
) -> ChatOpenAI:
    """
    Initialize language model, supporting OpenAI models and other model providers.

    Args:
        temperature: Model output temperature, controlling randomness. Default is 0.0.
        provider: Optional model provider, takes priority over environment variables.
        model_name: Optional model name, takes priority over environment variables.
        **kwargs: Other optional parameters, passed to model initialization.

    Returns:
        Initialized language model instance.

    Raises:
        ValueError: Raised when provided parameters are invalid or necessary configuration is missing.
    """
    provider = (
        provider.lower() if provider else os.getenv("LLM_PROVIDER", "openai").lower()
    )
    model_name = model_name or os.getenv("LLM_MODEL", "gpt-4")

    api_key_env_var = f"OPENAI_API_KEY_{provider.upper()}"
    api_base_env_var = f"OPENAI_API_BASE_{provider.upper()}"

    openai_api_key = os.environ.get(api_key_env_var)
    openai_api_base = os.environ.get(api_base_env_var)

    if not openai_api_key or not openai_api_base:
        raise ValueError(
            f"Cannot find API key or base URL for {provider}. Please check environment variable settings."
        )

    model_params = {
        "model": model_name,
        "openai_api_key": openai_api_key,
        "openai_api_base": openai_api_base,
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


class CustomEmbeddings(Embeddings):
    def __init__(
        self,
        api_key: str,
        api_url: str,
        model: str,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json",
        }

        all_embeddings = []

        for text in texts:
            payload = {"model": self.model, "input": text, "encoding_format": "float"}

            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            embedding = response.json()["data"][0]["embedding"]
            all_embeddings.append(embedding)

        return all_embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._get_embeddings([text])[0]
