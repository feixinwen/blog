"""Planner 节点 —— LLM Node，不调工具，结构化输出大纲。"""

import logging
from pathlib import Path
from typing import Any

from app.harness.model_factory import get_classifier_model
from app.workflow.schemas import BlogOutline
from app.workflow.state import BlogState

logger = logging.getLogger(__name__)

_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "nodes" / "planner.md").read_text(encoding="utf-8")
_MODEL = get_classifier_model().with_structured_output(BlogOutline)


async def planner(state: BlogState) -> dict[str, Any]:
    """根据需求 + 研究报告 → 结构化文章大纲。"""
    req = state.get("requirement")
    report = state.get("research_report")
    notes = state.get("research_notes", "")

    if not req:
        return {"outline": None, "current_stage": "PLANNING"}

    # 构建上下文
    context_parts = [
        f"## 用户需求\n- 主题：{req.topic}\n- 方向：{req.direction}\n"
        f"- 目标读者：{req.target_audience or '未指定'}\n- 文章类型：{req.blog_type}\n"
        f"- 技术深度：{req.technical_depth}\n- 字数目标：{req.target_length}",
    ]

    if report:
        findings = "\n".join(
            f"- {f.topic}: {f.conclusion[:200]}" for f in report.findings[:8]
        )
        context_parts.append(f"## 研究资料\n{findings}\n\n来源数量: {len(report.sources)}")

    if notes and not report:
        context_parts.append(f"## 研究笔记\n{notes[:2000]}")

    user_msg = "\n\n".join(context_parts)

    logger.info("planner: topic=%s", req.topic[:60])

    try:
        outline: BlogOutline = await _MODEL.ainvoke(
            [("system", _PROMPT), ("user", user_msg)]
        )
    except Exception as e:
        logger.error("planner failed: %s", e)
        return {"outline": None, "current_stage": "PLANNING"}

    logger.info("planner done: title=%s sections=%s", outline.title, len(outline.sections))
    return {"outline": outline, "current_stage": "PLANNING"}
