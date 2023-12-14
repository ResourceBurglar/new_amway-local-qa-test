"""Wrapper around MOSS APIs."""
from typing import Any, Dict, List, Mapping, Optional

import requests
from loguru import logger
from pydantic import Extra, root_validator

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
from langchain.utils import get_from_dict_or_env

default_moss_api_key: Optional[str] = "http://10.143.33.253:8000"

class Moss(LLM):
    """Wrapper around MOSS large language models.

    Check the repo: https://github.com/OpenLMLab/MOSS

    Example:
        .. code-block:: python

            from langchain.llms import Moss
            moss = Moss(moss_api_url="") # or set MOSS_API_URL in environment, then use: moss = Moss()
            response = moss("推荐5本好书")
    """

    moss_api_url: str = ""
    """Model name to use."""

    temperature: float = 0.4
    """What sampling temperature to use."""

    uid: Optional[str] = None
    """What sampling temperature to use."""

    max_length: int = 2048
    """The maximum number of tokens to generate in the completion."""

    top_p: float = 0.8
    """Total probability mass of tokens to consider at each step."""

    top_k: int = 40
    """The number of highest probability vocabulary tokens to
    keep for top-k-filtering."""

    repetition_penalty: float = 1.02
    """Penalizes repeated tokens according to frequency."""

    # moss_api_key: Optional[str] = "http://10.143.33.253:8000"
    """API key for MOSS API. Currently none, can be set if needed in the future."""


    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    # Note: this is commented out because we don't need an API key for now
    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key exists in environment."""
        # moss_api_key = get_from_dict_or_env(
        #     values, "moss_api_key", "MOSS_API_KEY"
        # )
        
        """Get and Validate api url from environment."""
        # moss_api_url = get_from_dict_or_env(
        #     values, "moss_api_url", "MOSS_API_URL"
        # )

        # values["moss_api_key"] = moss_api_key
        # values["moss_api_url"] = default_moss_api_key or moss_api_url
        values["moss_api_url"] = "http://10.140.208.168/glm/"
        return values

    @property
    def _default_params(self) -> Mapping[str, Any]:
        """Get the default parameters for calling MOSS API."""
        return {
            "temperature": self.temperature,
            "max_length": self.max_length,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
        }

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {**{"moss_api_url": self.moss_api_url}, **self._default_params}

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "moss"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call out to MOSS api url.

        Args:
            prompt: The prompt to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The string generated by the model.

        Example:
            .. code-block:: python

                response = moss("推荐5本好书")
        """
        headers = {
            "Content-Type": "application/json"
        }
        json = {"prompt": prompt, **self._default_params, **kwargs}
        logger.info("#############Request Amway LLMs INFO, url={}, headers={}, json={}.",
                    self.moss_api_url, headers, json)
        response = requests.post(
            url=self.moss_api_url,
            headers=headers,
            json=json,
        )
        response_json = response.json()
        logger.info("#############Request Amway LLMs INFO, response={}.", response_json)
        answer = response_json["response"]
        if stop is not None:
            # I believe this is required since the stop tokens
            # are not enforced by the model parameters
            answer = enforce_stop_tokens(answer, stop)
        return answer