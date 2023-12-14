"""Wrapper around MosaicML APIs."""
import time
from typing import Any, Dict, List, Mapping, Optional

import requests
from loguru import logger
from pydantic import BaseModel, Extra, root_validator

from langchain.embeddings.base import Embeddings
from langchain.utils import get_from_dict_or_env
from models.embeddings.amway.amway_embedding_config import *


class AmwayApiEmbeddings(BaseModel, Embeddings):
    """Wrapper around Amway's embedding api service.

    To use, you should have the environment variable ``AMWAY_EMBEDDINGS_API_URL`` to set with your api endpoint url, or pass
    it as a named parameter to the constructor.

    Example:
        .. code-block:: python

            from langchain.llms import AmwayApiEmbeddings
            amway_embeddings = AmwayApiEmbeddings()
    """

    amway_embeddings_api_url: str = DEFAULT_MODEL_URL
    """Endpoint URL to use."""
    
    amway_embeddings_api_key: Optional[str] = None
    """If needed some day"""

    model_name: Optional[str] = DEFAULT_MODEL_NAME
    """Model name to use."""

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and url exists in environment."""
        # amway_embeddings_api_key = get_from_dict_or_env(
        #     values, "amway_embeddings_api_key", "AMWAY_EMBEDDINGS_API_KEY"
        # )
        
        """Get and Validate api url from environment."""
        amway_embeddings_api_url = get_from_dict_or_env(
            values, "amway_embeddings_api_url", "AMWAY_EMBEDDINGS_API_URL"
        )

        # values["amway_embeddings_api_key"] = amway_embeddings_api_key
        values["amway_embeddings_api_url"] = amway_embeddings_api_url
        return values

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"amway_embeddings_api_url": self.amway_embeddings_api_url}

    def _embed(
            self,
            input: List[str]
    ) -> List[List[float]]:
        result_list = []
        temp = 0
        total = 0
        for i in input:
            try:
                total = total + 1
                if temp == 1000:
                    logger.info("embeddings request sleep 3s ....")
                    temp = 0
                    time.sleep(3)
                embeddings = self._embed_single(content=i, total=total)
            except Exception as err:
                print(err)
                continue
            temp = temp + 1
            result_list.append(embeddings)
        return result_list

    def _embed_single(
            self,
            content: str,
            total: int,
    ) -> List[float]:
        # HTTP headers for authorization
        headers = {
            # "Authorization": f"{self.amway_embeddings_api_key}",
            "Content-Type": "application/json",
        }

        # send request
        payload = {
            "content_chunk": content,
            # "model_name": self.model_name,
            }
        try:
            response = requests.post(
                self.amway_embeddings_api_url,
                headers=headers,
                json=payload,
                timeout=(HTTP_REQUEST_CONN_TIMEOUT, HTTP_REQUEST_READ_TIMEOUT)
            )
            logger.info("#############Request Amway Embeddings INFO, url={}, headers={}, response={}, total={}.",
                        self.amway_embeddings_api_url, headers, response, total)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error raised by embedding inference endpoint: {e}")

        try:
            parsed_response = response.json()

            # The inference API has changed a couple of times, so we add some handling
            # to be robust to multiple response formats.
            if isinstance(parsed_response, dict):
                if "embeddings" in parsed_response:
                    embeddings = parsed_response["embeddings"]
                else:
                    raise ValueError(
                        f"No key data in response: {parsed_response}"
                    )
            else:
                raise ValueError(f"Unexpected response type: {parsed_response}")

        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(
                f"Error raised by inference API: {e}.\nResponse: {response.text}"
            )

        return embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        embeddings = self._embed(texts)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a query using a MosaicML deployed instructor embedding model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        embedding = self._embed([text])[0]
        return embedding
