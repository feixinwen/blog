import logging
from contextlib import asynccontextmanager

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.deps import engine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 应用的生命周期管理。
    启动时：打印日志、自动创建数据库表。
    关闭时：释放引擎连接池。
    """
    logger.info("=" * 50)
    logger.info("博客系统启动中...")
    logger.info(f"数据库地址: {settings.database_url}")
    logger.info("=" * 50)

    SQLModel.metadata.create_all(engine)

    yield  # ← 应用运行期间停在这里

    logger.info("博客系统已关闭")


app = FastAPI(
    title="个人博客系统",
    description="FastAPI + Vue 3 个人博客",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS：允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vue 开发服务器
        "http://localhost",        # 生产环境 Nginx
    ],
    allow_credentials=True,
    allow_methods=["*"],          # 允许所有 HTTP 方法
    allow_headers=["*"],          # 允许所有请求头
)


# 挂载上传目录（作为静态文件服务）
upload_path = Path(settings.upload_dir)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount(settings.upload_url_prefix, StaticFiles(directory=str(upload_path)), name="uploads")


@app.get("/")
def root():
    return {"message": "博客 API 运行中"}


# ==================== 注册路由 ====================
from app.api.public.articles import router as public_articles_router
from app.api.public.categories import router as public_categories_router
from app.api.public.comments import router as public_comments_router
from app.api.public.site import router as public_site_router
from app.api.public.tags import router as public_tags_router

app.include_router(public_articles_router)
app.include_router(public_categories_router)
app.include_router(public_comments_router)
app.include_router(public_site_router)
app.include_router(public_tags_router)

# 后台路由
from app.api.admin.articles import router as admin_articles_router
from app.api.admin.auth import router as admin_auth_router
from app.api.admin.categories import router as admin_categories_router
from app.api.admin.comments import router as admin_comments_router
from app.api.admin.tags import router as admin_tags_router
from app.api.admin.upload import router as admin_upload_router

app.include_router(admin_auth_router)
app.include_router(admin_articles_router)
app.include_router(admin_categories_router)
app.include_router(admin_comments_router)
app.include_router(admin_tags_router)
app.include_router(admin_upload_router)
