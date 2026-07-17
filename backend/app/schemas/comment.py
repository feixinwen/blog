from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CommentCreate(BaseModel):
    """游客发表评论的请求体"""
    article_id: int
    author_name: str = Field(min_length=1, max_length=50)
    author_email: EmailStr          # Pydantic 自动校验邮箱格式
    content: str = Field(min_length=1, max_length=5000)


class CommentOut(BaseModel):
    """评论列表返回的响应"""
    id: int
    article_id: int
    author_name: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
