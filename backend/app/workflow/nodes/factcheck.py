"""FactCheck 节点 — 对照研究来源验证文章中的事实声明，1 次 LLM 调用。"""

import logging
from pathlib import Path
from typing import Any

from app.harness.model_factory import get_classifier_model
from app.workflow.schemas import FactCheckReport
from app.workflow.state import BlogState

logger = logging.getLogger(__name__)

_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "nodes" / "factcheck.md").read_text(encoding="utf-8")
_MODEL = get_classifier_model().with_structured_output(FactCheckReport)


async def factcheck(state: BlogState) -> dict[str, Any]:
    """对照研究来源验证草稿中的事实声明。"""
    draft = state.get("draft")
    report = state.get("research_report")

    if not draft or not draft.markdown:
        logger.warning("factcheck: no draft, skipping")
        return {"fact_check": None, "current_stage": "FACT_CHECK"}

    logger.info("factcheck start: title=%s chars=%s", draft.title, len(draft.markdown))

    user_msg = _build_factcheck_prompt(draft=draft, research_report=report)

    try:
        result: FactCheckReport = await _MODEL.ainvoke([
            ("system", _PROMPT),
            ("user", user_msg),
        ])
    except Exception as e:
        logger.error("factcheck failed: %s", e)
        return {"fact_check": None, "current_stage": "FACT_CHECK"}

    logger.info(
        "factcheck done: score=%s supported=%s contradicted=%s unverified=%s",
        result.overall_score,
        result.supported,
        result.contradicted,
        result.unverified,
    )
    return {"fact_check": result, "current_stage": "FACT_CHECK"}


def _build_factcheck_prompt(*, draft, research_report) -> str:
    parts = [f"文章标题：{draft.title}"]

    # 研究来源
    if research_report and research_report.sources:
        sources_text = "\n".join(
            f"- [{s.title}]({s.url}) — {s.summary}" for s in research_report.sources[:10]
        )
        parts.append(f"\n## 参考来源\n{sources_text}")

    if research_report and research_report.findings:
        findings_text = "\n".join(
            f"- {f.topic}：{f.conclusion}" for f in research_report.findings[:10]
        )
        parts.append(f"\n## 研究发现\n{findings_text}")

    # 正文（截断）
    parts.append(f"\n## 文章正文\n{draft.markdown[:12000]}")

    return "\n".join(parts)
