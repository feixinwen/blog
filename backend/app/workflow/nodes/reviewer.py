"""Reviewer 节点 — 合并 ThreadChecker + Reviewer，1 次 LLM 调用，结构化输出。"""

import logging
from pathlib import Path
from typing import Any

from app.harness.model_factory import get_classifier_model
from app.workflow.schemas import ReviewReport
from app.workflow.state import BlogState

logger = logging.getLogger(__name__)

_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "nodes" / "reviewer.md").read_text(encoding="utf-8")
_MODEL = get_classifier_model().with_structured_output(ReviewReport)


async def reviewer(state: BlogState) -> dict[str, Any]:
    """审读草稿，合并连贯性检查 + 综合质量审核。"""
    draft = state.get("draft")
    outline = state.get("outline")
    report = state.get("research_report")

    if not draft or not draft.markdown:
        logger.warning("reviewer: no draft to review, skipping")
        return {"review": None, "current_stage": "REVIEWING"}

    logger.info("reviewer start: title=%s chars=%s", draft.title, len(draft.markdown))

    user_msg = _build_review_prompt(
        draft=draft,
        outline=outline,
        research_report=report,
    )

    try:
        review: ReviewReport = await _MODEL.ainvoke([
            ("system", _PROMPT),
            ("user", user_msg),
        ])
    except Exception as e:
        logger.error("reviewer failed: %s", e)
        return {"review": None, "current_stage": "REVIEWING"}

    logger.info(
        "reviewer done: score=%s approved=%s coherence=%s issues=%s",
        review.score,
        review.approved,
        review.coherence_score,
        len(review.issues),
    )
    return {"review": review, "current_stage": "REVIEWING"}


def _build_review_prompt(*, draft, outline, research_report) -> str:
    parts = []

    parts.append(f"文章标题：{draft.title}")
    if outline:
        parts.append(f"文章副标题：{outline.subtitle or '无'}")
        parts.append(f"开头目标：{outline.introduction_goal or '无'}")
        parts.append(f"结尾目标：{outline.conclusion_goal or '无'}")
        sections_index = "\n".join(
            f"{s.order}. {s.title}（{s.estimated_words}字）— {s.purpose}"
            for s in outline.sections
        )
        parts.append(f"\n原始大纲：\n{sections_index}")

    # 研究资料要点（供事实核查）
    if research_report and research_report.findings:
        findings_text = "\n".join(
            f"- {f.topic}：{f.conclusion[:120]}" for f in research_report.findings[:10]
        )
        parts.append(f"\n研究资料（供事实核查参考）：\n{findings_text}")

    # 截断长文，reviewer 不需要全文
    markdown_snippet = draft.markdown[:12000]
    parts.append(f"\n文章正文（前 12000 字）：\n{markdown_snippet}")

    return "\n".join(parts)
