import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.deps import get_current_user, get_db
from app.models.article import Article, ArticleTagLink
from app.models.user import User
from app.schemas.article import ArticleDetailOut
from app.schemas.article_admin import ArticleCreate, ArticleUpdate

router = APIRouter(prefix="/api/admin/articles", tags=["后台-文章"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[ArticleDetailOut])
def admin_list_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """后台文章列表 —— 返回所有文章，包括未发布的"""
    logger.info(f"管理员 {current_user.username} 请求文章管理列表")

    articles = db.exec(
        select(Article).order_by(Article.created_at.desc())
    ).all()

    result = []
    for article in articles:
        result.append(
            ArticleDetailOut(
                id=article.id,
                title=article.title,
                slug=article.slug,
                content=article.content,
                summary=article.summary,
                cover_url=article.cover_url,
                category_name=article.category.name if article.category else None,
                category_slug=article.category.slug if article.category else None,
                created_at=article.created_at,
                updated_at=article.updated_at,
            )
        )
    return result


@router.post("", response_model=ArticleDetailOut, status_code=201)
def admin_create_article(
    body: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """新建文章"""
    logger.info(
        f"管理员 {current_user.username} 创建文章: title={body.title}, slug={body.slug}"
    )

    # 检查 slug 是否已存在
    existing = db.exec(
        select(Article).where(Article.slug == body.slug)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"文章标识 '{body.slug}' 已存在，请换一个",
        )

    article = Article(
        title=body.title,
        slug=body.slug,
        content=body.content,
        summary=body.summary,
        cover_url=body.cover_url,
        category_id=body.category_id,
        is_published=body.is_published,
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    # 关联标签
    for tag_id in body.tag_ids:
        link = ArticleTagLink(article_id=article.id, tag_id=tag_id)
        db.add(link)
    db.commit()

    logger.info(f"文章创建成功: id={article.id}, slug={article.slug}")
    return _to_detail(article)


@router.put("/{article_id}", response_model=ArticleDetailOut)
def admin_update_article(
    article_id: int,
    body: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """编辑文章"""
    logger.info(f"管理员 {current_user.username} 编辑文章: id={article_id}")

    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 只更新传了值的字段
    update_data = body.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    for key, value in update_data.items():
        setattr(article, key, value)

    article.updated_at = datetime.now(timezone.utc)

    # 如果传了标签列表，则替换关联的标签
    if tag_ids is not None:
        # 删掉旧关联
        db.exec(
            select(ArticleTagLink).where(ArticleTagLink.article_id == article_id)
        ).delete()  # type: ignore
        # 建新关联
        for tag_id in tag_ids:
            db.add(ArticleTagLink(article_id=article.id, tag_id=tag_id))

    db.add(article)
    db.commit()
    db.refresh(article)

    logger.info(f"文章编辑成功: id={article_id}")
    return _to_detail(article)


@router.delete("/{article_id}", status_code=204)
def admin_delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除文章"""
    logger.info(f"管理员 {current_user.username} 删除文章: id={article_id}")

    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="文章不存在")

    db.delete(article)
    db.commit()

    logger.info(f"文章已删除: id={article_id}")


def _to_detail(article: Article) -> ArticleDetailOut:
    """把 Article 对象转成详情 schema（复用）"""
    return ArticleDetailOut(
        id=article.id,
        title=article.title,
        slug=article.slug,
        content=article.content,
        summary=article.summary,
        cover_url=article.cover_url,
        category_name=article.category.name if article.category else None,
        category_slug=article.category.slug if article.category else None,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )
