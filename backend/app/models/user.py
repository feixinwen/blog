from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    用户表 —— 目前只有一个博主。
    表名默认是类名的小写 `user`。
    """
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
