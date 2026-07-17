import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.core.deps import get_db
from app.models.article import Article, ArticleTagLink
from app.models.tag import Tag
from app.schemas.tag import TagOut

router = APIRouter(prefix="/api/tags", tags=["公开-标签"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[TagOut])
def get_tags(db: Session = Depends(get_db)):
    """获取所有标签，同时统计每个标签下已发布文章数量"""
    logger.info("请求标签列表")

    rows = db.exec(
        select(
            Tag,
            func.count(Article.id).label("article_count"),
        )
        .join(ArticleTagLink, Tag.id == ArticleTagLink.tag_id, isouter=True)
        .join(Article, Article.id == ArticleTagLink.article_id, isouter=True)
        .where(
            (Article.is_published == True) | (Article.id == None)
        )
        .group_by(Tag.id)
        .order_by(Tag.id)
    ).all()

    return [
        TagOut(
            id=row[0].id,
            name=row[0].name,
            slug=row[0].slug,
            article_count=row[1],
        )
        for row in rows
    ]
