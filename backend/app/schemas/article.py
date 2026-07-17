from datetime import datetime

from pydantic import BaseModel


class ArticleListOut(BaseModel):
    """文章列表项 —— 列表页不返回全文 content，只返回摘要"""
    id: int
    title: str
    slug: str
    summary: str | None
    cover_url: str | None
    category_name: str | None
    category_slug: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ArticleDetailOut(BaseModel):
    """文章详情 —— 返回全文 content，用于阅读页"""
    id: int
    title: str
    slug: str
    content: str
    summary: str | None
    cover_url: str | None
    category_name: str | None
    category_slug: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
