from pydantic import BaseModel
from typing import Optional


class QueryResponse(BaseModel):
    """
    接口返回结构体
    """
    status: Optional[int] = 0
    message: str = None
    data: object = None

