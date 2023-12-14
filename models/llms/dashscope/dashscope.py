from typing import Any, List, Mapping, Optional
import requests
from loguru import logger
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from custom.amway.amway_config import BAIDUBCE_SECURE_ANSWER


class DashScopeAI(LLM):

    model_name = "qwen-turbo"
    top_p: float = 0.8
    top_k: int = 999
    temperature: float = 1.0
    url: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    api_key: str = "sk-37bf765fc1924ca7bd1bf02277b019b1"
    history: List[List[str]] = None

    @property
    def _llm_type(self) -> str:
        return "dashscope"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key,
        }

        # 从扩展参数中获取重试参数标识
        retry = True
        for k, v in kwargs.items():
            if k == "retry":
                retry = v
                break

        messages = []
        if self.history and len(self.history) > 0:
            for h in self.history:
                messages.append({
                    "role": "user",
                    "content": h[0],
                })
                messages.append({
                    "role": "system",
                    "content": h[1],
                })

        json = {
            "model": self.model_name,
            "input": {
                "prompt": prompt,
                "parameters": {
                    "top_p": self.top_p,
                    "top_k": self.top_k,
                    "temperature": self.temperature,
                    "messages": messages if retry else []
                },
            },
        }
        logger.info("#############Request DashScope LLMs INFO, url={}, headers={}, json={}.", self.url, headers, json)
        response = requests.post(url=self.url, headers=headers, json=json)
        response_json = response.json()
        logger.info("#############Request DashScope LLMs INFO, httpstatus={}, response={}.", response.status_code, response_json)

        if response.status_code != 200:
            if 'code' in response_json and response_json['code'] == "DataInspectionFailed" and retry:
                return self.__call__(prompt=prompt, retry=False, **kwargs)
            return BAIDUBCE_SECURE_ANSWER
        return response_json["output"]["text"]


if __name__ == "__main__":
    # print(DashScopeAI().__call__(prompt="你好！"))
    print(DashScopeAI().__call__(prompt="习近平的级别"))

