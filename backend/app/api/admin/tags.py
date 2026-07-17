import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.deps import get_current_user, get_db
from app.models.tag import Tag
from app.models.user import User

router = APIRouter(prefix="/api/admin/tags", tags=["后台-标签"])
logger = logging.getLogger(__name__)


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    slug: str = Field(min_length=1, max_length=50)


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    slug: str | None = Field(default=None, max_length=50)


@router.get("")
def list_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.exec(select(Tag).order_by(Tag.id)).all()


@router.post("", status_code=201)
def create_tag(
    body: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"管理员 {current_user.username} 创建标签: {body.name}")

    exist = db.exec(select(Tag).where(Tag.slug == body.slug)).first()
    if exist:
        raise HTTPException(409, detail="标签标识已存在")

    tag = Tag(name=body.name, slug=body.slug)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.put("/{tag_id}")
def update_tag(
    tag_id: int,
    body: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(404, detail="标签不存在")

    data = body.model_dump(exclude_unset=True)
    if "slug" in data:
        exist = db.exec(
            select(Tag).where(Tag.slug == data["slug"], Tag.id != tag_id)
        ).first()
        if exist:
            raise HTTPException(409, detail="标签标识已存在")

    for key, value in data.items():
        setattr(tag, key, value)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"管理员 {current_user.username} 删除标签: id={tag_id}")

    tag = db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(404, detail="标签不存在")

    db.delete(tag)
    db.commit()
