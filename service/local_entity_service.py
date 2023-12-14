# -*- coding: utf-8 -*-
import uuid
from datetime import datetime
from typing import List
from loguru import logger
from config.base_config import *
import pymysql
from service.model.chat_bot_model import ChatBotModel
from service.model.chat_history_model import ChatHistoryModel
from service.model.chat_images_model import ChatImagesModel
from service.model.namespace_file_model import NamespaceFileModel
from service.model.namespace_model import NamespaceModel
from service.model.chat_meeting_model import ChatMeetingModel


def get_db_conn():
    """
    获取数据库连接对象
    :return: conn数据库连接对象
    """
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        database=MYSQL_DATABASE,
        charset=MYSQL_CHARSET,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWD
    )


class ChatBotDomain:
    """
    机器人模块
    """
    table_name: str = "ai_chat_bot"

    def __init__(
            self,
            request_id: str = str(uuid.uuid4())
    ):
        """
        构造函数
        :param request_id: 请求唯一标识
        """
        self.request_id = request_id

    def find_all(
            self,
            id: str = None,
            bot_id: str = None,
    ) -> List[ChatBotModel]:
        """
        查询所有机器人列表
        :param id: 主键标识
        :param bot_id: 机器人标识
        :return: 机器人列表
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = f"select bot_id, prompt, namespace_id, name, memory_limit_size, " \
                      f"welcome_tip, vector_top_k, chains_chunk_type, prompt_variables, " \
                      f"prefix_prompt, prefix_prompt_variables, bot_type, slave_bot_mark," \
                      f"fixed_ques, use_type, suffix_prompt, " \
                      f"id, deleted, creator, create_time, updator, update_time, version " \
                      f"from {self.table_name} where deleted = 0"
                if id:
                    sql = sql + f" and id = '{id}'"
                if bot_id:
                    sql = sql + f" and bot_id = '{bot_id}'"

                cursor.execute(sql)
                data_list = cursor.fetchall()
                logger.info("Request_id={}, [{}]查询结果：{}.", self.request_id, self.table_name, data_list)

                result_list = []
                for data in data_list:
                    result_list.append(ChatBotModel(data))
                return result_list
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()

    def find_one(
            self,
            bot_id: str
    ) -> ChatBotModel:
        """
        根据标识查询机器人配置信息
        :param bot_id: 机器人标识
        :return: 机器人Model
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = f"select bot_id, prompt, namespace_id, name, memory_limit_size, " \
                      f"welcome_tip, vector_top_k, chains_chunk_type, prompt_variables, " \
                      f"prefix_prompt, prefix_prompt_variables, bot_type, slave_bot_mark," \
                      f"fixed_ques, use_type, suffix_prompt, " \
                      f"id, deleted, creator, create_time, updator, update_time, version " \
                      f"from {self.table_name} where bot_id = '{bot_id}'"
                cursor.execute(sql)
                data = cursor.fetchone()
                logger.info("Request_id={}, [{}]查询结果：{}.", self.request_id, self.table_name, data)
                if data:
                    return ChatBotModel(data)
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()

    def create(
            self,
            bot_id: str,
            name: str,
            welcome_tip: str,
            prompt: str,
            prompt_variables: str,
            prefix_prompt: str = '',
            prefix_prompt_variables: str = '',
            suffix_prompt: str = '',
            namespace_id: str = "0",
            memory_limit_size: int = MEMORY_LIMIT_SIZE,
            vector_top_k: int = VECTOR_SEARCH_TOP_K,
            chains_chunk_type: str = SPLIT_CHUNK_TYPE,
            bot_type: str = "Master",
            slave_bot_mark: str = '',
            fixed_ques: str = '',
            use_type: int = 1
    ) -> int:
        """
        新增机器人
        :param bot_id: 机器人标识
        :param prompt: 提示词信息
        :param prompt_variables: 提示词变量
        :param prefix_prompt: 提示词前缀信息
        :param prefix_prompt_variables: 提示词前缀变量
        :param suffix_prompt: 提示词后缀信息
        :param namespace_id: 知识库标识
        :param name: 机器人名称
        :param memory_limit_size: 长程记忆长度
        :param welcome_tip: 机器人欢迎语
        :param vector_top_k: 语义搜索Top值
        :param chains_chunk_type: 问答链交互类型
        :param bot_type: 机器人类型
        :param slave_bot_mark: 从节点机器人标记
        :param fixed_ques: (Slave类型机器人)固定问题
        :param use_type: 机器人使用类型
        :return: 自增长序号
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                current_time = datetime.now()
                sql = f"insert into {self.table_name} " \
                      f"(deleted, " \
                      f"creator, " \
                      f"create_time, " \
                      f"updator, " \
                      f"update_time, " \
                      f"version, " \
                      f"bot_id, " \
                      f"prompt, " \
                      f"prompt_variables, " \
                      f"prefix_prompt, " \
                      f"prefix_prompt_variables, " \
                      f"suffix_prompt, " \
                      f"namespace_id, " \
                      f"name, " \
                      f"memory_limit_size, " \
                      f"welcome_tip, " \
                      f"vector_top_k, " \
                      f"chains_chunk_type, " \
                      f"bot_type, " \
                      f"slave_bot_mark, " \
                      f"fixed_ques, " \
                      f"use_type) " \
                      f"values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'," \
                      f"'%s','%s','%s','%s','%s','%s','%s','%s');" % \
                      ('0', 'system', current_time, 'system', current_time, '0',
                       bot_id, prompt, prompt_variables, prefix_prompt, prefix_prompt_variables, suffix_prompt,
                       namespace_id, name, memory_limit_size, welcome_tip, vector_top_k,
                       chains_chunk_type, bot_type, slave_bot_mark, fixed_ques, use_type)

                cursor.execute(sql.encode('utf-8'))
                conn.commit()
                logger.info("Request_id={}, [{}]保存成功!", self.request_id, self.table_name)
                return cursor.lastrowid
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
            return 0
        finally:
            conn.close()


class NamespaceDomain:
    """
    知识库模块
    """
    table_name: str = "ai_namespace"

    def __init__(
            self,
            request_id: str = str(uuid.uuid4())
    ):
        """
        构造函数
        :param request_id: 请求唯一标识
        """
        self.request_id = request_id

    def find_by_id(
            self,
            namespace_id: str
    ) -> NamespaceModel:
        """
        根据标识查询知识库信息
        :param namespace_id: 知识库/命名空间标识
        :return: 知识库Model
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = f"select namespace, name, remark, chunk_size, chunk_overlap, type, user_id, " \
                      f"id, deleted, creator, create_time, updator, update_time, version " \
                      f"from {self.table_name} where id = '{namespace_id}'"
                cursor.execute(sql)
                data = cursor.fetchone()
                logger.info("Request_id={}, [{}]查询结果：{}.", self.request_id, self.table_name, data)
                if data:
                    return NamespaceModel(data)
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
            return None
        finally:
            conn.close()

    def find_all(
            self,
            id: str = None,
            user_id: str = None,
            type: str = None,
            name: str = None,
            namespace: str = None,
    ) -> List[NamespaceModel]:
        """
        查询全部知识库列表
        :param id: 主键标识
        :param user_id: 专属用户
        :param type: 知识库类型
        :param name: 知识库名称
        :param namespace: 知识库空间
        :return: 知识库列表
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = f"select namespace, name, remark, chunk_size, chunk_overlap, type, user_id, " \
                      f"id, deleted, creator, create_time, updator, update_time, version " \
                      f"from {self.table_name} where deleted = 0"
                if id:
                    sql = sql + f" and id = '{id}'"
                if user_id:
                    sql = sql + f" and user_id = '{user_id}'"
                if type:
                    sql = sql + f" and type = '{type}'"
                if name:
                    sql = sql + f" and name = '{name}'"
                if namespace:
                    sql = sql + f" and namespace = '{namespace}'"
                cursor.execute(sql)
                data_list = cursor.fetchall()
                logger.info("Request_id={}, [{}]查询结果：{}.", self.request_id, self.table_name, data_list)

                result_list = []
                for data in data_list:
                    result_list.append(NamespaceModel(data))
                return result_list
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()


class NamespaceFileDomain:
    """
    知识库文件模块
    """
    table_name: str = "ai_namespace_file"

    def __init__(
            self,
            request_id: str = str(uuid.uuid4())
    ):
        """
        构造函数
        :param request_id: 请求唯一标识
        """
        self.request_id = request_id

    def create(
            self,
            namespace_id: str,
            name: str,
            display_name: str,
            path: str,
            type: str,
            size: str,
            vector_ids: list[str],
            remark: str = None
    ) -> int:
        """
        创建知识库文件信息
        :param namespace_id: 知识库标识
        :param name: 文件名称
        :param display_name: 文件显示名称
        :param path: 文件路径
        :param type: 文件类型
        :param size: 文件大小
        :param remark: 备注信息
        :param vector_ids: 向量标识
        :return: 自增长序号
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                path = path.replace("\\", "\\\\")
                vector_ids_str = ','.join(vector_ids)
                current_time = datetime.now()
                sql = f"insert into {self.table_name} " \
                      f"(deleted, " \
                      f"creator, " \
                      f"create_time, " \
                      f"updator, " \
                      f"update_time, " \
                      f"version, " \
                      f"namespace_id, " \
                      f"name, " \
                      f"display_name, " \
                      f"path, " \
                      f"type, " \
                      f"size, " \
                      f"remark, " \
                      f"vector_ids, " \
                      f"vector_status, " \
                      f"vector_count, " \
                      f"channel) " \
                      f"values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % \
                      ('0', 'system', current_time, 'system', current_time, '0',
                       namespace_id, name, display_name, path, type, size, remark, vector_ids_str, "Done", 0, 'python')

                cursor.execute(sql.encode('utf-8'))
                conn.commit()
                logger.info("Request_id={}, [{}]保存成功!", self.request_id, self.table_name)
                return cursor.lastrowid
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
            return 0
        finally:
            conn.close()

    def update(
            self,
            file_id: int,
            vector_ids: list[str],
            vector_status: str,
            vector_count: int,
            deleted: int = 0,
    ):
        """
        修改知识库文件信息
        :param file_id: 文件主键标识
        :param vector_ids: 向量标识
        :param vector_status: 向量化状态
        :param vector_count: 向量化重试次数
        :param deleted: 是否删除
        :return: None
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                vector_ids_str = None
                if vector_ids:
                    vector_ids_str = ','.join(vector_ids)
                current_time = datetime.now()
                sql = f"update {self.table_name} set " \
                      f"deleted = '{deleted}', " \
                      f"updator = 'system', " \
                      f"update_time = '{current_time}', " \
                      f"vector_ids = '{vector_ids_str}', " \
                      f"vector_status = '{vector_status}', " \
                      f"vector_count = {vector_count} " \
                      f"where id={file_id}; "
                cursor.execute(sql.encode('utf-8'))
                conn.commit()
                logger.info("Request_id={}, [{}]修改成功!", self.request_id, self.table_name)
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
            return None
        finally:
            conn.close()

    def find_by_condition(
            self,
            file_id: str = None,
            namespace_id: str = None,
            name: str = None,
            path: str = None,
            vector_ids: str = None,
            vector_status: str = None,
    ) -> List[NamespaceFileModel]:
        """
        查询知识库文件列表信息
        :param file_id: 文件标识
        :param namespace_id: 知识库标识
        :param name: 文件名称
        :param path: 文件地址
        :param vector_ids: 向量标识
        :param vector_status: 向量状态
        :return: 知识库文件列表
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = f"select id, namespace_id, name, path, type, size, remark, vector_ids, " \
                      f"vector_status, vector_count, channel, deleted, creator, create_time, updator, update_time, version, " \
                      f"display_name, md5 " \
                      f"from {self.table_name} where deleted = 0 "
                if file_id:
                    sql = sql + f" and id = '{file_id}'"
                if namespace_id:
                    sql = sql + f" and namespace_id = '{namespace_id}'"
                if name:
                    sql = sql + f" and name like '%{name}'%"
                if path:
                    sql = sql + f" and path = '{path}'"
                if vector_ids:
                    sql = sql + f" and vector_ids like '%{vector_ids}'%"
                if vector_status:
                    sql = sql + f" and vector_status = '{vector_status}'"
                cursor.execute(sql)
                data_list = cursor.fetchall()
                logger.info("Request_id={}, [{}]查询结果：{}, 数据长度：{}.", self.request_id, self.table_name, data_list, len(data_list))

                result_list = []
                for data in data_list:
                    result_list.append(NamespaceFileModel(data))
                return result_list
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()

    def find_by_id(
            self,
            file_id,
    ) -> NamespaceFileModel:
        """
        查询指定的知识库文件
        :param file_id: 文件标识
        :return: 文件列表
        """
        file_list = self.find_by_condition(file_id=file_id)
        return file_list[0] if len(file_list) > 0 else None

    def find_by_status_none(
            self
    ) -> List[NamespaceFileModel]:
        """
        查询未向量化的文件列表
        :return: 文件列表
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = f"select id, namespace_id, name, path, type, size, remark, vector_ids, " \
                      f"vector_status, vector_count, channel, deleted, creator, create_time, updator, update_time, version, " \
                      f"display_name, md5 " \
                      f"from {self.table_name} where vector_status != 'Done' " \
                      f"and vector_count < {SCHEDULES_FILE_RETRY_COUNT} " \
                      f"and deleted = 0 " \
                      f"order by create_time desc " \
                      f"limit {SCHEDULES_FILE_LIMIT_COUNT};"
                cursor.execute(sql)
                data_list = cursor.fetchall()
                logger.info("Request_id={}, [{}]查询结果：{}, 数据长度：{}.", self.request_id, self.table_name, data_list, len(data_list))

                result_list = []
                for data in data_list:
                    result_list.append(NamespaceFileModel(data))
                return result_list
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()

    def find_by_path(
            self,
            file_name: str,
            namespace_id: str
    ) -> NamespaceFileModel:
        """
        根据文件目录查询指定记录
        :param namespace_id: 命名空间标识
        :param file_name: 文件名称
        :return: 元文件信息
        """
        conn = get_db_conn()
        try:
            logger.info(f">>>>>>>>>>>>>>>>>>>>>根据文件目录查询指定记录：file_name={file_name}, namespace_id={namespace_id}")
            with conn.cursor() as cursor:
                sql = f"select id, namespace_id, name, path, type, size, remark, vector_ids, " \
                      f"vector_status, vector_count, channel, deleted, creator, create_time, updator, update_time, version, " \
                      f"display_name, md5 " \
                      f"from {self.table_name} " \
                      f"where name = '{file_name}' and namespace_id = '{namespace_id}' ; "
                cursor.execute(sql)
                data = cursor.fetchone()
                logger.info("Request_id={}, [{}]查询结果：{}.", self.request_id, self.table_name, data)
                if data:
                    return NamespaceFileModel(data)
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()


class ChatHistoryDomain:
    """
    历史聊天记录模块
    """
    table_name: str = "ai_chat_history"

    def __init__(
            self,
            request_id: str = str(uuid.uuid4())
    ):
        """
        构造函数
        :param request_id: 请求唯一标识
        """
        self.request_id = request_id

    def find_all_by_id(
            self,
            user_id: str,
            bot_id: str,
    ) -> List[ChatHistoryModel]:
        """
        根据用户标识查询所有历史
        :param user_id: 用户标识
        :param bot_id: 机器人标识
        :return: 历史聊天记录列表
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = f"select question, answer, user_id, bot_id, create_time, update_time, " \
                      f"deleted, creator, updator, answer_like, group_uuid from {self.table_name} " \
                      f"where deleted = 0 and bot_id = '{bot_id}' and user_id = '{user_id}'"
                cursor.execute(sql)
                data_list = cursor.fetchall()
                logger.info("Request_id={}, [{}]查询结果：{}, 数据长度：{}.", self.request_id, self.table_name, data_list, len(data_list))

                result_list = []
                for data in data_list:
                    result_list.append(ChatHistoryModel(data))
                return result_list
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()

    def find_last_by_id(
            self,
            user_id: str,
            bot_id: str = None,
            limit_size: int = 3
    ) -> List[ChatHistoryModel]:
        """
        根据用户标识查询最近指定范围历史记录
        :param user_id: 用户标识
        :param bot_id: 机器人标识
        :param limit_size: 指定范围
        :return: 历史聊天记录Model
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                if bot_id:
                    sql = f"select question, answer, user_id, bot_id, create_time, update_time, " \
                          f"deleted, creator, updator, answer_like, group_uuid from {self.table_name} " \
                          f"where deleted = 0 and (answer_like is null or answer_like = 'LIKE') and user_id = '{user_id}' and bot_id = '{bot_id}' " \
                          f"order by create_time desc limit {limit_size};"
                else:
                    sql = f"select question, answer, user_id, bot_id, create_time, update_time, " \
                          f"deleted, creator, updator, answer_like, group_uuid from {self.table_name} " \
                          f"where deleted = 0 and (answer_like is null or answer_like = 'LIKE')  and user_id = '{user_id}' " \
                          f"order by create_time desc limit {limit_size};"
                cursor.execute(sql)
                data_list = cursor.fetchall()
                logger.info("Request_id={}, [{}]查询结果：{}, 数据长度：{}.", self.request_id, self.table_name, data_list, len(data_list))

                result_list = []
                for data in data_list:
                    result_list.append(ChatHistoryModel(data))
                return result_list
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()

    def create(
            self,
            user_id: str,
            bot_id: str,
            question: str,
            answer: str,
            question_time: datetime = None,
            answer_time: datetime = None,
            deleted: int = 0,
            group_uuid: str = None,
    ) -> int:
        """
        创建历史聊天记录
        :param user_id: 用户标识信息
        :param bot_id: 机器人标识信息
        :param question: 提问
        :param answer: 回答
        :param question_time: 提问时间
        :param answer_time: 回答时间
        :param deleted: 是否标记删除
        :param group_uuid: 会话分组标识
        :return: 自增长序号
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                # 设置问答时间，若未指定则默认取当前时间
                current_time = datetime.now()
                question_time = question_time or current_time
                answer_time = answer_time or current_time

                answer = answer.replace("'", "\\'")
                question = question.replace("'", "\\'")

                sql = f"insert into {self.table_name} " \
                      f"(deleted, " \
                      f"creator, " \
                      f"create_time, " \
                      f"updator, " \
                      f"update_time, " \
                      f"version, " \
                      f"user_id, " \
                      f"bot_id, " \
                      f"question, " \
                      f"answer, " \
                      f"group_uuid) " \
                      f"values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % \
                      (deleted, 'system', question_time, 'system', answer_time, '0', user_id, bot_id, question, answer, group_uuid)

                cursor.execute(sql.encode('utf-8'))
                conn.commit()
                logger.info("Request_id={}, [{}]保存成功!", self.request_id, self.table_name)
                return cursor.lastrowid
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
            conn.rollback()
        finally:
            conn.close()


class ChatImagesDomain:

    table_name: str = "ai_chat_images"

    def __init__(
            self,
            request_id: str = str(uuid.uuid4())
    ):
        self.request_id = request_id

    def find_by_id(
            self,
            images_id: str
    ) -> ChatImagesModel:
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = f"select id, deleted, creator, create_time, updator, update_time, version, " \
                      f"user_id, source, target, answer_like, num, uuid, style, model, dir, status " \
                      f"from {self.table_name} where id = '{images_id}'"
                cursor.execute(sql)
                data = cursor.fetchone()
                logger.info("Request_id={}, [{}]查询结果：{}.", self.request_id, self.table_name, data)
                if data:
                    return ChatImagesModel(data)
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()

    def update(
            self,
            images_id: str,
            images_status: str,
            images_uuid: str,
            deleted: int = 0,
            targets: List[str] = None,
    ):
        conn = get_db_conn()
        try:
            targets = targets if targets else []
            with conn.cursor() as cursor:
                current_time = datetime.now()
                sql = f"update {self.table_name} set " \
                      f"deleted = '{deleted}', " \
                      f"updator = 'system', " \
                      f"update_time = '{current_time}', " \
                      f"status = '{images_status}', " \
                      f"uuid = '{images_uuid}', " \
                      f"target = '{','.join(targets)}' " \
                      f"where id={images_id}; "
                cursor.execute(sql.encode('utf-8'))
                conn.commit()
                logger.info("Request_id={}, [{}]修改成功!", self.request_id, self.table_name)
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()

            
            

class ChatMeetingRoomDomain:
    """
    会议室预订聊天记录模块
    """
    table_name: str = "meeting_chat_history"

    def __init__(
            self,
            request_id: str = str(uuid.uuid4())
    ):
        """
        构造函数
        :param request_id: 请求唯一标识
        """
        self.request_id = request_id

    def find_all_by_id(
            self,
            user_id: str,
            bot_id: str,
    ) -> List[ChatMeetingModel]:
        """
        根据用户标识查询所有历史
        :param user_id: 用户标识
        :param bot_id: 机器人标识
        :return: 历史聊天记录列表
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = f"select question, answer, user_id, bot_id, question_time, " \
                      f"answer_time, category, parameters group_id from {self.table_name} " \
                      f"where bot_id = '{bot_id}' and user_id = '{user_id}' and deleted = 0"
                cursor.execute(sql)
                data_list = cursor.fetchall()
                logger.info("Request_id={}, [{}]查询结果：{}, 数据长度：{}.", self.request_id, self.table_name, data_list, len(data_list))

                result_list = []
                for data in data_list:
                    result_list.append(ChatMeetingModel(data))
                return result_list
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()

    def find_last_by_id(
            self,
            user_id: str,
            bot_id: str = None,
            group_id: str = None,
            limit_size: int = 3,
            
    ) -> List[ChatMeetingModel]:
        """
        根据用户标识查询最近指定范围历史记录
        :param user_id: 用户标识
        :param bot_id: 机器人标识
        :param limit_size: 指定范围
        :return: 历史聊天记录Model
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                if bot_id:
                    sql = f"select question, answer, user_id, bot_id, question_time, " \
                          f"answer_time, category, parameters group_id from {self.table_name} " \
                          f"where user_id = '{user_id}' and bot_id = '{bot_id}' and group_id = '{group_id}' " \
                          f"and category = '{control_type}' and deleted = 0 " \
                          f"order by question_time desc limit {limit_size};"
                else:
                    sql = f"select question, answer, user_id, bot_id, question_time, " \
                          f"answer_time, category, parameters group_id from {self.table_name} " \
                          f"where user_id = '{user_id}' and group_id = '{group_id}' " \
                          f"and category = '{control_type}' deleted = 0 " \
                          f"order by question_time desc limit {limit_size};"
                cursor.execute(sql)
                data_list = cursor.fetchall()
                logger.info("Request_id={}, [{}]查询结果：{}, 数据长度：{}.", self.request_id, self.table_name, 
                            data_list, len(data_list))

                result_list = []
                for data in data_list:
                    result_list.append(ChatMeetingModel(data))
                return result_list
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()

    def create(
            self,
            user_id: str,
            bot_id: str,
            question: str,
            answer: str,
            category: int,
            parameters: str,
            group_id: str,
            question_time: datetime = None,
            answer_time: datetime = None,
            deleted: int = 0
    ) -> int:
        """
        创建历史聊天记录
        :param user_id: 用户标识信息
        :param bot_id: 机器人标识信息
        :param question: 提问
        :param answer: 回答
        :param question_time: 提问时间
        :param answer_time: 回答时间
        :return: 自增长序号
        """
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                # 设置问答时间，若未指定则默认取当前时间
                current_time = datetime.now()
                question_time = question_time or current_time
                answer_time = answer_time or current_time

                answer = answer.replace("'", "\\'")
                question = question.replace("'", "\\'")

                sql = f"insert into {self.table_name} " \
                      f"(question_time, " \
                      f"answer_time, " \
                      f"user_id, " \
                      f"bot_id, " \
                      f"question, " \
                      f"answer, " \
                      f"category, " \
                      f"parameters, " \
                      f"deleted, " \
                      f"group_id) " \
                      f"values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % \
                      (question_time, answer_time, user_id, bot_id, question, answer, category, parameters, deleted, group_id)

                cursor.execute(sql.encode('utf-8'))
                conn.commit()
                logger.info("Request_id={}, [{}]保存成功!", self.request_id, self.table_name)
                return cursor.lastrowid
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
            conn.rollback()
        finally:
            conn.close()