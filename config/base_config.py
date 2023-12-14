import os

# 底座大模型
DEFAULT_LLM = os.environ.get("DEFAULT_LLM") or "OpenAI"
CURRENT_LLM = "ChatGLM" or DEFAULT_LLM

# OpenAI配置
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_TEMPERATURE = 0
OPENAI_OUTPUT_TOKEN_LENGTH = 1024
OPENAI_MODEL_NAME = "gpt-3.5-turbo"

# 向量配置
VECTOR_DATABASE_TYPE = os.environ.get("VECTOR_DATABASE_TYPE") or "Postgres"
VECTOR_EMBEDDINGS_MODEL = os.environ.get("VECTOR_EMBEDDINGS_MODEL") or "OpenAI"
VECTOR_EMBEDDINGS_MODEL_TYPE = os.environ.get("VECTOR_EMBEDDINGS_MODEL_TYPE") or "text-embedding-ada-002"

# Pinecone配置
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_API_ENV = os.environ.get("PINECONE_API_ENV")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")

# Postgres配置
PGVECTOR_DRIVER = "psycopg2"
PGVECTOR_HOST = "10.143.17.179"
PGVECTOR_PORT = "5432"
PGVECTOR_DATABASE = "bespin_chat_qa"
PGVECTOR_USER = "bespin_chat_qa"
PGVECTOR_PASSWORD = "nDqeQ-vixYl1"
PGVECTOR_DIMENSIONS = 1024

# Mysql配置
MYSQL_HOST = "10.140.208.169"
MYSQL_PORT = 3306
MYSQL_CHARSET = "utf8mb4"
MYSQL_DATABASE = "bespin_chat"
MYSQL_USER = "bespin_chat"
MYSQL_PASSWD = "fCVGkU%2DD23mgPKe"

# 上传文件临时目录
CONTENT_PATH = os.environ.get("CONTENT_PATH") or 'D:\\workspaceGit\\content\\'
# Chunk块默认长度
SPLIT_LENGTH_FUNCTION = None
# Chunk块默认大小
SPLIT_CHUNK_SIZE = 2500
# Chunk类型
SPLIT_CHUNK_TYPE = "stuff"
# Chunk块默认重叠值
SPLIT_CHUNK_OVERLAP = 5
# 常规默认匹配最近N条矢量数据
VECTOR_SEARCH_TOP_K = 2
# 语义搜索阈值
VECTOR_SEARCH_SCORE = 0.3
# 长程记忆配置信息
MEMORY_LIMIT_SIZE = 2
# 文件向量化定时任务间隔频率,单位秒
SCHEDULES_ENABLED = True
if os.environ.get("SCHEDULES_ENABLED") == 'False':
    SCHEDULES_ENABLED = False
SCHEDULES_RATE_SECOND = 10
SCHEDULES_FILE_RETRY_COUNT = 3
SCHEDULES_FILE_LIMIT_COUNT = 5

ANSWER_SCENE_SUFFIX = "\n\n请问是否发起申请？(是/否)"
