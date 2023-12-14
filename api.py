# -*- coding: utf-8 -*-
import traceback
import uuid
import time
from typing import List, Tuple
import uvicorn
from starlette.responses import RedirectResponse
from fastapi import (FastAPI, File, UploadFile, Request, Body)
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from apscheduler.schedulers.background import BackgroundScheduler
from starlette.staticfiles import StaticFiles
from loguru import logger
from pathlib import Path
from custom.amway.aigc.face_chain_client import FaceChainClient
from custom.amway.aigc.infer_param import InferParam, FcInferParam
from custom.amway.aigc.service.aigc_service import AmwayAIGC
from custom.amway.aigc.train_param import TrainParam, FcTrainParam
from custom.amway.amway_config import SFT_SOURCE_PATH, SFT_TARGET_PATH, OCP_SCHEDULES_ENABLED, OCP_SCHEDULES_RATE_SECOND
from custom.amway.prepare.service.prepare_update_param import PrepareUpdateParam
from framework.business_code import ERROR_10207
from framework.business_except import BusinessException
from custom.amway.speech.service.speech_service import SpeechText
from custom.amway.prepare.service.prepare_services import NamespacePrepare, NamespacePrepareService
from service.bot_service import BotInitDomain
from service.chat_private_service import ChatPrivateDomain
from service.chat_public_service import ChatPublicDomain
from service.local_entity_service import (ChatBotDomain, ChatHistoryDomain, NamespaceDomain, NamespaceFileDomain)
from service.local_repo_service import LocalRepositoryDomain
from custom.amway.cvision.service.cvision_service import CvDomain
from service.namespace_file_schedule import reload_namespace_file
from service.ask_service import ask
from config.base_config import *
from config.loguru_config import init_log_config
from framework.api_model import QueryResponse
from models.vectordatabase.v_client import get_instance_client
from custom.amway.sft.service.sft_data_service import SftDataService
from service.tablespace_data_schedule import reload_online_count_predict

app = FastAPI(docs_url=None, redoc_url=None)
BASE_DIR = Path(__file__).resolve().parent
app.mount('/static', StaticFiles(directory=BASE_DIR /
          'framework'/'static'/'swagger-ui'), name='static')
scheduler = BackgroundScheduler()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Swagger
    :return:
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    """
    Swagger
    :return:
    """
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """
    Swagger
    :return:
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


@app.on_event('startup')
async def start_scheduler():
    """
    1.日志框架初始化配置
    2.定时任务初始化配置
    :return:
    """
    init_log_config()
    if SCHEDULES_ENABLED:
        scheduler.add_job(reload_namespace_file, 'interval', seconds=SCHEDULES_RATE_SECOND)
    if OCP_SCHEDULES_ENABLED:
        scheduler.add_job(reload_online_count_predict, 'interval', seconds=OCP_SCHEDULES_RATE_SECOND)
    if SCHEDULES_ENABLED or OCP_SCHEDULES_ENABLED:
        scheduler.start()


@app.on_event('shutdown')
async def stop_scheduler():
    """
    定时任务回收化配置
    :return:
    """
    if SCHEDULES_ENABLED:
        scheduler.shutdown()


@app.get('/')
async def document():
    """
    访问根目录时重定向至文档地址
    :return: None
    """
    return RedirectResponse(url="/docs")


@app.middleware("http")
async def _aop_info_(request: Request, call_next):
    """
    中间件: 请求日志埋点
    :param request: 请求
    :param call_next: 回调函数
    :return: Response
    """
    logger.info("###API###AOP#### Request Header={}, Url={}.", request.headers, request.url)
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info("###API###AOP#### Response Header={}.", response.headers)
    return response


@app.post(
    path="/knowledge-base/upload",
    tags=["KnowledgeBase:知识库模块"],
    summary="知识库上传文件",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
async def api_upload_file(
        user_file: UploadFile = File(...),
        namespace_id: str = None
) -> QueryResponse:
    """
    知识库上传文件\n
    :param user_file: 用户文件\n\n
    :param namespace_id: 知识库标识\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        # 上传文件保存至临时目录
        filepath = CONTENT_PATH + user_file.filename
        content = await user_file.read()
        print(user_file.filename)
        with open(filepath, 'wb') as f:
            f.write(content)
        print(f)
        # 向量标识
        ids = None
        if namespace_id:
            # 根据标识查询知识库信息
            namespaceModel = NamespaceDomain().find_by_id(namespace_id)
            if not namespaceModel:
                logger.error(f"[10001]未查询到所属知识库[{namespace_id}]信息")
                raise BusinessException(10001, "未查询到所属知识库信息")
            namespace = namespaceModel.namespace
            split_chunk_size = namespaceModel.chunk_size
            split_chunk_overlap = namespaceModel.chunk_overlap
            # 向本地知识库推送元数据
            localRepositoryDomain = LocalRepositoryDomain()
            ids = localRepositoryDomain.push(
                glob=user_file.filename,
                namespace=namespace,
                split_chunk_size=split_chunk_size,
                split_chunk_overlap=split_chunk_overlap
            )
        else:
            # 向本地知识库推送元数据
            localRepositoryDomain = LocalRepositoryDomain()
            ids = localRepositoryDomain.push(glob=user_file.filename)
        # 保存源文件信息
        namespaceFileDomain = NamespaceFileDomain()
        namespaceFileDomain.create(
            namespace_id=namespace_id,
            name=user_file.filename,
            path=CONTENT_PATH,
            type=user_file.content_type,
            size=str(user_file.size),
            remark="python",
            vector_ids=ids
        )
    except BusinessException as business_err:
        logger.error("###API###api_upload_file error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_upload_file error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/chat",
    tags=["Chat:聊天模块"],
    summary="聊天功能",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_chat(
        ques: str,
        namespace_id: str = None
) -> QueryResponse:
    """
    聊天功能\n
    :param ques: 问题\n
    :param namespace_id: 知识库标识\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        if namespace_id:
            response.data = ChatPrivateDomain(request_id).chat(ques=ques, namespace_id=namespace_id)
        else:
            response.data = ChatPublicDomain(request_id).chat(ques=ques)
    except BusinessException as business_err:
        logger.error("###API###api_chat error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_chat error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/chat/ask",
    tags=["Chat:聊天模块"],
    summary="领域知识问答接口",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_chat_ask(
        ques: str,
        bot_id: str,
        user_id: str = None,
        group_uuid: str = None,
) -> QueryResponse:
    """
    领域知识问答功能\n
    :param ques: 问题\n
    :param bot_id: 机器人标识\n
    :param user_id: 用户标识\n
    :param group_uuid: 会话分组标识\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    logger.info("###API###api_chat_ask info, request_id={} bot_id={}, user_id={}, ques={}",
                request_id, bot_id, user_id, ques)
    try:
        response.data = ChatPrivateDomain(request_id).ask(
            ques=ques,
            bot_id=bot_id,
            user_id=user_id,
            group_uuid=group_uuid,
        )
    except BusinessException as business_err:
        logger.error("###API###api_chat_ask error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_chat_ask error, requestId={}, err={}.", request_id, err)
        traceback.print_exc()
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/chat/public/ask",
    tags=["Chat:聊天模块"],
    summary="公共知识问答接口",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_chat_public_ask(
        ques: str,
        bot_id: str,
        user_id: str = None,
        group_uuid: str = None,
) -> QueryResponse:
    """
    公共知识问答功能\n
    :param ques: 问题\n
    :param bot_id: 机器人标识\n
    :param user_id: 用户标识\n
    :param group_uuid: 会话分组标识\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    logger.info("###API###api_chat_public_ask info, request_id={} bot_id={}, user_id={}, ques={}",
                request_id, bot_id, user_id, ques)
    try:
        response.data = ChatPublicDomain(request_id).ask(
            ques=ques,
            bot_id=bot_id,
            user_id=user_id,
            group_uuid=group_uuid,
        )
    except BusinessException as business_err:
        logger.error("###API###api_chat_public_ask error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_chat_public_ask error, requestId={}, err={}.", request_id, err)
        traceback.print_exc()
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/chat/ask-cv",
    tags=["Chat:聊天模块"],
    summary="简历问答接口",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_chat_ask_cv(
        ques: str,
        bot_id: str,
        num: int,
        user_id: str = None,
        namespace_id: str = None,
) -> QueryResponse:
    """
    简历问答接口\n
    :param ques: 问题\n
    :param bot_id: 机器人标识\n
    :param num: 筛选份数\n
    :param user_id: 用户标识\n
    :param namespace_id: 指定知识库标识\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        # 简历问答
        response.data = CvDomain(request_id=request_id).ask(
            ques=ques,
            bot_id=bot_id,
            num=num,
            user_id=user_id,
            namespace_id=namespace_id,
            request_id=request_id
        )
    except BusinessException as business_err:
        logger.error("###API###api_chat_ask_cv error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_chat_ask_cv error, requestId={}, err={}.", request_id, err)
        traceback.print_exc()
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/generate/speech",
    tags=["Generate:生成模块"],
    summary="生成演讲稿",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_generate_speech(
        ques: str,
        bot_id: str,
        namespace_id_business: str,
        namespace_id_style: str,
        user_id: str = None,
) -> QueryResponse:
    """
    生成演讲稿接口\n
    :param ques: 问题\n
    :param bot_id: 机器人标识\n
    :param user_id: 用户标识\n
    :param namespace_id_business: 业务背景知识库标识\n
    :param namespace_id_style: 风格背景知识库标识\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        speechText = SpeechText(
            ques=ques,
            bot_id=bot_id,
            user_id=user_id,
            namespace_id_business=namespace_id_business,
            namespace_id_style=namespace_id_style,
            request_id=request_id,
        )
        response.data = speechText.transform()
    except BusinessException as business_err:
        logger.error("###API###api_generate_speech error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_generate_speech error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/chat/ask-upload-file",
    tags=["Chat:聊天模块"],
    summary="附件问答接口",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
async def api_chat_ask_upload_file(
        ques: str,
        chain_type: str,
        user_file: UploadFile = File(...)
) -> QueryResponse:
    """
    附件问答接口\n
    :param chain_type: 类型\n
    :param ques: 问题\n
    :param user_file: 用户文件\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        # 上传文件保存至临时目录
        filepath = CONTENT_PATH + user_file.filename
        content = await user_file.read()
        print(user_file.filename)
        with open(filepath, 'wb') as f:
            f.write(content)
        print(f)
        # 问答服务
        response.data = ask(
            ques=ques,
            glob=user_file.filename,
            chain_type=chain_type,
        )
    except BusinessException as business_err:
        logger.error("###API###api_chat_ask_upload_file error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_chat_ask_upload_file error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/chat/history",
    tags=["Chat:聊天模块"],
    summary="查询指定用户的历史聊天记录",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_chat_history(
        bot_id: str,
        user_id: str,
) -> QueryResponse:
    """
    查询指定用户的历史聊天记录\n
    :param bot_id: 机器人标识\n
    :param user_id: 用户标识\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        # 根据标识查询机器人配置信息
        chatBotModel = ChatBotDomain().find_one(bot_id=bot_id)
        # 查询历史聊天记录
        chatHistoryDomain = ChatHistoryDomain()
        history = chatHistoryDomain.find_all_by_id(user_id=user_id, bot_id=bot_id)
        data = {
            "bot": chatBotModel,
            "history": history
        }
        response.data = data
    except BusinessException as business_err:
        logger.error("###API###api_chat_history error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_chat_history error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/bot/public/init",
    tags=["Bot:机器人模块"],
    summary="初始化公共知识机器人",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_init_public_bot() -> QueryResponse:
    """
    初始化公共知识机器人\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        BotInitDomain(request_id=request_id).init_bot_list()
    except BusinessException as business_err:
        logger.error("###API###api_init_public_bot error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_init_public_bot error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.get(
    path="/bot",
    tags=["Bot:机器人模块"],
    summary="查询机器人列表信息",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_get_bot(
        id: str = None,
        bot_id: str = None
) -> QueryResponse:
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        bot_list = ChatBotDomain(request_id=request_id).find_all(
            id=id,
            bot_id=bot_id,
        )
        response.data = {
            "bot_list_length": len(bot_list),
            "bot_list": bot_list
        }
    except BusinessException as business_err:
        logger.error("###API###api_get_bot error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_get_bot error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.get(
    path="/bot/{bot_id}",
    tags=["Bot:机器人模块"],
    summary="查询机器人详情信息",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_get_bot_info(
        bot_id: str,
) -> QueryResponse:
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        chatBotModel = ChatBotDomain(request_id=request_id).find_one(bot_id=bot_id)
        setattr(chatBotModel, "namespace", NamespaceDomain(request_id=request_id).find_by_id(namespace_id=chatBotModel.namespace_id))
        response.data = chatBotModel
    except BusinessException as business_err:
        logger.error("###API###api_get_bot_info error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_get_bot_info error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.get(
    path="/namespace",
    tags=["Namespace:知识库模块"],
    summary="查询知识库列表信息",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_get_namespace(
        id: str = None,
        user_id: str = None,
        type: str = None,
        name: str = None,
        namespace: str = None,
) -> QueryResponse:
    """
    查询全部知识库列表
    :param id: 主键标识
    :param user_id: 专属用户
    :param type: 知识库类型
    :param name: 知识库名称
    :param namespace: 知识库空间
    :return: 知识库列表
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        response.data = NamespaceDomain(request_id=request_id).find_all(
            id=id,
            user_id=user_id,
            type=type,
            name=name,
            namespace=namespace,
        )
    except BusinessException as business_err:
        logger.error("###API###api_get_namespace error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_get_namespace error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.get(
    path="/namespace/{namespace_id}",
    tags=["Namespace:知识库模块"],
    summary="查询知识库详情信息",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_get_namespace_info(
        namespace_id: str,
) -> QueryResponse:
    """
    查询知识库详情信息
    :param namespace_id: 主键标识
    :return: 知识库详情
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        response.data = NamespaceDomain(request_id=request_id).find_by_id(namespace_id=namespace_id)
        setattr(response.data, "file_list", NamespaceFileDomain(request_id=request_id).find_by_condition(namespace_id=namespace_id))
    except BusinessException as business_err:
        logger.error("###API###api_get_namespace_info error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_get_namespace_info error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.get(
    path="/namespace/{namespace_id}/file",
    tags=["Namespace:知识库模块"],
    summary="查询知识库所属文件列表",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_get_namespace_file(
        namespace_id: str,
) -> QueryResponse:
    """
    查询知识库所属文件列表
    :param namespace_id: 主键标识
    :return: 文件列表
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        response.data = NamespaceFileDomain(request_id=request_id).find_by_condition(namespace_id=namespace_id)
    except BusinessException as business_err:
        logger.error("###API###api_get_namespace_file error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_get_namespace_file error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.get(
    path="/namespace/{namespace_id}/file/{file_id}",
    tags=["Namespace:知识库模块"],
    summary="查询知识库所属的指定文件详情",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_get_namespace_file_info(
        namespace_id: str,
        file_id: str,
) -> QueryResponse:
    """
    查询知识库所属的指定文件详情
    :param namespace_id: 主键标识
    :param file_id: 文件标识
    :return: 文件详情信息
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        namespaceModel = NamespaceDomain(request_id=request_id).find_by_id(namespace_id=namespace_id)
        if not namespaceModel:
            return response

        namespaceFileModel = NamespaceFileDomain(request_id=request_id).find_by_id(file_id=file_id)
        if not namespaceFileModel:
            return response

        ids = str(namespaceFileModel.vector_ids).split(',') if namespaceFileModel.vector_ids else []
        vector_list = get_instance_client().query_data(namespace=namespaceModel.namespace, ids=ids)
        vector_list_result = [
            {
                "uuid": v.uuid,
                "collection_id": v.collection_id,
                "custom_id": v.custom_id,
                "document": v.document,
                "metadata": v.cmetadata
            }
            for v in vector_list
        ]
        response.data = namespaceFileModel
        setattr(response.data, "namespace", namespaceModel)
        setattr(response.data, "vector_list_length", len(vector_list_result))
        setattr(response.data, "vector_list", vector_list_result)
    except BusinessException as business_err:
        logger.error("###API###api_get_namespace_file_info error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_get_namespace_file_info error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/namespace/{namespace_id}/file/{file_id}",
    tags=["Namespace:知识库模块"],
    summary="删除知识库所属的指定文件向量数据",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_del_namespace_file_data(
        namespace_id: str,
        file_id: str,
        ids: list[str],
        is_want_deleted_file: bool = False,
) -> QueryResponse:
    """
    删除知识库所属的指定文件向量数据
    :param namespace_id: 主键标识\n
    :param file_id: 文件标识\n
    :param ids: 向量标识集合\n
    :param is_want_deleted_file: 是要删除整个文件\n
    :return: None
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        # 分别查询知识库和指定文件的信息
        namespaceModel = NamespaceDomain(request_id=request_id).find_by_id(namespace_id=namespace_id)
        namespaceFileModel = NamespaceFileDomain(request_id=request_id).find_by_id(file_id=file_id)
        if namespaceFileModel.namespace_id != namespace_id:
            logger.error("Namespace ERROR, [{}]指定文件[{}]所属知识库标识不匹配, DB[{}] PARAM[{}], request_id={}.",
                         ERROR_10207, file_id, namespaceFileModel.namespace_id, namespace_id, request_id)
            raise BusinessException(ERROR_10207.code, ERROR_10207.message)
        ids_model = str(namespaceFileModel.vector_ids).split(',') if namespaceFileModel.vector_ids else []
        # 是要删除整个文件
        if is_want_deleted_file:
            # 删除向量数据
            api_del_vector_namespace_data(namespace=namespaceModel.namespace, ids=ids_model)
            # 更新业务数据
            NamespaceFileDomain(request_id=request_id).update(
                file_id=int(file_id),
                vector_ids=[],
                vector_status='Done',
                vector_count=0,
                deleted=1 if is_want_deleted_file else 0,
            )
        else:
            # 删除向量数据
            api_del_vector_namespace_data(namespace=namespaceModel.namespace, ids=ids)
            ids_array = [i for i in ids_model if i not in ids]
            # 更新业务数据
            NamespaceFileDomain(request_id=request_id).update(
                file_id=int(file_id),
                vector_ids=ids_array,
                vector_status='Done',
                vector_count=0,
                deleted=1 if len(ids_array) == 0 else 0,
            )
    except BusinessException as business_err:
        logger.error("###API###api_del_namespace_file_data error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_del_namespace_file_data error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/vector/del/namespace",
    tags=["Vector:向量模块"],
    summary="删除命名空间的所有向量数据",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_del_vector_namespace(
        namespace: str
) -> QueryResponse:
    """
    删除命名空间的所有向量数据\n
    :param namespace: 命名空间\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        vector_client = get_instance_client()
        vector_client.delete_data(namespace=namespace, delete_all=True)
    except BusinessException as business_err:
        logger.error("###API###api_del_vector_namespace error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_del_vector_namespace error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/vector/del/namespace/data",
    tags=["Vector:向量模块"],
    summary="删除命名空间的指定向量数据",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_del_vector_namespace_data(
        namespace: str,
        ids: list[str],
) -> QueryResponse:
    """
    删除命名空间的指定向量数据\n
    :param namespace: 命名空间\n
    :param ids: 向量标识集合\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        logger.info("###API###api_del_vector_namespace_data INFO, requestId={}, ids={}", request_id, ids)
        if ids and len(ids) > 0 and ids[0] != 'None':
            vector_client = get_instance_client()
            vector_client.delete_data(namespace=namespace, ids=ids)
    except BusinessException as business_err:
        logger.error("###API###api_del_vector_namespace_data error, requestId={}, err={}.",
                     request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_del_vector_namespace_data error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/sft/init-data",
    tags=["SFT:微调模块"],
    summary="初始化生成SFT数据",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_init_sft_data(
        source_file_path: str = None,
        target_file_path: str = None,
) -> QueryResponse:
    """
    初始化生成SFT数据\n
    :param source_file_path: 需要微调的源文件目录
    :param target_file_path: 指定微调数据的存放目录
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        if not source_file_path:
            source_file_path = SFT_SOURCE_PATH
        if not target_file_path:
            target_file_path = SFT_TARGET_PATH
        service = SftDataService(
            source_file_path=source_file_path,
            target_file_path=target_file_path,
        )
        service.transform()
        logger.info("#########api_init_sft_data success! request_id={}", request_id)
    except BusinessException as business_err:
        logger.error("###API###api_init_sft_data error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_init_sft_data error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/sft/loader",
    tags=["SFT:微调模块"],
    summary="加载分析源文本数据",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_load_sft_data(
        source_file_path: str = None,
        target_file_path: str = None,
) -> QueryResponse:
    """
    加载分析源文本数据\n
    :param source_file_path: 需要微调的源文件目录
    :param target_file_path: 指定微调数据的存放目录
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        if not source_file_path:
            source_file_path = SFT_SOURCE_PATH
        if not target_file_path:
            target_file_path = SFT_TARGET_PATH
        service = SftDataService(
            source_file_path=source_file_path,
            target_file_path=target_file_path,
        )
        docs = service.reload()
        metadata = [doc.metadata for doc in docs]
        response.data = {
            "total": len(metadata),
            "metadata": metadata
        }
        logger.info("#########api_load_sft_data success! request_id={}, 文件总数=[{}], 元数据=[{}].",
                    request_id, len(metadata), metadata)
    except BusinessException as business_err:
        logger.error("###API###api_load_sft_data error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_load_sft_data error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/amway/prepare/upload",
    tags=["Amway:安利定制模块"],
    summary="知识库上传预制文件",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
async def api_prepare_upload(
        user_file: UploadFile = File(...),
        namespace_id: str = None,
        encoding: str = 'gb18030',
) -> QueryResponse:
    """
    知识库上传预制文件\n
    :param user_file: 预制文件路径
    :param namespace_id: 知识库标识\n
    :param encoding: 编码\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        # 上传文件保存至临时目录
        file_path = CONTENT_PATH + user_file.filename
        content = await user_file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        # 开始获取
        namespacePrepare = NamespacePrepare(
            path=CONTENT_PATH,
            file_type=user_file.content_type,
            file_path=file_path,
            file_name=user_file.filename,
            file_size=user_file.size,
            namespace_id=namespace_id,
            encoding=encoding,
            request_id=request_id,
        )
        namespacePrepare.transformer()
    except BusinessException as business_err:
        logger.error("###API###api_prepare_upload error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_prepare_upload error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/amway/prepare/insert",
    tags=["Amway:安利定制模块"],
    summary="知识库添加预制数据",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
async def api_prepare_insert(
        namespace_id: str,
        data_list: List[Tuple],
        remark: str = None,
) -> QueryResponse:
    """
    知识库添加预制数据\n
    :param namespace_id: 知识库标识\n
    :param data_list: 编码\n
    :param remark: 备注信息\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        # 开始获取
        namespacePrepare = NamespacePrepare(
            path=CONTENT_PATH,
            file_type="",
            file_path="",
            file_name="",
            file_size=0,
            namespace_id=namespace_id,
            scene="insert",
            data_list=data_list,
            remark=remark,
            request_id=request_id,
        )
        namespacePrepare.transformer()
    except BusinessException as business_err:
        logger.error("###API###api_prepare_insert error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_prepare_insert error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/amway/prepare/update",
    tags=["Amway:安利定制模块"],
    summary="知识库修改预制数据",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
async def api_prepare_update(
        namespace_id: str,
        file_id: str = None,
        file_name: str = "",
        file_path: str = "",
        file_type: str = "",
        file_size: str = "0",
        file_display_name: str = "",
        remark: str = None,
        data: PrepareUpdateParam = Body(...),
) -> QueryResponse:
    """
    知识库修改预制数据\n
    :param namespace_id: 知识库标识\n
    :param file_id: 文件标识\n
    :param file_name: 文件名称\n
    :param file_path: 文件路径\n
    :param file_type: 文件类型\n\n
    :param file_size: 文件大小\n
    :param file_size: 文件大小\n
    :param file_display_name: 文件显示名称\n
    :param remark: 备注信息\n
    :param data: 数据\n
    :return: QueryResponse
    """
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        namespacePrepareService = NamespacePrepareService(
            namespace_id=namespace_id,
            name=file_name,
            path=file_path,
            type=file_type,
            size=file_size,
            file_id=file_id,
            file_display_name=file_display_name,
            remark=remark,
            param=data,
            request_id=request_id,
        )
        namespacePrepareService.handle()
    except BusinessException as business_err:
        logger.error("###API###api_prepare_update error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_prepare_update error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/amway/aigc/train",
    tags=["Amway:安利定制模块"],
    summary="AIGC训练",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_aigc_train(
        data: TrainParam = Body(...),
) -> QueryResponse:
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        aigc = AmwayAIGC(request_id=request_id)
        aigc.train(param=data)
    except BusinessException as business_err:
        logger.error("###API###api_aigc_train error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_aigc_train error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/amway/aigc/infer",
    tags=["Amway:安利定制模块"],
    summary="AIGC推理",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
def api_aigc_infer(
        data: InferParam = Body(...),
) -> QueryResponse:
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        aigc = AmwayAIGC(request_id=request_id)
        response.data = {
            "target": aigc.infer(param=data)
        }
    except BusinessException as business_err:
        logger.error("###API###api_aigc_infer error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_aigc_infer error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/amway/aigc/fc/train",
    tags=["Amway:安利定制模块"],
    summary="AIGC-FC 训练",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
async def api_aigc_fc_train(
        data: FcTrainParam = Body(...),
) -> QueryResponse:
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        client = FaceChainClient()
        response.data = client.train(
            img64_list=data.img64_list,
            person_name=data.person_name,
        )
    except BusinessException as business_err:
        logger.error("###API###api_aigc_fc_train error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_aigc_fc_train error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


@app.post(
    path="/amway/aigc/fc/infer",
    tags=["Amway:安利定制模块"],
    summary="AIGC-FC 推理",
    response_model=QueryResponse,
    response_description="返回体对象[status:结果状态(0成功), message:错误信息, data:业务数据]",
)
async def api_aigc_fc_infer(
        data: FcInferParam = Body(...),
) -> QueryResponse:
    response = QueryResponse()
    request_id = str(uuid.uuid4())
    try:
        client = FaceChainClient()
        response.data = client.infer(
            style=data.style,
            person_name=data.person_name,
            num_generate=data.num_generate,
        )
    except BusinessException as business_err:
        logger.error("###API###api_aigc_fc_infer error, requestId={}, err={}.", request_id, business_err)
        response.message = business_err.message
        response.status = business_err.code
    except Exception as err:
        logger.error("###API###api_aigc_fc_infer error, requestId={}, err={}.", request_id, err)
        response.message = str(err)
        response.status = -1
    return response


if __name__ == "__main__":
    uvicorn.run(app='api:app', host="0.0.0.0", port=8063, reload=True, workers=100)
