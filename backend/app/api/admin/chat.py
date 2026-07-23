"""聊天创作助手 API —— SSE 流式输出。"""

import json
import logging
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.deps import get_current_user, get_db
from app.models.article import Article, ArticleTagLink
from app.models.tag import Tag
from app.models.user import User
from app.workflow.graph import get_blog_graph

router = APIRouter(prefix="/api/admin", tags=["后台-创作助手"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"


@router.post("/chat")
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    stream: bool = Query(False),
    db: Session = Depends(get_db),
):
    """发送消息给创作助手。stream=true 使用 SSE 流式输出。"""
    logger.info("创作助手: user=%s stream=%s", current_user.username, stream)

    thread_id = f"user_{current_user.id}_{body.thread_id}"
    graph = get_blog_graph()

    if not stream:
        from langchain_core.messages import HumanMessage

        config = {"configurable": {"thread_id": thread_id}}
        result = await graph._graph.ainvoke(
            {"messages": [HumanMessage(content=body.message)], "user_input": body.message, "intent": ""},
            config,
        )
        last = result["messages"][-1] if result.get("messages") else None
        text = last.content if last else ""
        return {
            "response": text,
            "thread_id": body.thread_id,
            "ready_to_generate": "[GENERATE]" in text,
        }

    return StreamingResponse(
        _save_and_stream(graph, body.message, thread_id, db),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


async def _save_and_stream(graph, message: str, thread_id: str, db: Session):
    """包装 stream：转发事件给前端 + 拦截 article 事件存数据库。"""
    article_data: dict | None = None

    async for line in graph.stream(message, thread_id=thread_id):
        yield line
        if article_data is None and line.startswith("data: "):
            try:
                payload = json.loads(line[6:])
                if payload.get("article"):
                    article_data = payload["article"]
            except (json.JSONDecodeError, KeyError):
                pass

    if article_data and article_data.get("content"):
        try:
            article_id = _save_draft(article_data, db)
            logger.info("文章已自动保存为草稿: id=%s title=%s", article_id, article_data.get("title"))
        except Exception:
            logger.exception("自动保存草稿失败")


def _save_draft(data: dict, db: Session) -> int:
    title = data.get("title", "未命名文章").strip()
    content = data.get("content", "").strip()
    summary = data.get("summary", "").strip() or None
    tags: list[str] = data.get("tags", [])

    slug = _generate_slug(title, db)

    article = Article(
        title=title,
        slug=slug,
        content=content,
        summary=summary,
        is_published=False,
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    # 关联标签（按名称查找已有标签，不存在则跳过——MVP 阶段不自动创建标签）
    if tags:
        for tag_name in tags:
            name = tag_name.strip()
            if not name:
                continue
            existing_tag = db.exec(select(Tag).where(Tag.name == name)).first()
            if existing_tag:
                db.add(ArticleTagLink(article_id=article.id, tag_id=existing_tag.id))
        db.commit()

    return article.id


def _generate_slug(title: str, db: Session) -> str:
    base = title.strip().lower()
    base = re.sub(r"[^\w\s-]", "", base)
    base = re.sub(r"[-\s]+", "-", base)
    base = base.strip("-") or "article"

    # 截断
    if len(base) > 80:
        base = base[:80].rstrip("-")

    # 唯一性检查
    slug = base
    existing = db.exec(select(Article).where(Article.slug == slug)).first()
    if not existing:
        return slug

    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    return f"{base}-{ts}"
