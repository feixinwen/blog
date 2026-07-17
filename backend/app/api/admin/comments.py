import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.deps import get_current_user, get_db
from app.models.comment import Comment
from app.models.user import User

router = APIRouter(prefix="/api/admin/comments", tags=["后台-评论"])
logger = logging.getLogger(__name__)


@router.get("")
def list_all_comments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """后台查看所有评论（包括被隐藏的），按时间倒序"""
    return db.exec(
        select(Comment).order_by(Comment.created_at.desc())
    ).all()


@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """软删除评论 —— 设为不可见，不物理删除数据"""
    logger.info(f"管理员 {current_user.username} 删除评论: id={comment_id}")

    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(404, detail="评论不存在")

    comment.is_visible = False
    db.add(comment)
    db.commit()

    logger.info(f"评论已软删除: id={comment_id}")
