# -*- coding: utf-8 -*-
import uuid
from typing import List
from loguru import logger
from config.base_config import *
import pymysql
from service.model.online_count_predict_model import OnlineCountPredictModel


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


class OnlineCountPredictDomain:
    """
    在线预测数据表
    """
    table_name: str = "dp_online_count_predict_df"

    def __init__(
            self,
            request_id: str = str(uuid.uuid4())
    ):
        self.request_id = request_id

    def find(
            self,
            limit_count: int = 14,
    ) -> List[OnlineCountPredictModel]:
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = f"select sale_date, max_online_cnt, online_count_pred " \
                      f"from {self.table_name} order by sale_date desc limit {limit_count} "
                cursor.execute(sql)
                data_list = cursor.fetchall()
                logger.info("Request_id={}, [{}]查询结果：{}, 数据长度：{}.", self.request_id, self.table_name, data_list, len(data_list))

                result_list = []
                for data in data_list:
                    result_list.append(OnlineCountPredictModel(data))
                return result_list
        except Exception as e:
            logger.error("Request_id={}, [{}]数据库操作异常, Message={}", self.request_id, self.table_name, e)
        finally:
            conn.close()
