import os

DEFAULT_MODEL_NAME = \
    os.environ.get("AMWAY_EMBEDDING_MODEL_NAME") or "GanymedeNil/text2vec-large-chinese"
DEFAULT_MODEL_URL = "http://10.143.33.239:8003/embeddings"
# DEFAULT_MODEL_URL = "http://10.143.33.253:8001/embeddings"
# DEFAULT_MODEL_URL = \
#     os.environ.get("AMWAY_EMBEDDING_MODEL_URL") or "http://10.143.33.253:8001/embeddings"

HTTP_REQUEST_CONN_TIMEOUT = 3
HTTP_REQUEST_READ_TIMEOUT = 5
