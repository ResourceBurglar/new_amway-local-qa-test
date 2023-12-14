import uuid
from datetime import datetime
from langchain import PromptTemplate
from loguru import logger
from config.base_config import MEMORY_LIMIT_SIZE
from content.prompt_template_chat import CONVERSATION_CHAT_TEMPLATE
from custom.amway.amway_config import AMWAY_ENABLED, AMWAY_CUS_ENABLED, AMWAY_MEETING_ROOM_ENABLED
from custom.amway.amway_custom import chat_public
from framework.business_code import ERROR_10007, ERROR_10000
from framework.business_except import BusinessException
from models.chains.chain_model import ChainModel
from service.base_chat_message import BaseChatMessage
from service.local_entity_service import ChatBotDomain, ChatHistoryDomain, ChatMeetingRoomDomain
from service.meeting_room_system import MeetingParams, MeetingRoomSystem


class ChatPublicDomain(BaseChatMessage):
    """
    公共知识问答服务
    """
    def __init__(
            self,
            request_id: str = str(uuid.uuid4()),
    ):
        """
        构造方法
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
        公共知识问答
        :param ques: 问题
        :param bot_id: 机器人标识
        :param user_id: 用户标识
        :param group_uuid: 会话分组标识
        :return: AI回答内容
        """
        question_time = datetime.now()
        # 根据标识查询机器人配置信息
        chatBotDomain = ChatBotDomain(self.request_id)
        chatBotModel = chatBotDomain.find_one(bot_id=bot_id)
        logger.info("ChatPublicDomain INFO, request_id={}, 当前机器人信息：{}.", self.request_id, chatBotModel)
        if not chatBotModel:
            logger.error("ChatPublicDomain ERROR, [{}]未查询到机器人[{}]信息, request_id={}.", ERROR_10000, bot_id, self.request_id)
            raise BusinessException(ERROR_10000.code, ERROR_10000.message)
        if not chatBotModel.is_public_bot():
            logger.error("ChatPublicDomain ERROR, [{}]当前机器人[{}]的使用类型不合法, request_id={}.", ERROR_10007, bot_id, self.request_id)
            raise BusinessException(ERROR_10007.code, ERROR_10007.message)

        # 查询历史聊天记录
        chatHistoryDomain = ChatHistoryDomain(self.request_id)
        memory_limit_size = chatBotModel.memory_limit_size or MEMORY_LIMIT_SIZE
        if AMWAY_ENABLED:
            history = chatHistoryDomain.find_last_by_id(user_id=user_id, limit_size=memory_limit_size)
        else:
            history = chatHistoryDomain.find_last_by_id(user_id=user_id, bot_id=bot_id, limit_size=memory_limit_size)
        logger.info("ChatPublicDomain INFO, request_id={}, 当前历史聊天记录：{}.", self.request_id, history)
        
        
        
        # 会议室预订系统逻辑
        if AMWAY_MEETING_ROOM_ENABLED:
            if '会议室' in ques:
                # 查询关于会议室的历史聊天记录
                control_type = MeetingParams.get_controlType(ques)
                chatMeetingRoomDomain = ChatMeetingRoomDomain(self.request_id)
                if AMWAY_ENABLED:
                    meeting_history = chatMeetingRoomDomain.find_last_by_id(user_id=user_id,control_type=control_type,
                                                                            group_id=group_uuid,limit_size=1)
                else:
                    meeting_history = chatMeetingRoomDomain.find_last_by_id(user_id=user_id,control_type=control_type,
                                                                            bot_id=bot_id,group_id=group_uuid
                                                                           limit_size=1)
                if not meeting_history:
                    params = MeetingParams.get_params(controlType=control_type, sequence=ques, params=dict())
                    meeting_system = MeetingRoomSystem(sequence=ques,control_type = control_type,params = params)
                    if MeetingParams.is_all_params(params):
                        return meeting_system.create()
                    else:
                        return meeting_system.next_round()
                else:
                    params = eval(meeting_history.parameters)
                    new_params = MeetingParams.get_params(controlType=control_type, sequence=ques, params=params)
                    
                
                
                
                
            
            
            

        # 定制逻辑
        if AMWAY_CUS_ENABLED:
            return chat_public(
                ques=ques,
                bot_id=bot_id,
                user_id=user_id,
                group_uuid=group_uuid,
                history=history,
                question_time=question_time,
                request_id=self.request_id,
            )

        # 封装历史聊天记录
        memory, chat_glm_history = ChainModel.init_memory(history=history)
        # 封装指令信息
        prompt: PromptTemplate
        if not chatBotModel.prompt or str(chatBotModel.prompt).isspace():
            prompt = PromptTemplate(template=CONVERSATION_CHAT_TEMPLATE, input_variables=["chat_history", "question"])
        else:
            prompt_input_variables = chatBotModel.prompt_variables.split(",")
            template = chatBotModel.prompt + chatBotModel.suffix_prompt
            prompt = PromptTemplate(template=template, input_variables=prompt_input_variables)

        # 发起问答
        chain = ChainModel.get_instance_with_llm_chain(prompt_template=prompt, memory=memory, verbose=True, history=chat_glm_history)
        logger.info("ChatPublicDomain INFO, request_id={}, chain.prompt={}.", self.request_id, chain.prompt)
        answer = chain.predict(question=ques)
        logger.info("ChatPublicDomain INFO, request_id={}, 问题=[{}], 回答结果=[{}].", self.request_id, ques, answer)
        return self.purge_with_history(
            ques=ques,
            answer=answer,
            bot_id=bot_id,
            user_id=user_id,
            question_time=question_time,
            chatHistoryDomain=chatHistoryDomain,
            group_uuid=group_uuid,
        )

    def chat(
            self,
            ques: str
    ) -> str:
        """
        聊天功能
        :param ques: 问题
        :return: 回答
        """
        prompt = """{question}
        """
        prompt_template = PromptTemplate(template=prompt, input_variables=["question"])
        chain = ChainModel.get_instance_with_llm_chain(prompt_template=prompt_template)
        answer = chain.predict(question=ques)
        logger.info("ChatPublicDomain INFO[Chat] request_id={}, 问题=[{}], 回答结果=[{}].", self.request_id, ques, answer)
        return answer
