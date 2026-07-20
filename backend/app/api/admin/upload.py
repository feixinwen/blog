import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["后台-上传"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload")
async def upload_image(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    """上传图片 —— 返回可访问的 URL"""
    # 校验文件类型
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {ext}，仅支持 {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 校验文件大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, detail="文件不能超过 5MB")

    # 用随机文件名避免冲突和覆盖
    filename = f"{uuid.uuid4().hex}{ext}"
    save_dir = Path(settings.upload_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    filepath = save_dir / filename
    with open(filepath, "wb") as f:
        f.write(content)

    url = f"{settings.backend_base_url}{settings.upload_url_prefix}/{filename}"
    logger.info(f"管理员 {current_user.username} 上传图片: {filename}")

    return {"url": url}
