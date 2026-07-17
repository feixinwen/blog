import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.core.deps import get_db
from app.models.article import Article
from app.models.category import Category
from app.schemas.article import ArticleDetailOut, ArticleListOut
from app.schemas.common import PaginatedResponse
from app.services.article import list_articles

router = APIRouter(prefix="/api/articles", tags=["公开-文章"])
logger = logging.getLogger(__name__)


@router.get("", response_model=PaginatedResponse[ArticleListOut])
def get_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category_slug: str | None = Query(None),
    tag_slug: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """文章列表：支持分页、按分类 / 标签筛选"""
    logger.info(
        f"请求文章列表 page={page} page_size={page_size} "
        f"category={category_slug} tag={tag_slug}"
    )
    return list_articles(db, page, page_size, category_slug, tag_slug)


@router.get("/{slug}", response_model=ArticleDetailOut)
def get_article(slug: str, db: Session = Depends(get_db)):
    """文章详情：根据 slug 获取文章全文"""
    logger.info(f"请求文章详情: slug={slug}")

    # 关联查询：文章 + 分类
    article = db.exec(
        select(Article, Category.name)
        .join(Category, Article.category_id == Category.id, isouter=True)
        .where(Article.slug == slug, Article.is_published == True)
    ).first()

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在",
        )

    # article 是 (Article对象, Category.name字符串) 的元组
    row = article[0]  # Article 对象
    return ArticleDetailOut(
        id=row.id,
        title=row.title,
        slug=row.slug,
        content=row.content,
        summary=row.summary,
        cover_url=row.cover_url,
        category_name=article[1],  # 分类名来自 join
        category_slug=row.category.slug if row.category else None,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
