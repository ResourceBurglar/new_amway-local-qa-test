from typing import List, Any
from langchain.base_language import BaseLanguageModel
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chains.question_answering import load_qa_chain
from loguru import logger
from langchain import LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory
from custom.amway.allm.chatglm.chatglm import ChatGlmAI
from custom.amway.amway_config import AMWAY_ENABLED
from custom.amway.amway_custom import get_memory
from framework.business_code import ERROR_10002
from framework.business_except import BusinessException
from models.llms.dashscope.dashscope import DashScopeAI
from models.llms.llms_adapter import LLMsAdapter
from content.prompt_template_chat import (
    CONVERSATION_CHAT_TEMPLATE,
    CONVERSATION_CHAT_VARIABLES,
    MEMORY_HISTORY_KEY, MEMORY_INPUT_KEY
)
from service.model.chat_history_model import ChatHistoryModel


class ChainModel:
    """
    链式模型
        - 可提供默认常规的聊天链实例对象
        - 可提供语义搜索的聊天链实例对象
    """
    @classmethod
    def get_instance(
            cls,
            llm: BaseLanguageModel = None,
    ) -> LLMChain:
        """
        获取默认的聊天链实例对象
        :param llm: 大模型对象
        :return: 聊天链实例对象
        """
        return cls.get_instance_with_llm_chain_by_history_prompt(
            prompt=CONVERSATION_CHAT_TEMPLATE,
            prompt_input_variables=CONVERSATION_CHAT_VARIABLES,
            memory_history_key=MEMORY_HISTORY_KEY,
            memory_input_key=MEMORY_INPUT_KEY,
            llm=llm,
        )

    @classmethod
    def get_instance_with_llm_chain_by_history_prompt(
            cls,
            prompt: str,
            prompt_input_variables: List[str],
            memory_history_key: str,
            memory_input_key: str,
            history: List[ChatHistoryModel] = None,
            llm: BaseLanguageModel = None,
            verbose: bool = False,
    ) -> LLMChain:
        """
        获取聊天链实例对象
        :param prompt: 提示词信息
        :param prompt_input_variables: 提示词占位符
        :param memory_history_key:  长程记忆-历史记录占位符字段
        :param memory_input_key: 长程记忆-输入信息占位符字段
        :param history: 历史聊天记录
        :param llm: 大模型对象
        :param verbose: 过程冗余信息
        :return: 聊天链实例对象
        """
        prompt_template = PromptTemplate(template=prompt, input_variables=prompt_input_variables)
        return cls.get_instance_with_llm_chain_by_history(
            prompt_template=prompt_template,
            history=history,
            memory_history_key=memory_history_key,
            memory_input_key=memory_input_key,
            verbose=verbose,
            llm=llm,
        )

    @classmethod
    def get_instance_with_llm_chain_by_history(
            cls,
            prompt_template: PromptTemplate,
            history: List[ChatHistoryModel] = None,
            memory_history_key: str = MEMORY_HISTORY_KEY,
            memory_input_key: str = MEMORY_INPUT_KEY,
            llm: BaseLanguageModel = None,
            verbose: bool = False,
    ) -> LLMChain:
        """
        获取聊天链实例对象
        :param prompt_template: 提示词模板对象
        :param history: 历史聊天记录
        :param memory_history_key:  长程记忆-历史记录占位符字段
        :param memory_input_key: 长程记忆-输入信息占位符字段
        :param llm: 大模型对象
        :param verbose: 过程冗余信息
        :return: 聊天链实例对象
        """
        # 封装历史聊天记录
        memory, chat_glm_history = cls.init_memory(
            history=history,
            memory_history_key=memory_history_key,
            memory_input_key=memory_input_key
        )
        return cls.get_instance_with_llm_chain(
            prompt_template=prompt_template,
            verbose=verbose,
            memory=memory,
            llm=llm,
        )

    @classmethod
    def get_instance_with_llm_chain(
            cls,
            prompt_template: PromptTemplate,
            verbose: bool = False,
            memory: ConversationBufferMemory = None,
            llm: BaseLanguageModel = None,
            history: List[List[str]] = None,
    ) -> LLMChain:
        """
        获取聊天链实例对象
        :param prompt_template: 提示词模板对象
        :param verbose: 过程冗余信息
        :param memory: 长程记忆
        :param llm: 大模型对象
        :param history: 历史聊天记录
        :return: 聊天链实例对象
        """
        llm = llm if llm else LLMsAdapter().get_model_instance(history=history)
        if isinstance(llm, ChatGlmAI) or isinstance(llm, DashScopeAI):
            memory, chat_glm_history = cls.init_memory()
        return LLMChain(
            llm=llm,
            prompt=prompt_template,
            verbose=verbose,
            memory=memory,
        )

    @classmethod
    def get_instance_with_refine(
            cls,
            prompt: str,
            prefix_prompt: str,
            prompt_variables: List[str] = None,
            prefix_prompt_variables: List[str] = None,
            llm: BaseLanguageModel = LLMsAdapter().get_model_instance(),
            **kwargs: Any,
    ) -> BaseCombineDocumentsChain:
        """
        Refine模式的链式问答
        :param prompt: 提示词信息
        :param prompt_variables: 提示词占位符
        :param prefix_prompt: 提示词前缀信息
        :param prefix_prompt_variables: 提示词前缀占位符
        :param llm: 大模型对象
        :param kwargs: 扩展参数
        :return: 聊天链实例对象
        """
        for k, v in kwargs.items():
            if k == "str_prompt_variables":
                prompt_variables = v.split(",")
                continue
            if k == "str_prefix_prompt_variables":
                prefix_prompt_variables = v.split(",")
                continue
        # 校验指令参数信息是否合法
        if not prompt or not prompt_variables or not prefix_prompt or not prefix_prompt_variables:
            logger.error("######ChainModel error[{}], prompt param is not legal.", ERROR_10002)
            raise BusinessException(ERROR_10002.code, ERROR_10002.message)
        # 封装指令模板
        refine_prompt = PromptTemplate(
            input_variables=prompt_variables,
            template=prompt,
        )
        question_prompt = PromptTemplate(
            input_variables=prefix_prompt_variables,
            template=prefix_prompt,
        )
        # 创建链式问答对象
        return load_qa_chain(
            llm=llm,
            chain_type='refine',
            question_prompt=question_prompt,
            refine_prompt=refine_prompt,
            verbose=True,
        )

    @classmethod
    def get_instance_with_stuff(
            cls,
            prompt: str,
            prompt_variables: List[str] = None,
            history: List[ChatHistoryModel] = None,
            llm: BaseLanguageModel = LLMsAdapter().get_model_instance(),
            **kwargs: Any,
    ) -> BaseCombineDocumentsChain:
        """
        Stuff模式的链式问答
        :param prompt: 提示词信息
        :param prompt_variables: 提示词占位符
        :param history: 历史聊天记录
        :param llm: 大模型实例对象
        :param kwargs: 扩展参数
        :return: 聊天链实例对象
        """
        for k, v in kwargs.items():
            if k == "str_prompt_variables":
                prompt_variables = v.split(",")
                continue
        # 校验指令参数信息是否合法
        if not prompt or not prompt_variables:
            logger.error("######ChainModel error[{}], prompt param is not legal.", ERROR_10002)
            raise BusinessException(ERROR_10002.code, ERROR_10002.message)
        # 封装历史聊天记录
        prompt_template = PromptTemplate(template=prompt, input_variables=prompt_variables)
        if isinstance(llm, ChatGlmAI) or isinstance(llm, DashScopeAI):
            memory = cls.init_memory()[0]
        else:
            memory = cls.init_memory(history=history)[0]
        return load_qa_chain(
            llm=llm,
            chain_type='stuff',
            prompt=prompt_template,
            memory=memory,
            verbose=True,
        )

    @staticmethod
    def init_memory(
            history: List[ChatHistoryModel] = None,
            memory_history_key: str = "chat_history",
            memory_input_key: str = "question"
    ):
        """
        封装历史聊天记录
        :param history: 历史聊天记录
        :param memory_history_key:  长程记忆-历史记录占位符字段
        :param memory_input_key: 长程记忆-输入信息占位符字段
        :return: 长程记忆对象
        """
        if AMWAY_ENABLED:
            memory = get_memory(
                history=history,
                memory_history_key=memory_history_key,
                memory_input_key=memory_input_key,
            )
        else:
            memory = ConversationBufferMemory(memory_key=memory_history_key, input_key=memory_input_key)
            if history and len(history) > 0:
                # history转memory倒叙处理
                for h in history[::-1]:
                    memory.chat_memory.add_user_message(h.question)
                    memory.chat_memory.add_ai_message(h.answer)
        chat_glm_history = [[h.question, h.answer] for h in history[::-1]] if history and len(history) > 0 else []
        return memory, chat_glm_history
