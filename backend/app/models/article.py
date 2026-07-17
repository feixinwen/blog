from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Text as SAText
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.comment import Comment


class ArticleTagLink(SQLModel, table=True):
    """
    文章和标签的多对多中间表。
    比如一篇文章打上 3 个标签，这张表存 3 行关联记录。
    """
    __tablename__ = "article_tags"

    article_id: int = Field(foreign_key="articles.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


class Article(SQLModel, table=True):
    """文章表"""
    __tablename__ = "articles"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    slug: str = Field(max_length=200, unique=True, index=True)
    content: str = Field(sa_type=SAText)  # TEXT 类型，存 Markdown 全文
    summary: Optional[str] = Field(default=None, sa_type=SAText)  # TEXT 类型
    cover_url: Optional[str] = Field(default=None, max_length=500)
    is_published: bool = Field(default=True)

    # 外键：每篇文章属于一个分类
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    # 关系：可以通过 article.category 直接拿到分类对象
    category: Optional["Category"] = Relationship(back_populates="articles")

    # 关系：通过 article.comments 拿到该文章所有评论
    comments: list["Comment"] = Relationship(back_populates="article")
