"""研究节点 —— ReAct Agent + Context + 去重 + 结构化输出。"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from langgraph.prebuilt import create_react_agent

from app.harness.model_factory import get_chat_model, get_classifier_model
from app.tools import RESEARCH_TOOLS
from app.workflow.schemas import ResearchContext, ResearchReport
from app.workflow.state import BlogState

logger = logging.getLogger(__name__)

# ===== 约束 =====
MAX_ITERATIONS = 10
TIMEOUT_SECONDS = 120

# ===== Prompt =====
_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "nodes" / "research.md").read_text(encoding="utf-8")

# ===== 模型 =====
_EXPLORE_MODEL = get_chat_model(temperature=0.5, streaming=True)
_FORMAT_MODEL = get_classifier_model()  # 温度 0，格式化输出

_AGENT = create_react_agent(_EXPLORE_MODEL, RESEARCH_TOOLS, prompt=_PROMPT)


# ===== Context 构造 =====
def _build_context(state: BlogState) -> ResearchContext:
    req = state.get("requirement")
    if not req:
        return ResearchContext(topic="未指定主题", direction="")

    return ResearchContext(
        topic=req.topic,
        direction=req.direction,
        audience=req.target_audience or "",
        blog_type=req.blog_type or "",
        technical_depth=req.technical_depth or "intermediate",
        need_code=req.need_code_examples,
        user_materials=[m.content for m in req.personal_materials],
    )


# ===== 搜索去重 =====
_searched_queries: set[str] = set()


def _seen_query(q: str) -> bool:
    """检查 query 是否已搜过（模糊去重）。"""
    q_lower = q.strip().lower()
    for prev in _searched_queries:
        if q_lower == prev or q_lower in prev or prev in q_lower:
            return True
    _searched_queries.add(q_lower)
    return False


# ===== 研究节点 =====
async def research(state: BlogState) -> dict[str, Any]:
    """ReAct Agent 探索 → 结构化 ResearchReport。"""
    req = state.get("requirement")
    if not req:
        return {"research_notes": "", "research_report": None, "current_stage": "RESEARCH"}

    context = _build_context(state)
    _searched_queries.clear()

    user_msg = f"""## 博客需求
{context.model_dump_json(indent=2)}

请根据以上需求收集研究资料。
搜索前先规划要搞清楚哪些问题，然后逐一研究。"""

    logger.info("research agent start: topic=%s", req.topic[:60])

    # ---- 第 1 步：Agent 自由探索 ----
    try:
        result = await asyncio.wait_for(
            _AGENT.ainvoke(
                {"messages": [("user", user_msg)]},
                config={"recursion_limit": MAX_ITERATIONS},
            ),
            timeout=TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.warning("research agent timeout")
        return _fallback()
    except Exception as e:
        logger.error("research agent failed: %s", e)
        return _fallback(str(e))

    msgs = result.get("messages", [])
    notes = msgs[-1].content if msgs else ""
    logger.info("research agent done: %s chars, %s steps", len(notes), len(msgs))

    # ---- 第 2 步：格式化输出 ----
    report = await _format_report(context, notes)

    return {
        "research_notes": notes,
        "research_report": report,
        "current_stage": "RESEARCH",
        "messages": [msgs[-1]] if msgs else [],
    }


# ===== 结构化格式化节点 =====
_FORMAT_PROMPT = """你负责将研究笔记转换为结构化的 ResearchReport JSON。

规则：
- 每条 finding 必须关联 source_indices（引用 sources 数组下标）
- 不确定的信息在 conclusion 中标注"不确定"
- missing_information 列出尚未搞清楚的问题
- confidence 评估整体可靠性：high（有官方文档/源码支撑）、medium（有高质量博客）、low（大部分信息未验证）
- sources 中 quality 按：官方文档/源码=high、优质博客=medium、社区/论坛=low"""


async def _format_report(context: ResearchContext, notes: str) -> ResearchReport:
    try:
        model = _FORMAT_MODEL.with_structured_output(ResearchReport)
        report = await model.ainvoke([
            ("system", _FORMAT_PROMPT),
            ("user", f"## 博客需求\n{context.model_dump_json(indent=2)}\n\n## 研究笔记\n{notes}"),
        ])
        return report
    except Exception as e:
        logger.warning("format report failed: %s", e)
        # 降级：生成最小报告
        return ResearchReport(
            research_questions=[],
            findings=[],
            sources=[],
            writing_suggestions=notes[:500],
            confidence="low",
        )


def _fallback(error: str = "") -> dict[str, Any]:
    return {
        "research_notes": f"研究过程出错: {error}",
        "research_report": ResearchReport(
            research_questions=[],
            findings=[],
            sources=[],
            writing_suggestions="研究未能完成，请基于已有知识继续。",
            confidence="low",
        ),
        "current_stage": "RESEARCH",
    }


