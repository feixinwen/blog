from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Text as SAText
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.article import Article


class Comment(SQLModel, table=True):
    """评论表 —— 游客无需登录即可发表"""
    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="articles.id")
    author_name: str = Field(max_length=50)
    author_email: str = Field(max_length=100)
    content: str = Field(sa_type=SAText)  # TEXT 类型
    is_visible: bool = Field(default=True)  # 博主可设为 False 即删除
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    # 关系：通过 comment.article 拿到所属文章对象
    article: Optional["Article"] = Relationship(back_populates="comments")
