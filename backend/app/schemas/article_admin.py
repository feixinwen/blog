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
