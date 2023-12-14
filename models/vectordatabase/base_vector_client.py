from abc import ABC, abstractmethod
from typing import (Dict, Any, List, Tuple)
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from models.vectordatabase.custom.custom_pgvector import EmbeddingStore


class BaseVectorClient(ABC):
    """
    向量库客户端
    """
    @abstractmethod
    def delete_data(
            self,
            namespace: str = None,
            ids: list[str] = None,
            delete_all: bool = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        删除向量数据
        :param namespace: 命名空间标识
        :param ids: 向量标识
        :param delete_all: 是否全部删除
        :param kwargs: 扩展参数
        :return: 未删除成功的ids
        """
        pass

    @abstractmethod
    def query_data(
            self,
            namespace: str = None,
            ids: list[str] = None,
    ) -> List[EmbeddingStore]:
        """
        删除向量数据
        :param namespace: 命名空间标识
        :param ids: 向量标识
        :return: 未删除成功的ids
        """
        pass

    @abstractmethod
    def insert_data(
            self,
            split_docs: List[Document],
            embedding: Embeddings,
            namespace: str) -> list[str]:
        """
        添加向量数据
        :param split_docs: 分割文件集
        :param embedding: 稀疏值类型
        :param namespace: 命名空间标识
        :return: 向量索引信息
        """
        pass

    @abstractmethod
    def search_data(
            self,
            ques: str,
            embedding: Embeddings,
            namespace: str,
            search_top_k: int) -> List[Tuple[Document, float]]:
        """
        搜索向量数据
        :param ques: 问题
        :param embedding: 稀疏值类型
        :param namespace: 命名空间标识
        :param search_top_k: top数
        :return: Chunk文档集合
        """
        pass

    @abstractmethod
    def get_vector_database_type(self) -> str:
        """
        获取向量库的类型名称
        :return: 类型名称
        """
        pass
