## 依赖管理
```
## pip install pipreqs
pipreqs . --encoding=utf8 --force
```

## 部署指引
### 构建镜像
```
docker build -t bespin/bespin-local-qa:{tag} .
```
### 测试环境部署命令
```
### 运行容器实例
docker_ run -m 512m --restart=always --privileged=true -itd -p8063:8063 -v/tmp:/tmp -v/home/bespin-local-qa:/app/bespin-local-qa -w/app/bespin-local-qa/ \
 -e DEFAULT_LLM="OpenAI" \
 -e SCHEDULES_ENABLED="True" \
 -e OPENAI_API_KEY="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" \
 -e VECTOR_DATABASE_TYPE="Postgres" \
 -e VECTOR_EMBEDDINGS_MODEL="OpenAI" \
 -e VECTOR_EMBEDDINGS_MODEL_TYPE="text-embedding-ada-002" \
 -e PINECONE_API_KEY="b046df4e-ef4c-4d96-b861-86ad9e11af1b" \
 -e PINECONE_API_ENV="us-west4-gcp" \
 -e PINECONE_INDEX="bespin-member-gz" \
 -e PGVECTOR_DRIVER="psycopg2" \
 -e PGVECTOR_HOST="192.168.191.44" \
 -e PGVECTOR_PORT="5432" \
 -e PGVECTOR_DATABASE="bespin_chat" \
 -e PGVECTOR_USER="postgres" \
 -e PGVECTOR_PASSWORD="12456" \
 -e MYSQL_HOST="192.168.191.44" \
 -e MYSQL_PORT="3306" \
 -e MYSQL_CHARSET="utf8mb4" \
 -e MYSQL_DATABASE="bespin_chat" \
 -e MYSQL_USER="bespin_chat" \
 -e MYSQL_PASSWD="7DZ23JD2uU%2347e3N" \
 -e CONTENT_PATH="/app/bespin-local-qa/content/" \
 -e HTTP_PROXY="http://Jason1:4905@159.75.82.57:8088" \
 -e HTTPS_PROXY="http://Jason1:4905@159.75.82.57:8088" \
 -e NO_PROXY="localhost,127.0.0.1,docker-registry.somecorporation.com" \
 --name bespin-local-qa tuchuanhuhuhu/chuanhuchatgpt:latest \
 sh -c "pip install -r requirements.txt && python3 -u api.py 2>&1"
 
 
### 进入实例内部
docker exec -it bespin-local-qa /bin/bash

### 安装相关依赖
cd bespin-local-qa
pip install -r requirements.txt

### 后台运行程序
nohup python api.py &
```




### 安利环境部署命令
```
### 运行容器实例
docker run -m 512m --restart=always --privileged=true -itd -p8063:8063 -v/nas:/nas -v/app/bespin-local-qa:/app/bespin-local-qa -w/app/bespin-local-qa/\
 -e DEFAULT_LLM="Moss" \
 -e MOSS_API_URL="http://10.143.33.253:19324" \
 -e AMWAY_EMBEDDING_MODEL_NAME="GanymedeNil/text2vec-large-chinese" \
 -e AMWAY_EMBEDDING_MODEL_URL="http://10.143.33.252:8001/embeddings" \
 -e SCHEDULES_ENABLED="True" \
 -e OPENAI_API_KEY="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" \
 -e VECTOR_DATABASE_TYPE="Postgres" \
 -e VECTOR_EMBEDDINGS_MODEL="AmwayMoss" \
 -e VECTOR_EMBEDDINGS_MODEL_TYPE="text-embedding-ada-002" \
 -e PINECONE_API_KEY="b046df4e-ef4c-4d96-b861-86ad9e11af1b" \
 -e PINECONE_API_ENV="us-west4-gcp" \
 -e PINECONE_INDEX="bespin-member-gz" \
 -e PGVECTOR_DRIVER="psycopg2" \
 -e PGVECTOR_HOST="10.143.17.179" \
 -e PGVECTOR_PORT="5432" \
 -e PGVECTOR_DATABASE="bespin_chat" \
 -e PGVECTOR_USER="postgres" \
 -e PGVECTOR_PASSWORD="amwaypgml2" \
 -e MYSQL_HOST="10.143.17.185" \
 -e MYSQL_PORT="3306" \
 -e MYSQL_CHARSET="utf8mb4" \
 -e MYSQL_DATABASE="bespin_chat" \
 -e MYSQL_USER="bespin_chat" \
 -e MYSQL_PASSWD="cda3db18e695" \
 -e CONTENT_PATH="/nas/namespace/py_upload/" \
 -e NO_PROXY="*" \
 --name bespin-local-qa bespin/bot-py-api:latest \
 sh -c "python -u api.py 2>&1"

### 进入实例内部
docker exec -it bespin-local-qa /bin/bash

### 安装相关依赖
cd bespin-local-qa
pip install -r requirements.txt

### 后台运行程序
nohup python api.py &
```
