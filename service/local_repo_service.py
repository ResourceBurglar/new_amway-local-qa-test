# -*- coding: utf-8 -*-
import uuid
from typing import List, Tuple
from loguru import logger
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from config.base_config import *
from framework.business_code import ERROR_10208
from framework.business_except import BusinessException
from models.embeddings.es_model_adapter import EmbeddingsModelAdapter
from models.vectordatabase.v_client import get_instance_client


class LocalRepositoryDomain:
    """
    本地知识库问答模块
    """
    pinecone_api_key: str = PINECONE_API_KEY
    pinecone_api_env: str = PINECONE_API_ENV
    pinecone_index: str = PINECONE_INDEX
    doc_content_path: str = CONTENT_PATH

    def __init__(
            self,
            request_id: str = str(uuid.uuid4())
    ):
        """
        构造函数
        :param request_id: 请求唯一标识
        """
        self.request_id = request_id

    def push(self,
             glob: str,
             namespace: str = None,
             doc_content_path: str = CONTENT_PATH,
             split_chunk_size: int = SPLIT_CHUNK_SIZE,
             split_chunk_overlap: int = SPLIT_CHUNK_OVERLAP) -> list[str]:
        """
        向本地知识库推送元数据
        :param doc_content_path: 元数据目录地址
        :param split_chunk_overlap: Chunk字符重叠值
        :param split_chunk_size: Chunk长度
        :param glob: 文件名称
        :param namespace: 知识库标识
        :return: None
        """
        doc_content_path = doc_content_path or self.doc_content_path
        docs = self.loader(glob=glob, doc_content_path=doc_content_path)
        print(f"####解析的文档数量有：{len(docs)}")
        print(f"####第一个文档长度有：{len(docs[0].page_content)}")

        split_chunk_size = split_chunk_size or SPLIT_CHUNK_SIZE
        split_chunk_overlap = split_chunk_overlap or SPLIT_CHUNK_OVERLAP
        if split_chunk_size == -1:
            total_length = 0
            for _doc in docs:
                total_length = total_length + len(_doc.page_content)
            print(f"############total_length={total_length}########split_chunk_overlap={split_chunk_overlap}######")
            split_chunk_size = total_length/split_chunk_overlap
        # 元数据切割处理
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=split_chunk_size,
            chunk_overlap=split_chunk_overlap
        )
        split_docs = text_splitter.split_documents(docs)
        print(f"####Chunk长度策略：", split_chunk_size)
        print(f"####Chunk重叠策略：", split_chunk_overlap)
        print(f"####切割后的文件数量有：{len(split_docs)}")
        # 保存元数据
        embeddingsModelAdapter = EmbeddingsModelAdapter()
        embedding = embeddingsModelAdapter.get_model_instance()
        vector_client = get_instance_client()
        ids = vector_client.insert_data(split_docs=split_docs, embedding=embedding, namespace=namespace)
        print(f"####切割后的文件ids有：", ids)
        return ids

    def loader(
            self,
            glob: str,
            doc_content_path: str,
    ) -> List[Document]:
        """
        文件加载
        :param glob: 文件名称
        :param doc_content_path: 目录地址
        :return: 加载结果
        """
        # 基本参数校验
        if not glob or not doc_content_path:
            logger.error("LocalRepositoryDomain loader ERROR, param is not legal, glob={}, doc_content_path={}, "
                         "request_id={}.", glob, doc_content_path, self.request_id)
            raise BusinessException(ERROR_10208.code, ERROR_10208.message)

        if ".pdf" in glob or ".PDF" in glob:
            # loader = PyPDFLoader(file_path=(doc_content_path + glob))
            loader = DirectoryLoader(path=doc_content_path, glob=str("**/"+glob))
            return loader.load()
        else:
            loader = DirectoryLoader(path=doc_content_path, glob=str("**/"+glob))
            return loader.load()

    def search(
            self,
            ques: str,
            namespace: str = None,
            vector_search_top_k: int = VECTOR_SEARCH_TOP_K,
    ) -> List[Tuple[Document, float]]:
        """
        本地知识库-语义搜索
        :param ques: 问题信息
        :param namespace: 向量库标识
        :param vector_search_top_k: 匹配数量
        :return: 向量库文档列表
        """
        embedding = EmbeddingsModelAdapter().get_model_instance()
        vector_client = get_instance_client()
        ques_docs = vector_client.search_data(
            ques=ques,
            embedding=embedding,
            namespace=namespace,
            search_top_k=vector_search_top_k
        )
        logger.info("####向量库查询结果，request_id={}, \n>>>匹配数: {} \n>>>文档数量: {} \n>>>文档内容: {} \n>>>用户问题: {}",
                    self.request_id, vector_search_top_k, len(ques_docs), ques_docs, ques)

        new_ques_docs = [
            (
                _doc,
                _score,
            )
            for _doc, _score in ques_docs if _score == float(0.0)
        ]

        new_ques_docs = new_ques_docs if len(new_ques_docs) > 0 else [
            (
                _doc,
                _score,
            )
            for _doc, _score in ques_docs if _score <= float(VECTOR_SEARCH_SCORE)
        ]
        logger.info("####阈值控制筛选结果，request_id={}, \n>>>阈值: {}, \n>>>文档数量: {}, \n>>>文档内容: {} \n>>>用户问题: {}",
                    self.request_id, float(VECTOR_SEARCH_SCORE), len(new_ques_docs), new_ques_docs, ques)
        return new_ques_docs
