import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.deps import get_db
from app.core.security import create_access_token, verify_password
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["后台-认证"])
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """管理员登录，成功返回 JWT token"""
    logger.info(f"管理员登录尝试: username={body.username}")

    # 1. 查用户是否存在
    user = db.exec(
        select(User).where(User.username == body.username)
    ).first()

    if user is None:
        logger.warning(f"登录失败: 用户名不存在 {body.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 2. 验证密码
    if not verify_password(body.password, user.password_hash):
        logger.warning(f"登录失败: 密码错误 {body.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 3. 生成 token
    token = create_access_token(user.id)
    logger.info(f"管理员登录成功: username={body.username}, user_id={user.id}")

    return LoginResponse(access_token=token)
