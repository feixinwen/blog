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
    read_count: int
    comment_count: int
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
    read_count: int
    comment_count: int
    prev_slug: str | None       # 上一篇 slug
    prev_title: str | None      # 上一篇标题
    next_slug: str | None       # 下一篇 slug
    next_title: str | None      # 下一篇标题
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
