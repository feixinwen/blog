"""需求分析节点 —— 结构化 LLM Node，不聊天，只输出 BlogRequirement。"""

import json
import logging
from pathlib import Path
from typing import Any

from app.harness.model_factory import get_requirement_model
from app.workflow.schemas import BlogRequirement, WritingDefaults
from app.workflow.state import BlogState

logger = logging.getLogger(__name__)

_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "nodes" / "requirement_analyzer.md").read_text(encoding="utf-8")
_MODEL = get_requirement_model()


def _to_json(obj) -> str:
    """安全序列化 Pydantic 模型或 dict。"""
    if obj is None:
        return "无"
    if hasattr(obj, "model_dump_json"):
        return obj.model_dump_json(indent=2)
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


def _build_context(state: BlogState) -> str:
    topic_brief = state.get("topic_brief")
    existing = state.get("requirement")
    defaults = state.get("writing_defaults") or WritingDefaults()
    user_input = state["user_input"]

    # 最近几轮相关消息
    recent: list[str] = []
    for m in state.get("messages", [])[-6:]:
        recent.append(m.content if hasattr(m, "content") else str(m))

    parts = [
        "## 当前用户输入",
        user_input,
        "",
        "## 已确认的主题摘要",
        _to_json(topic_brief),
        "",
        "## 已有需求",
        _to_json(existing),
        "",
        "## 默认写作配置",
        _to_json(defaults),
        "",
        "## 最近对话",
        json.dumps(recent, ensure_ascii=False, indent=2),
    ]
    return "\n".join(parts)


async def analyze_requirement(state: BlogState) -> dict[str, Any]:
    """分析需求 → 输出 BlogRequirement。只分析，不聊天。"""
    logger.info("analyze_requirement: %s", state["user_input"][:60])

    context = _build_context(state)
    model = _MODEL.with_structured_output(BlogRequirement)
    requirement: BlogRequirement = await model.ainvoke(
        [("system", _PROMPT), ("user", context)]
    )

    logger.info(
        "analyze_requirement → %s missing=%s",
        requirement.status, requirement.missing_fields,
    )
    return {
        "requirement": requirement,
        "requirement_status": requirement.status,
        "current_stage": "REQUIREMENT_ANALYSIS",
    }
