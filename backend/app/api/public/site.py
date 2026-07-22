import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.deps import get_db
from app.models.user import User

router = APIRouter(prefix="/api", tags=["公开-站点"])
logger = logging.getLogger(__name__)


@router.get("/site-info")
def get_site_info(db: Session = Depends(get_db)):
    """返回博客站点基本信息"""
    user = db.exec(select(User).order_by(User.id).limit(1)).first()
    return {
        "author": user.username if user else "博客作者",
    }
