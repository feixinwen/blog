import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select

from app.core.deps import get_db
from app.models.article import Article
from app.models.category import Category
from app.models.comment import Comment
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
    """文章详情：根据 slug 获取文章全文，阅读数 +1"""
    logger.info(f"请求文章详情: slug={slug}")

    row = db.exec(
        select(Article, Category.name)
        .join(Category, Article.category_id == Category.id, isouter=True)
        .where(Article.slug == slug, Article.is_published == True)
    ).first()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在",
        )

    article = row[0]

    # 阅读数 +1
    article.read_count += 1
    db.add(article)
    db.commit()
    db.refresh(article)

    # 评论数
    comment_count = db.exec(
        select(func.count()).where(
            Comment.article_id == article.id, Comment.is_visible == True
        )
    ).one()

    # 上一篇（更早发布的）
    prev_article = db.exec(
        select(Article.slug, Article.title)
        .where(Article.is_published == True, Article.created_at < article.created_at)
        .order_by(Article.created_at.desc())
        .limit(1)
    ).first()

    # 下一篇（更晚发布的）
    next_article = db.exec(
        select(Article.slug, Article.title)
        .where(Article.is_published == True, Article.created_at > article.created_at)
        .order_by(Article.created_at.asc())
        .limit(1)
    ).first()

    return ArticleDetailOut(
        id=article.id,
        title=article.title,
        slug=article.slug,
        content=article.content,
        summary=article.summary,
        cover_url=article.cover_url,
        category_name=row[1],
        category_slug=article.category.slug if article.category else None,
        read_count=article.read_count,
        comment_count=comment_count,
        prev_slug=prev_article[0] if prev_article else None,
        prev_title=prev_article[1] if prev_article else None,
        next_slug=next_article[0] if next_article else None,
        next_title=next_article[1] if next_article else None,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )
