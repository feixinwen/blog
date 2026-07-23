"""澄清需求节点 —— 不调 LLM，直接读取 next_question 展示给用户。"""

import logging
from typing import Any

from langchain_core.messages import AIMessage

from app.workflow.state import BlogState

logger = logging.getLogger(__name__)


async def clarify_requirement(state: BlogState) -> dict[str, Any]:
    """把 requirement_analyzer 的 next_question 包装成回复。不调 LLM。"""
    req = state.get("requirement")
    question = req.next_question if req else None
    text = question or "为了更好规划文章，请再补充一些细节。"
    logger.info("clarify_requirement: %s", text[:80])
    return {
        "messages": [AIMessage(content=text)],
        "current_stage": "WAITING_INPUT",
    }
