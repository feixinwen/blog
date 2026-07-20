from datetime import datetime

from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    """新建文章请求体"""
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    summary: str | None = None
    cover_url: str | None = None
    category_id: int | None = None
    tag_ids: list[int] = []  # 关联的标签 ID 列表
    is_published: bool = True


class ArticleUpdate(BaseModel):
    """编辑文章请求体 —— 所有字段可选，传什么更新什么"""
    title: str | None = Field(default=None, max_length=200)
    slug: str | None = Field(default=None, max_length=200)
    content: str | None = None
    summary: str | None = None
    cover_url: str | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None  # None 表示不修改标签
    is_published: bool | None = None


class ArticleAdminDetail(BaseModel):
    """后台文章详情 —— 包含编辑需要的所有字段"""
    id: int
    title: str
    slug: str
    content: str
    summary: str | None
    cover_url: str | None
    category_id: int | None
    category_name: str | None
    tag_ids: list[int]
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
