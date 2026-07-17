from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.article import Article


class Category(SQLModel, table=True):
    """文章分类表"""
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True)
    slug: str = Field(max_length=50, unique=True, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    # 反向关系：通过 category.articles 拿到该分类下所有文章
    articles: list["Article"] = Relationship(back_populates="category")
