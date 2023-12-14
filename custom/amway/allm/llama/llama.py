"""Wrapper around MOSS APIs."""
import traceback
from typing import Any, List, Mapping, Optional
import requests
from loguru import logger
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
from framework.business_code import ERROR_10900
from framework.business_except import BusinessException


class LLamaAI(LLM):

    url = "http://10.143.33.252:19327/v1/completions"
    temperature = 0.4
    top_p: float = 0.8
    top_k: int = 40
    max_length: int = 2048
    repetition_penalty: float = 1.02

    @property
    def _default_params(self) -> Mapping[str, Any]:
        return {
            "temperature": self.temperature,
            "max_length": self.max_length,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
        }

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {**{"url": self.url}, **self._default_params}

    @property
    def _llm_type(self) -> str:
        return "llama"

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        json = {
            "prompt": prompt,
            **self._default_params,
            **kwargs
        }
        logger.info("###Request LLamaAI INFO, url={}, headers={}, json={}.", self.url, headers, json)
        try:
            response = requests.post(
                url=self.url,
                headers=headers,
                json=json,
            )
        except Exception as err:
            traceback.print_exc()
            logger.error("###Request LLamaAI ERROR, code={}, message={}.", ERROR_10900, err)
            raise BusinessException(ERROR_10900.code, ERROR_10900.message)
        logger.info("###Request LLamaAI INFO, response={}.", response.text)
        response_json = response.json()
        answer = response_json["choices"][0]["text"]
        if stop is not None:
            answer = enforce_stop_tokens(answer, stop)
        return answer
