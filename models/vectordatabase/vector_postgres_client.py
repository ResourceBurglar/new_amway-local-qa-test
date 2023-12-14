import uuid
from typing import List, Tuple, Dict, Any

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from models.vectordatabase.custom.custom_pgvector import PGVector, DistanceStrategy, EmbeddingStore
from loguru import logger

from config.base_config import *
from framework.business_except import BusinessException
from models.embeddings.es_model_adapter import EmbeddingsModelAdapter
from models.vectordatabase.base_vector_client import BaseVectorClient


class VectorPostgresClient(BaseVectorClient):
    """
    Postgres向量库客户端
    """
    pgvector_driver: str = PGVECTOR_DRIVER
    pgvector_host: str = PGVECTOR_HOST
    pgvector_port: str = PGVECTOR_PORT
    pgvector_database: str = PGVECTOR_DATABASE
    pgvector_user: str = PGVECTOR_USER
    pgvector_password: str = PGVECTOR_PASSWORD

    def __get_db_conn(self):
        CONNECTION_STRING = PGVector.connection_string_from_db_params(
            driver=self.pgvector_driver,
            host=self.pgvector_host,
            port=self.pgvector_port,
            database=self.pgvector_database,
            user=self.pgvector_user,
            password=self.pgvector_password
        )
        return CONNECTION_STRING

    def delete_data(
            self,
            namespace: str = None,
            ids: list[str] = None,
            delete_all:
            bool = None,
            **kwargs
    ) -> Dict[str, Any]:
        embeddingsModelAdapter = EmbeddingsModelAdapter()
        embedding = embeddingsModelAdapter.get_model_instance()

        if delete_all:
            PGVector.from_existing_index(
                embedding=embedding,
                collection_name=namespace,
                connection_string=self.__get_db_conn(),
                distance_strategy=DistanceStrategy.COSINE,
                pre_delete_collection=False
            ).delete_collection()
        else:
            PGVector.from_existing_index(
                embedding=embedding,
                collection_name=namespace,
                connection_string=self.__get_db_conn(),
                distance_strategy=DistanceStrategy.COSINE,
                pre_delete_collection=False
            ).delete_embeddings(ids=ids)
        pass

    def query_data(
            self,
            namespace: str = None,
            ids: list[str] = None
    ) -> List[EmbeddingStore]:
        return PGVector.from_existing_index(
                embedding=EmbeddingsModelAdapter().get_model_instance(),
                collection_name=namespace,
                connection_string=self.__get_db_conn(),
                distance_strategy=DistanceStrategy.COSINE,
                pre_delete_collection=False
        ).query_embeddings(ids=ids)

    def insert_data(
            self,
            split_docs: List[Document],
            embedding: Embeddings,
            namespace: str
    ) -> list[str]:
        ids = [str(uuid.uuid4()).replace("-", "") for n in range(0, len(split_docs))]
        PGVector.from_documents(
            documents=split_docs,
            embedding=embedding,
            collection_name=namespace,
            connection_string=self.__get_db_conn(),
            distance_strategy=DistanceStrategy.COSINE,
            pre_delete_collection=False,
            ids=ids
        )
        return ids

    def search_data(
            self,
            ques: str,
            embedding: Embeddings,
            namespace: str,
            search_top_k: int
    ) -> List[Tuple[Document, float]]:
        store = PGVector.from_existing_index(
            embedding=embedding,
            collection_name=namespace,
            connection_string=self.__get_db_conn(),
            distance_strategy=DistanceStrategy.COSINE,
            pre_delete_collection=False
        )
        return store.similarity_search_with_score(query=ques, k=search_top_k)

    def get_vector_database_type(self) -> str:
        return 'Postgres'
