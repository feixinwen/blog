"""Writer 节点 —— 逐章节写作，含叙事上下文摘要以保持章节连贯。"""

import logging
import re
from pathlib import Path
from typing import Any

from app.harness.model_factory import get_chat_model
from app.workflow.schemas import ArticleDraft, ArticleSection, BlogOutline, OutlineSection, ResearchReport
from app.workflow.state import BlogState

logger = logging.getLogger(__name__)

_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "nodes" / "writer.md").read_text(encoding="utf-8")
_MODEL = get_chat_model(temperature=0.7, streaming=True)

_SUMMARY_RE = re.compile(r"<!--\s*section_summary:\s*(.*?)\s*-->")


async def writer(state: BlogState) -> dict[str, Any]:
    """逐章节写作，生成 ArticleDraft。"""
    outline = state.get("outline")
    report = state.get("research_report")

    if not outline or not outline.sections:
        logger.warning("writer: no outline or empty sections, skipping")
        return {
            "draft": None,
            "current_stage": "WRITING",
        }

    logger.info("writer start: title=%s sections=%s", outline.title, len(outline.sections))

    research_text = _format_research(report) if report else ""
    full_context = _build_article_context(outline)

    sections: list[ArticleSection] = []
    previous_summaries: list[str] = []

    for planned in outline.sections:
        logger.info("writer: section %s/%s: %s", planned.order, len(outline.sections), planned.title)

        prev_text = _format_previous_summaries(previous_summaries) if previous_summaries else ""
        user_msg = _build_section_prompt(
            context=full_context,
            section=planned,
            research=research_text,
            previous_summary=prev_text,
        )

        markdown = await _MODEL.ainvoke([
            ("system", _PROMPT),
            ("user", user_msg),
        ])

        content = markdown.content.strip() if hasattr(markdown, "content") else str(markdown).strip()

        summary, clean_content = _extract_summary(content)
        previous_summaries.append(f"第{planned.order}节「{planned.title}」：{summary}")

        sections.append(ArticleSection(
            title=planned.title,
            markdown=clean_content,
            summary=summary,
            order=planned.order,
        ))
        logger.info("writer: section done: title=%s chars=%s", planned.title, len(clean_content))

    full_markdown = "\n\n".join(s.markdown for s in sections)
    draft = ArticleDraft(
        title=outline.title,
        markdown=full_markdown,
        sections=sections,
        metadata={"writer": "writer"},
    )

    logger.info("writer done: title=%s sections=%s chars=%s", draft.title, len(sections), len(full_markdown))
    return {
        "draft": draft,
        "current_stage": "WRITING",
    }


def _build_article_context(outline: BlogOutline) -> str:
    """构建文章整体上下文——告诉 Writer 这篇文章的整体目标和风格。"""
    parts = [
        f"文章标题：{outline.title}",
    ]
    if outline.subtitle:
        parts.append(f"副标题：{outline.subtitle}")
    if outline.article_style:
        parts.append(f"风格定位：{outline.article_style}")
    if outline.introduction_goal:
        parts.append(f"开头目标：{outline.introduction_goal}")
    if outline.conclusion_goal:
        parts.append(f"结尾目标：{outline.conclusion_goal}")

    section_index = "\n".join(
        f"{s.order}. {s.title}（{s.estimated_words}字）— {s.purpose}" for s in outline.sections
    )
    parts.append(f"\n完整章节结构：\n{section_index}")
    return "\n".join(parts)


def _format_research(report: ResearchReport) -> str:
    """将 ResearchReport 格式化为 Writer 可用的参考文本。"""
    lines = []

    if report.findings:
        lines.append("## 研究资料\n")
        for i, f in enumerate(report.findings, 1):
            lines.append(f"{i}. **{f.topic}**：{f.conclusion}")

    if report.sources:
        lines.append("\n## 参考来源\n")
        for s in report.sources:
            line = f"- [{s.title}]({s.url})"
            if s.summary:
                line += f" — {s.summary}"
            lines.append(line)

    if report.writing_suggestions:
        lines.append(f"\n## 写作建议\n{report.writing_suggestions}")

    return "\n".join(lines)


def _format_previous_summaries(summaries: list[str]) -> str:
    """格式化叙事上下文摘要列表。"""
    return "前面章节已覆盖的内容，请勿重复：\n" + "\n".join(f"- {s}" for s in summaries)


def _build_section_prompt(
    *,
    context: str,
    section: OutlineSection,
    research: str,
    previous_summary: str,
) -> str:
    """构建单章节写作的 user prompt。"""
    parts = [
        context,
        f"\n## 当前任务：撰写第 {section.order} 章\n",
        f"**章节标题**：{section.title}",
        f"**写作目的**：{section.purpose or '围绕核心要点展开'}",
        f"**目标字数**：约 {section.estimated_words} 字",
    ]

    if section.key_points:
        parts.append(f"\n**必须覆盖的要点**：\n" + "\n".join(f"- {p}" for p in section.key_points))

    if research:
        parts.append(f"\n{research}")

    if previous_summary:
        parts.append(f"\n{previous_summary}")

    return "\n".join(parts)


def _extract_summary(markdown: str) -> tuple[str, str]:
    """从 Markdown 末尾提取叙事摘要，返回 (summary, cleaned_markdown)。"""
    m = _SUMMARY_RE.search(markdown)
    if m:
        summary = m.group(1).strip()
        clean = _SUMMARY_RE.sub("", markdown).strip()
        return summary, clean
    # 降级：用第一句作为摘要
    first_line = markdown.strip().split("\n")[0]
    return first_line[:80], markdown
