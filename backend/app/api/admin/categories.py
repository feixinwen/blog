import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.deps import get_current_user, get_db
from app.models.category import Category
from app.models.user import User

router = APIRouter(prefix="/api/admin/categories", tags=["后台-分类"])
logger = logging.getLogger(__name__)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    slug: str = Field(min_length=1, max_length=50)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    slug: str | None = Field(default=None, max_length=50)


@router.get("")
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.exec(select(Category).order_by(Category.id)).all()


@router.post("", status_code=201)
def create_category(
    body: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"管理员 {current_user.username} 创建分类: {body.name}")

    exist = db.exec(select(Category).where(Category.slug == body.slug)).first()
    if exist:
        raise HTTPException(409, detail="分类标识已存在")

    category = Category(name=body.name, slug=body.slug)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}")
def update_category(
    category_id: int,
    body: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(404, detail="分类不存在")

    data = body.model_dump(exclude_unset=True)
    if "slug" in data:
        exist = db.exec(
            select(Category).where(
                Category.slug == data["slug"], Category.id != category_id
            )
        ).first()
        if exist:
            raise HTTPException(409, detail="分类标识已存在")

    for key, value in data.items():
        setattr(category, key, value)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"管理员 {current_user.username} 删除分类: id={category_id}")

    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(404, detail="分类不存在")

    db.delete(category)
    db.commit()
