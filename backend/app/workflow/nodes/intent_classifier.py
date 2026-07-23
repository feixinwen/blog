"""意图分类节点 —— 一次轻量 LLM 结构化输出。"""

import json
import logging
from pathlib import Path
from typing import Any

from app.harness.model_factory import get_classifier_model
from app.workflow.schemas import INTENT_SCHEMA
from app.workflow.state import BlogState

logger = logging.getLogger(__name__)

_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "nodes" / "intent_classifier.md").read_text(encoding="utf-8")


async def classify_intent(state: BlogState) -> dict[str, Any]:
    """分类用户意图 → BLOG_CREATION / NON_BLOG / UNCLEAR。"""
    msg = state["user_input"]
    logger.info("classify_intent: %s", msg[:60])

    # 附带最近对话历史，帮助短指令（如"开始写吧"）获取上下文
    recent = _recent_history(state)
    user_content = f"【最近对话上下文】\n{recent}\n\n【当前用户输入】\n{msg}" if recent else msg

    model = get_classifier_model().bind(response_format=INTENT_SCHEMA)
    resp = await model.ainvoke([("system", _PROMPT), ("user", user_content)])
    parsed = json.loads(resp.content)

    logger.info("classify_intent → %s (%s)", parsed["intent"], parsed.get("reason", ""))
    return {"intent": parsed["intent"]}


def _recent_history(state: BlogState) -> str:
    """提取最近 3 轮对话摘要，帮助意图分类理解上下文。"""
    msgs = state.get("messages", [])
    pairs: list[str] = []
    for m in msgs[-6:]:  # 最近 6 条消息≈3 轮对话
        content = m.content if hasattr(m, "content") else str(m)
        role = "用户" if getattr(m, "type", "") == "human" else "助手"
        pairs.append(f"[{role}] {content[:120]}")
    return "\n".join(pairs) if pairs else ""
