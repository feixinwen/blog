import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.core.deps import get_db
from app.models.article import Article
from app.models.category import Category
from app.schemas.category import CategoryOut

router = APIRouter(prefix="/api/categories", tags=["公开-分类"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    """获取所有分类，同时统计每个分类下已发布文章数量"""
    logger.info("请求分类列表")

    # 查询：分类 + 文章计数
    rows = db.exec(
        select(
            Category,
            func.count(Article.id).label("article_count"),
        )
        .join(Article, Article.category_id == Category.id, isouter=True)
        .where(
            (Article.is_published == True) | (Article.id == None)
        )
        .group_by(Category.id)
        .order_by(Category.id)
    ).all()

    return [
        CategoryOut(
            id=row[0].id,
            name=row[0].name,
            slug=row[0].slug,
            article_count=row[1],
        )
        for row in rows
    ]
