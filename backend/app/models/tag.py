from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Tag(SQLModel, table=True):
    """标签表"""
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True)
    slug: str = Field(max_length=50, unique=True, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
