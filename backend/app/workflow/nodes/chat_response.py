"""流式聊天响应节点工厂。"""

import logging
from pathlib import Path
from typing import Any

from app.harness.model_factory import get_chat_model
from app.workflow.state import BlogState

logger = logging.getLogger(__name__)
_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "nodes"


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def make_chat_node(prompt_name: str):
    """返回一个流式聊天节点函数。"""
    system_prompt = _load_prompt(prompt_name)
    model = get_chat_model(temperature=0.7, streaming=True)

    async def _node(state: BlogState) -> dict[str, Any]:
        logger.info("%s: replying to user", prompt_name)
        messages = list(state.get("messages", []))
        response = await model.ainvoke(
            [("system", system_prompt)] + [(m.type, m.content) for m in messages]
        )
        logger.info("%s: done, chars=%s", prompt_name, len(response.content or ""))
        return {"messages": [response]}

    return _node


fallback_response = make_chat_node("fallback")
clarify_intent = make_chat_node("clarify")


# ===== discuss_topic：单独实现，需要检测 [GENERATE] 标记 =====
_DISCUSS_PROMPT = _load_prompt("discuss")
_DISCUSS_MODEL = get_chat_model(temperature=0.7, streaming=True)


async def discuss_topic(state: BlogState) -> dict[str, Any]:
    """讨论话题 —— 检测到 [GENERATE] 时标记进入需求分析。"""
    messages = list(state.get("messages", []))
    msg_count = len(messages)
    logger.info("discuss_topic: messages=%s", msg_count)
    response = await _DISCUSS_MODEL.ainvoke(
        [("system", _DISCUSS_PROMPT)] + [(m.type, m.content) for m in messages]
    )

    response_text = response.content or ""
    trigger = "[GENERATE]" in response_text
    logger.info("discuss_topic: trigger=%s chars=%s", trigger, len(response_text))

    result: dict[str, Any] = {"messages": [response]}
    if trigger:
        result["current_stage"] = "REQUIREMENT_ANALYSIS"

    # 从最近对话中提取话题上下文，供 requirement_analyzer 使用
    user_msgs = [m.content for m in messages if getattr(m, "type", "") == "human"]
    recent_topic = "；".join(m[:120] for m in user_msgs[-3:]) if user_msgs else "未指定"
    result["topic_brief"] = {"topic": recent_topic, "direction": "", "confirmed": False}

    return result

