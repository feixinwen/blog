"""Revision 节点 — 根据 ReviewReport 逐条修改草稿，结构化 JSON 输出。"""

import json
import logging
import re
from pathlib import Path
from typing import Any

from app.harness.model_factory import get_chat_model
from app.workflow.schemas import ArticleDraft, ArticleSection, RevisedDraft
from app.workflow.state import BlogState

logger = logging.getLogger(__name__)

_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "nodes" / "revision.md").read_text(encoding="utf-8")
_MODEL = get_chat_model(temperature=0.5)  # 中等温度，修订需要一定创造性但不宜过高


async def revision(state: BlogState) -> dict[str, Any]:
    """根据 review 修改草稿，输出修订后的 ArticleDraft。"""
    draft = state.get("draft")
    review = state.get("review")
    outline = state.get("outline")

    if not draft or not review:
        logger.warning("revision: no draft or review, skipping")
        return {"current_stage": "REVISING"}

    revision_count = state.get("revision_count", 0) + 1
    logger.info("revision start: title=%s round=%s", draft.title, revision_count)

    user_msg = _build_revision_prompt(draft=draft, review=review, outline=outline)
    raw = await _MODEL.ainvoke([
        ("system", _PROMPT),
        ("user", user_msg),
    ])
    content = raw.content.strip() if hasattr(raw, "content") else str(raw).strip()

    try:
        revised = _parse_revised_draft(content)
    except Exception as e:
        logger.error("revision parse failed: %s", e)
        # 降级：保留原稿
        return {
            "draft": draft,
            "revision_count": revision_count,
            "current_stage": "REVISING",
        }

    # 更新 draft
    updated = ArticleDraft(
        title=revised.title or draft.title,
        markdown=revised.markdown,
        sections=[ArticleSection(title="修订稿", markdown=revised.markdown, summary="", order=0)],
        tags=revised.tags or draft.tags,
        metadata={**draft.metadata, "revision_count": revision_count},
    )

    logger.info("revision done: title=%s round=%s chars=%s", updated.title, revision_count, len(updated.markdown))
    return {
        "draft": updated,
        "revision_count": revision_count,
        "current_stage": "REVISING",
    }


def _build_revision_prompt(*, draft, review, outline) -> str:
    parts = []

    parts.append(f"文章标题：{draft.title}")

    # 审核结果
    parts.append(f"\n## 审核结果\n- 综合评分：{review.score}")
    parts.append(f"- 是否通过：{review.approved}")
    parts.append(f"- 连贯性评分：{review.coherence_score}")
    parts.append(f"- 总结：{review.summary}")

    if review.issues:
        parts.append("\n## 待修复问题")
        for item in review.issues:
            parts.append(
                f"- [{item.severity}] {item.location}（{item.issue_type}）\n"
                f"  问题：{item.description}\n"
                f"  建议：{item.suggestion or '无'}"
            )

    # 大纲（供参考）
    if outline:
        sections_index = "\n".join(
            f"{s.order}. {s.title} — {s.purpose}" for s in outline.sections
        )
        parts.append(f"\n## 原始大纲\n{sections_index}")

    # 原始正文
    parts.append(f"\n## 原始正文\n{draft.markdown}")

    return "\n".join(parts)


def _parse_revised_draft(raw: str) -> RevisedDraft:
    text = _extract_json_text(raw)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error("revision returned invalid JSON: %s", raw[:500])
        raise ValueError("RevisionAgent failed to parse revised draft JSON") from exc

    if "markdown" not in data and "content" in data:
        data["markdown"] = data["content"]
    return RevisedDraft.model_validate(data)


def _extract_json_text(raw: str) -> str:
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
    return text
