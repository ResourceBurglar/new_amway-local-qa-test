import re
from datetime import datetime
from typing import Dict
from config.base_config import ANSWER_SCENE_SUFFIX
from content.filter_book import filter_history_list
from service.local_entity_service import ChatHistoryDomain


class BaseChatMessage:
    """
    聊天消息基础处理
    """
    @classmethod
    def purge_with_history(
            cls,
            ques: str,
            answer: str,
            bot_id: str,
            user_id: str,
            question_time: datetime = datetime.now(),
            chatHistoryDomain: ChatHistoryDomain = ChatHistoryDomain(),
            **kwargs
    ) -> Dict:
        """
        问答结果清洗并保留历史聊天记录
        :param ques: 问题
        :param answer: 回答
        :param bot_id: 机器人标识
        :param user_id: 用户标识
        :param question_time: 问答时间点
        :param chatHistoryDomain: 历史聊天记录实体服务类
        :return: 问答结果
        """
        # 敏感词|智能策略
        new_answer = cls.purge(answer=answer)
        # 保存历史聊天记录
        return cls.save_history_message(
            ques=ques,
            answer=new_answer,
            bot_id=bot_id,
            user_id=user_id,
            question_time=question_time,
            chatHistoryDomain=chatHistoryDomain,
            **kwargs,
        )

    @classmethod
    def purge(
            cls,
            answer: str,
    ) -> str:
        """
        问答结果清洗逻辑
        :param answer: 回答
        :return: 问答结果
        """
        # 智能策略 - 超链接格式处理
        url_pattern = "(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]"
        url_collection = re.findall(url_pattern, answer)
        for url in url_collection:
            answer = answer.replace(url, " "+url+" ")

        # 敏感词|智能策略
        new_answer = answer
        if "AI: " in answer:
            new_answer = answer.split("AI:")[1]
        elif "Answer: " in answer:
            new_answer = answer.split("Answer:")[1]
        elif "answer: " in answer:
            new_answer = answer.split("answer:")[1]
        elif "<|MOSS|>:" in answer:
            new_answer = answer.split("<|MOSS|>:")[1]
        elif "回答：" in answer:
            new_answer = answer.split("回答：")[1]
        elif "回答:" in answer:
            new_answer = answer.split("回答:")[1]
        return new_answer

    @classmethod
    def save_history_message(
            cls,
            ques: str,
            answer: str,
            bot_id: str,
            user_id: str,
            question_time: datetime = datetime.now(),
            chatHistoryDomain: ChatHistoryDomain = ChatHistoryDomain(),
            **kwargs
    ) -> Dict:
        """
        保存历史聊天记录
        :param ques: 问题
        :param answer: 回答
        :param bot_id: 机器人标识
        :param user_id: 用户标识
        :param question_time: 问答时间点
        :param chatHistoryDomain: 历史聊天记录实体服务类
        :return: 问答结果
        """
        scene = None
        group_uuid = None
        for k, v in kwargs.items():
            if k == "scene":
                scene = v
            if k == "group_uuid":
                group_uuid = v

        # 智能策略 - 历史记录过滤不满意内容
        is_want_save_history = True
        for cts in filter_history_list:
            if cts in answer:
                is_want_save_history = False
                break

        has_flag = cls.has_answer_scene_suffix(scene=scene)
        if user_id:
            deleted = 0 if is_want_save_history else 1
            history_id = chatHistoryDomain.create(
                user_id=user_id,
                bot_id=bot_id,
                question=ques,
                answer=answer,
                question_time=question_time,
                deleted=deleted,
                group_uuid=group_uuid,
            )
            return {
                "answer": answer if not has_flag else answer+ANSWER_SCENE_SUFFIX,
                "history_id": history_id,
                "scene": scene,
            }
        return {
            "answer": answer if not has_flag else answer+ANSWER_SCENE_SUFFIX,
            "history_id": 0,
            "scene": scene,
        }

    @staticmethod
    def has_answer_scene_suffix(scene: str) -> bool:
        if not scene or scene == "echart" or len(scene.strip()) == 0:
            return False
        return True
