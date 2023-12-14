from typing import List

from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI
from config.base_config import *
from custom.amway.allm.chatglm.chatglm import ChatGlmAI
from custom.amway.allm.chatglm.chatglm3 import ChatGlm3AI
from models.llms.baidubce.baidubce import BaidubceAI
from models.llms.dashscope.dashscope import DashScopeAI
from custom.amway.allm.llama.llama import LLamaAI
from custom.amway.allm.moss.moss import Moss
from custom.amway.amway_config import (
    AI_BC_MODEL_NAME,
    AI_BC_TEMPERATURE,
    AI_BC_API_KEY,
    AI_BC_OUTPUT_TOKEN_LENGTH,
    AI_BC_MODEL_BASE_URL,
)


class LLMsAdapter:
    """
    大语言模型 - 适配器
    """

    def __init__(
            self,
            model: str = CURRENT_LLM,
    ):
        """
        构造函数
        :param model: 指定模型
        """
        self.model = model

    def get_model_instance(
            self,
            history: List[List[str]] = None
    ) -> BaseLanguageModel:
        """
        获取指定的大语言模型实例
        :return: 模型实例
        """
        if self.model == "OpenAI":
            return ChatOpenAI(
                model_name=OPENAI_MODEL_NAME,
                temperature=OPENAI_TEMPERATURE,
                openai_api_key=OPENAI_API_KEY,
                max_tokens=OPENAI_OUTPUT_TOKEN_LENGTH
            )
        elif self.model == "BaiChuan":
            return ChatOpenAI(
                model_name=AI_BC_MODEL_NAME,
                temperature=AI_BC_TEMPERATURE,
                openai_api_key=AI_BC_API_KEY,
                max_tokens=AI_BC_OUTPUT_TOKEN_LENGTH,
                openai_api_base=AI_BC_MODEL_BASE_URL,
            )
        elif self.model == "LLaMA":
            return LLamaAI()
        elif self.model == "Moss":
            return Moss()
        elif self.model == "ChatGLM":
            return ChatGlmAI(history=history)
        elif self.model == "ChatGLM3":
            return ChatGlm3AI(history=history)
        elif self.model == "Baidubce":
            return BaidubceAI(history=history)
        elif self.model == "DashScope":
            return DashScopeAI(history=history)
        else:
            """
            TODO 其他类型的LLMs
            """