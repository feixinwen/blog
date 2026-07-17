from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 密码哈希上下文 —— bcrypt 算法
# schemes=["bcrypt"]  表示用 bcrypt 加密
# deprecated="auto"   意思是如果 bcrypt 版本过时了，自动升级
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """把明文密码变成加密字符串，存数据库用"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码：用户输入的明文 和 数据库存的密文 是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """登录成功后，生成一个 JWT token 返回给前端"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(user_id),   # subject: 存用户 ID，表示"这个 token 属于谁"
        "exp": expire,          # expires: 过期时间
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int | None:
    """解析 token，如果有效返回 user_id，无效返回 None"""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return int(payload.get("sub"))
    except JWTError:
        return None
