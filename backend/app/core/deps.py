from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, create_engine

from app.core.config import settings
from app.core.security import decode_access_token

engine = create_engine(settings.database_url)


def get_db():
    """
    每个请求进来时，创建一个新的数据库会话，
    请求结束后自动关闭，防止连接泄漏。
    """
    with Session(engine) as session:
        yield session


# HTTPBearer: 从请求头 Authorization 里提取 Bearer token
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    """
    从请求的 JWT token 里解析出当前登录用户的 ID，
    然后从数据库查出用户对象。token 无效或用户不存在就返回 401。
    """
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
        )
    from app.models.user import User

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )
    return user
