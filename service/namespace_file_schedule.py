import datetime
from loguru import logger
from service.local_entity_service import NamespaceFileDomain, NamespaceDomain
from service.local_repo_service import LocalRepositoryDomain


def reload_namespace_file():
    """
    定时任务-本地知识库文件向量化处理
    :return: None
    """
    logger.info("###Reload_namespace_file###: {}.", datetime.datetime.now())
    namespaceFileDomain = NamespaceFileDomain()
    file_list = namespaceFileDomain.find_by_status_none()
    for fl in file_list:
        try:
            namespaceModel = NamespaceDomain().find_by_id(fl.namespace_id)
            namespace = namespaceModel.namespace
            split_chunk_size = namespaceModel.chunk_size
            split_chunk_overlap = namespaceModel.chunk_overlap
            # 向本地知识库推送元数据
            localRepositoryDomain = LocalRepositoryDomain()
            ids = localRepositoryDomain.push(
                glob=fl.name,
                doc_content_path=fl.path,
                namespace=namespace,
                split_chunk_size=split_chunk_size,
                split_chunk_overlap=split_chunk_overlap
            )
            # 成功场景: 同步更新至业务库-知识库表
            vector_count = int(fl.vector_count)
            namespaceFileDomain.update(
                file_id=fl.id,
                vector_ids=ids,
                vector_status='Done',
                vector_count=vector_count
            )
            logger.info("###Reload_namespace_file###向量化文件成功：文件名称[{}], 向量标识[{}].", fl.name, ids)
        except Exception as err:
            logger.error("###Reload_namespace_file###向量化文件失败：文件名称[{}], Message={}.", fl.name, err)
            # 失败场景: 同步更新至业务库-知识库表
            vector_count = int(fl.vector_count)+1
            namespaceFileDomain.update(
                file_id=fl.id,
                vector_ids=None,
                vector_status='Fail',
                vector_count=vector_count
            )
    pass
