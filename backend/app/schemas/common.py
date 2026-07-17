from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页响应，T 可以是任意类型"""
    items: list[T]
    total: int        # 总记录数，前端用 total / page_size 算总页数
    page: int         # 当前页码
    page_size: int    # 每页条数
