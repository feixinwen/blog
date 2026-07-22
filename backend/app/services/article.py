import logging

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.article import Article, ArticleTagLink
from app.models.category import Category
from app.models.comment import Comment
from app.schemas.article import ArticleListOut
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)


def list_articles(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    category_slug: str | None = None,
    tag_slug: str | None = None,
) -> PaginatedResponse[ArticleListOut]:
    """文章列表（分页 + 分类/标签筛选），只返回已发布的文章"""

    # 评论数子查询
    comment_count_sub = (
        select(func.count(Comment.id))
        .where(Comment.article_id == Article.id, Comment.is_visible == True)
        .correlate(Article)
        .scalar_subquery()
        .label("comment_count")
    )

    # 基础查询：已发布文章 + 关联分类表 + 评论数
    query = (
        select(Article, Category.name, comment_count_sub)
        .join(Category, Article.category_id == Category.id, isouter=True)
        .where(Article.is_published == True)
    )

    # 按分类筛选
    if category_slug:
        query = query.where(Category.slug == category_slug)
        logger.info(f"按分类筛选文章: category_slug={category_slug}")

    # 按标签筛选：需要子查询拿到匹配的文章 ID
    if tag_slug:
        from app.models.tag import Tag

        matching_article_ids = (
            select(ArticleTagLink.article_id)
            .join(Tag, ArticleTagLink.tag_id == Tag.id)
            .where(Tag.slug == tag_slug)
        )
        query = query.where(Article.id.in_(matching_article_ids))
        logger.info(f"按标签筛选文章: tag_slug={tag_slug}")

    # 查询总条数（分页前先数一下共有多少条）
    total = db.exec(
        select(func.count()).select_from(query.subquery())
    ).one()

    # 分页 + 倒序排列
    query = query.order_by(Article.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size)
    rows = db.exec(query).all()

    # 把数据库查询结果转成 schema 对象
    items = [
        ArticleListOut(
            id=row[0].id,
            title=row[0].title,
            slug=row[0].slug,
            summary=row[0].summary,
            cover_url=row[0].cover_url,
            category_name=row[1],        # row[1] 是 Category.name
            category_slug=row[0].category.slug if row[0].category else None,
            read_count=row[0].read_count,
            comment_count=row[2] or 0,   # row[2] 是评论数（子查询）
            created_at=row[0].created_at,
        )
        for row in rows
    ]

    logger.info(f"查询文章列表: page={page}, page_size={page_size}, total={total}")

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
