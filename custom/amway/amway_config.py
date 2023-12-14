import os
# 安利定制化服务开关
AMWAY_ENABLED = True
# 预制文档回答功能开关
AMWAY_PREPARE_ANSWER = AMWAY_ENABLED and False
# 历史聊天记录定制开关
AMWAY_HISTORY_CUSTOM_ENABLED = AMWAY_ENABLED and True
AMWAY_HISTORY_CUSTOM_PREFIX_Q = " "
AMWAY_HISTORY_CUSTOM_PREFIX_A = " "
# 公共知识模型切换开关
AMWAY_CUS_ENABLED = AMWAY_ENABLED and False
AMWAY_CUS_REPLACE_ENABLED = AMWAY_CUS_ENABLED and True
AMWAY_CUS_REPLACE_CONTENT = {
    '我是百度公司开发的文心一言，英文名是ERNIE Bot': '我是通用大模型AI助手',
    '我是百度研发的知识增强大语言模型': '我是通用大模型AI助手',
    '我是百度公司开发的文心一言': '我是通用大模型AI助手',
    '我的英文名是ERNIE Bot': '我是通用大模型AI助手',
    '我是文心一言': '我是通用大模型AI助手',
    '我是百度公司': '我是Amway公司',
    'ERNIE Bot': '通用大模型AI助手',
    '文心一言': '通用大模型AI助手',
}
# 公共知识模型 - 千帆大模型
AMWAY_BAIDUBCE_ENABLED = AMWAY_CUS_ENABLED and True
# 公共知识模型 - 灵积大模型
AMWAY_DASHSCOPE_ENABLED = AMWAY_CUS_ENABLED and False
# 在线预测数据定时任务开关
OCP_SCHEDULES_ENABLED = True
OCP_SCHEDULES_RATE_SECOND = 43200
# SFT path info
SFT_SOURCE_PATH = os.environ.get("SFT_SOURCE_PATH") or 'D:\\workspaceGit\\content_sft\\source\\'
SFT_TARGET_PATH = os.environ.get("SFT_TARGET_PATH") or 'D:\\workspaceGit\\content_sft\\target\\'
# SFT outline
SFT_OUTLINE_SPLIT = os.environ.get("SFT_OUTLINE_SPLIT") or '\n'

# 千帆大模型平台API凭证
BAIDUBCE_API_KEY = "jqRTawAE8TIkTrGNZNnbelpw"
# 千帆大模型平台API密钥
BAIDUBCE_SECRET_KEY = "yZneTYhSXmwMDIE9QpTIDVBVYHjA5MxY"
# 千帆大模型平台获取token接口地址
BAIDUBCE_ACCESS_TOKEN_URL = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={BAIDUBCE_API_KEY}&client_secret={BAIDUBCE_SECRET_KEY}"
# 千帆大模型平台AI聊天接口地址
BAIDUBCE_CHAT_URL = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"
# BAIDUBCE_CHAT_URL = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token={access_token}"
# 千帆大模型平台，较高的数值会使输出更加随机，而较低的数值会使其更加集中和确定，默认0.95，范围 (0, 1.0]，不能为0
BAIDUBCE_TEMPERATURE = 0.5
# 千帆大模型平台，影响输出文本的多样性，取值越大，生成文本的多样性越强，默认0.8，取值范围 [0, 1.0]
BAIDUBCE_TOP_P = 0.8
# 千帆大模型平台，通过对已生成的token增加惩罚，减少重复生成的现象，值越大表示惩罚越大，默认1.0，取值范围：[1.0, 2.0]
BAIDUBCE_PENALTY_SCORE = 1.0
# 千帆大模型平台，安全问题话术
BAIDUBCE_SECURE_ANSWER = "用户输入存在安全风险，建议关闭当前会话，清理历史会话信息。"

# 百川AI配置
AI_BC_API_KEY = "baichuan-13B-chat"
AI_BC_TEMPERATURE = 0.2
AI_BC_OUTPUT_TOKEN_LENGTH = 4096
AI_BC_MODEL_NAME = "baichuan-13B-chat"
AI_BC_MODEL_BASE_URL = "http://10.143.33.252:8002/v1"

# LLM可选项：[OpenAI][BaiChuan][ChatGLM]
# 安利定制化场景-简历筛选场景的LLM配置
AMWAY_CVISION_CHOOSE_LLM = "ChatGLM3"
# 安利定制化场景-演讲稿草案生成的LLM配置
AMWAY_SPEECH_DRAFT_CHOOSE_LLM = "ChatGLM3"
# 安利定制化场景-演讲稿终稿生成的LLM配置
AMWAY_SPEECH_RESULT_CHOOSE_LLM = "ChatGLM3"
# 安利定制化场景-SFT数据-演讲稿摘要生成-所选模型类别
AMWAY_SFT_SPEECH_ABSTRACT_CHOOSE_LLM = "ChatGLM3"
# 安利定制化场景-SFT数据-演讲稿大纲生成-所选模型类别
AMWAY_SFT_SPEECH_OUTLINES_CHOOSE_LLM = "ChatGLM3"
# 安利定制化场景-SFT数据-演讲稿段落生成-所选模型类别
AMWAY_SFT_SPEECH_PARAGRAPH_CHOOSE_LLM = "ChatGLM3"

# 案例定制化场景-会议室预订系统开关
AMWAY_MEETING_ROOM_ENABLED = True
