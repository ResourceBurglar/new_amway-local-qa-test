import uuid
from datetime import datetime
from typing import List, Tuple, Any
from langchain import PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.schema import Document
from loguru import logger
from config.base_config import MEMORY_LIMIT_SIZE, SPLIT_CHUNK_TYPE
from custom.amway.amway_config import AMWAY_ENABLED, AMWAY_CUS_ENABLED
from custom.amway.amway_custom import get_prepare_answer, get_prepare_docs, chat_public
from framework.business_code import ERROR_10007, ERROR_10000, ERROR_10001, ERROR_10201
from framework.business_except import BusinessException
from models.chains.chain_model import ChainModel
from models.embeddings.es_model_adapter import EmbeddingsModelAdapter
from models.llms.llms_adapter import LLMsAdapter
from models.vectordatabase.v_client import get_instance_client
from service.base_chat_message import BaseChatMessage
from service.local_entity_service import ChatBotDomain, ChatHistoryDomain, NamespaceDomain
from service.local_repo_service import LocalRepositoryDomain
from service.model.chat_history_model import ChatHistoryModel


class ChatPrivateDomain(BaseChatMessage):
    """
    领域知识问答服务
    """
    def __init__(
            self,
            request_id: str = str(uuid.uuid4())
    ):
        """
        构造函数
        :param request_id: 请求唯一标识
        """
        self.request_id = request_id

    def ask(
            self,
            ques: str,
            bot_id: str,
            user_id: str = None,
            group_uuid: str = None,
    ) -> dict:
        """
        领域知识问答
        :param ques: 问题
        :param bot_id: 机器人标识
        :param user_id: 用户标识
        :param group_uuid: 会话分组标识\n
        :return: AI回答内容
        """
        question_time = datetime.now()
        # 查询机器人信息
        chatBotModel = ChatBotDomain(request_id=self.request_id).find_one(bot_id=bot_id)
        if not chatBotModel:
            logger.error("ChatPrivateDomain_ask ERROR, [{}]未查询到机器人[{}]信息, request_id={}.", ERROR_10000, bot_id, self.request_id)
            raise BusinessException(ERROR_10000.code, ERROR_10000.message)
        if not chatBotModel.is_private_bot():
            logger.error("ChatPrivateDomain_ask ERROR, [{}]当前机器人[{}]的使用类型不合法, request_id={}.", ERROR_10007, bot_id, self.request_id)
            raise BusinessException(ERROR_10007.code, ERROR_10007.message)

        # 查询知识库信息
        namespace_id = chatBotModel.namespace_id
        if not namespace_id:
            logger.error("ChatPrivateDomain_ask ERROR, [{}]未查询到所属知识库[{}]信息, request_id={}.", ERROR_10001, namespace_id, self.request_id)
            raise BusinessException(ERROR_10001.code, ERROR_10001.message)
        namespaceModel = NamespaceDomain(request_id=self.request_id).find_by_id(namespace_id)
        if not namespaceModel:
            logger.error("ChatPrivateDomain_ask ERROR, [{}]未查询到所属知识库[{}]信息, request_id={}.", ERROR_10001, namespace_id, self.request_id)
            raise BusinessException(ERROR_10001.code, ERROR_10001.message)
        namespace = namespaceModel.namespace

        # 查询历史聊天记录
        chatHistoryDomain = ChatHistoryDomain(request_id=self.request_id)
        memory_limit_size = chatBotModel.memory_limit_size or MEMORY_LIMIT_SIZE
        if AMWAY_ENABLED:
            history = chatHistoryDomain.find_last_by_id(user_id=user_id, limit_size=memory_limit_size)
        else:
            history = chatHistoryDomain.find_last_by_id(user_id=user_id, bot_id=bot_id, limit_size=memory_limit_size)

        # 知识库-语义搜索
        ques_docs = LocalRepositoryDomain(request_id=self.request_id).search(
            ques=ques,
            namespace=namespace,
            vector_search_top_k=chatBotModel.vector_top_k
        )

        if AMWAY_CUS_ENABLED and len(ques_docs) == 0:
            return chat_public(
                ques=ques,
                bot_id=bot_id,
                user_id=user_id,
                group_uuid=group_uuid,
                history=history,
                question_time=question_time,
                request_id=self.request_id,
            )

        # 知识库-Q&A类型处理
        if namespaceModel.is_prepare_type():
            if AMWAY_ENABLED:
                _answer = get_prepare_answer(ques_docs=ques_docs)
                if _answer:
                    return _answer
            if ques_docs and ques_docs[0][0].metadata.get("scene") \
                    and ques_docs[0][0].metadata.get("scene") != "nan" \
                    and ques_docs[0][0].metadata.get("scene") != "None":
                scene = ques_docs[0][0].metadata.get("scene")
                answer = ques_docs[0][0].metadata.get("answer")
                # 保留历史聊天记录
                return self.save_history_message(
                    ques=ques,
                    answer=answer,
                    bot_id=bot_id,
                    user_id=user_id,
                    question_time=question_time,
                    chatHistoryDomain=chatHistoryDomain,
                    scene=scene,
                    group_uuid=group_uuid,
                )
            new_ques_docs = get_prepare_docs(ques_docs=ques_docs)
        else:
            new_ques_docs = ques_docs

        # 请求大模型问答功能
        answer = self.ask_to_docs(
            ques=ques,
            prompt=chatBotModel.prompt,
            prompt_variables=chatBotModel.prompt_variables,
            prefix_prompt=chatBotModel.prefix_prompt,
            prefix_prompt_variables=chatBotModel.prefix_prompt_variables,
            ques_docs=new_ques_docs,
            history=history,
            split_chunk_type=chatBotModel.chains_chunk_type,
        )
        # 保留历史聊天记录
        return self.save_history_message(
            ques=ques,
            answer=answer,
            bot_id=bot_id,
            user_id=user_id,
            question_time=question_time,
            chatHistoryDomain=chatHistoryDomain,
            group_uuid=group_uuid,
        )

    def ask_to_docs(
            self,
            ques: str,
            ques_docs: List[Tuple[Document, float]],
            prompt: str,
            prompt_variables: str,
            prefix_prompt: str = None,
            prefix_prompt_variables: str = None,
            history: List[ChatHistoryModel] = None,
            split_chunk_type: str = SPLIT_CHUNK_TYPE,
            llm: BaseLanguageModel = None,
            **kwargs: Any,
    ) -> str:
        """
        本地知识库问答能力
        :param ques_docs: 文档信息
        :param split_chunk_type: Chunk类型
        :param ques: 问题信息
        :param prompt: 提示词信息
        :param prompt_variables: 提示词变量
        :param prefix_prompt: 前缀提示词信息
        :param prefix_prompt_variables: 前缀提示词变量
        :param history: 历史聊天记录
        :param llm: 大模型对象
        :return: 问答结果
        """
        llm = llm if llm else LLMsAdapter().get_model_instance(history=ChainModel.init_memory(history=history)[1])
        if split_chunk_type == "stuff":
            chain = ChainModel.get_instance_with_stuff(
                prompt=prompt,
                str_prompt_variables=prompt_variables,
                history=history,
                llm=llm,
                **kwargs
            )
            input_documents = [doc for doc, _ in ques_docs]
            answer = chain.run(input_documents=input_documents, question=ques)
            logger.info("####ChatPrivateDomain ask_to_docs INFO，request_id={}, \n>>>AI回答: [{}].", self.request_id, answer)
            return BaseChatMessage.purge(answer=answer)
        elif split_chunk_type == "refine":
            chain = ChainModel.get_instance_with_refine(
                prompt=prompt,
                prefix_prompt=prefix_prompt,
                str_prompt_variables=prompt_variables,
                str_prefix_prompt_variables=prefix_prompt_variables,
                llm=llm
            )
            input_documents = [doc for doc, _ in ques_docs]
            answer = chain.run(input_documents=input_documents, question=ques)
            logger.info("####ChatPrivateDomain ask_to_docs INFO，request_id={}, \n>>>AI回答: [{}].", self.request_id, answer)
            return BaseChatMessage.purge(answer=answer)
        else:
            pass

    def chat(
            self,
            ques: str,
            namespace_id: str
    ) -> str:
        """
        聊天功能
        :param ques: 问题
        :param namespace_id: 知识库标识
        :return: 回答
        """
        # 根据标识查询知识库信息
        namespaceModel = NamespaceDomain().find_by_id(namespace_id)
        if not namespaceModel:
            logger.error("ChatPrivateDomain_chat ERROR, [{}]未查询到所属知识库[{}]信息, request_id={}.", ERROR_10001, namespace_id, self.request_id)
            raise BusinessException(ERROR_10001.code, ERROR_10001.message)
        # 语义搜索知识库中的相关信息
        ques_docs: list
        try:
            ques_docs = get_instance_client().search_data(
                ques=ques,
                embedding=EmbeddingsModelAdapter().get_model_instance(),
                namespace=namespaceModel.namespace,
                search_top_k=1,
            )
        except Exception as err:
            logger.error("ChatPrivateDomain_chat ERROR, [{}]查询向量库文档操作失败, message={}, request_id={}.", ERROR_10201, err, self.request_id)
            raise BusinessException(ERROR_10201.code, ERROR_10201.message)
        if not ques_docs and len(ques_docs) == 0:
            logger.error("ChatPrivateDomain_chat ERROR, [{}]查询向量库文档操作失败, request_id={}.", ERROR_10201, self.request_id)
            raise BusinessException(ERROR_10201.code, ERROR_10201.message)

        prompt = """{question}
            可以参考的上下文: 
            {context}
            """
        handle_prompt = prompt.replace('{context}', ques_docs[0][0].page_content)
        prompt_template = PromptTemplate(template=handle_prompt, input_variables=["question"])
        chain = ChainModel.get_instance_with_llm_chain(prompt_template=prompt_template)
        return chain.predict(question=ques)
