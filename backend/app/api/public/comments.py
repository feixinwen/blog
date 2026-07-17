import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.deps import get_db
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentOut

router = APIRouter(prefix="/api/comments", tags=["公开-评论"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[CommentOut])
def get_comments(article_id: int, db: Session = Depends(get_db)):
    """获取某篇文章的所有可见评论（按时间正序）"""
    logger.info(f"请求评论列表: article_id={article_id}")

    comments = db.exec(
        select(Comment)
        .where(
            Comment.article_id == article_id,
            Comment.is_visible == True,
        )
        .order_by(Comment.created_at.asc())
    ).all()

    return comments


@router.post("", response_model=CommentOut, status_code=201)
def create_comment(body: CommentCreate, db: Session = Depends(get_db)):
    """游客发表评论 —— 无需登录，直接可见"""
    logger.info(
        f"新评论: article_id={body.article_id}, "
        f"author={body.author_name}, email={body.author_email}"
    )

    comment = Comment(
        article_id=body.article_id,
        author_name=body.author_name,
        author_email=body.author_email,
        content=body.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)  # 刷新后拿到数据库生成的 id 和 created_at

    return comment
