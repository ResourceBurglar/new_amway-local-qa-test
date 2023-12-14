import uuid
from typing import List
from loguru import logger
import requests
from custom.amway.amway_config import BAIDUBCE_SECURE_ANSWER
from service.model.chat_history_model import ChatHistoryModel


class DashScopeClient:

    def __init__(
            self,
            model_name: str = "qwen-turbo",
            top_p: float = 0.8,
            top_k: int = 999,
            temperature: float = 1.0,
            url: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            api_key: str = "sk-37bf765fc1924ca7bd1bf02277b019b1",
            request_id: str = str(uuid.uuid4()),
    ):
        self.model_name = model_name
        self.top_p = top_p
        self.top_k = top_k
        self.temperature = temperature
        self.url = url
        self.api_key = api_key
        self.request_id = request_id

    def chat(
            self,
            ques: str,
            history: List[ChatHistoryModel] = [],
            retry: bool = True,
    ):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key,
        }

        messages = []
        for h in history:
            messages.append({
                "role": "user",
                "content": h.question,
            })
            messages.append({
                "role": "system",
                "content": h.answer,
            })

        json = {
            "model": self.model_name,
            "input": {
                "prompt": ques,
                "parameters": {
                    "top_p": self.top_p,
                    "top_k": self.top_k,
                    "temperature": self.temperature,
                    "messages": messages
                },
            },
        }
        logger.info("#############Request DashScope LLMs INFO, request_id={}, url={}, headers={}, json={}.", self.request_id, self.url, headers, json)
        response = requests.post(url=self.url, headers=headers, json=json)
        response_json = response.json()
        logger.info("#############Request DashScope LLMs INFO, request_id={}, httpstatus={}, response={}.", self.request_id, response.status_code, response_json)

        if response.status_code != 200:
            if 'code' in response_json and response_json['code'] == "DataInspectionFailed" and retry:
                return self.chat(ques=ques, history=[], retry=False)
            return BAIDUBCE_SECURE_ANSWER, False
        return response_json["output"]["text"], True


if __name__ == '__main__':
    client = DashScopeClient()
    print(client.chat(ques="习近平的级别"))
    # print(client.chat(ques="广州哪里好玩？"))
