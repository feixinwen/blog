"""Assembler 节点 — 纯代码节点（0 次 LLM 调用），格式化 + 拼装最终 Markdown。"""

import logging
import re
from typing import Any

from app.workflow.state import BlogState

logger = logging.getLogger(__name__)

# 模型常见的前言模式（每行一个前缀）
_MODEL_PREFACE_PATTERNS = [
    "以下是",
    "下面是",
    "这是修订后的",
    "这是根据评审意见",
    "好的，",
    "这是最终",
    "这是生成",
]


async def assembler(state: BlogState) -> dict[str, Any]:
    """拼装最终 Markdown，添加头部和参考文献。"""
    draft = state.get("draft")
    report = state.get("research_report")

    if not draft or not draft.markdown:
        logger.warning("assembler: no draft, skipping")
        return {"current_stage": "ASSEMBLING"}

    logger.info("assembler start: title=%s chars=%s", draft.title, len(draft.markdown))

    original = draft.markdown
    cleaned = _cleanup_markdown(original, draft.title)

    # 拼装最终文档
    parts = [_build_header(draft.title)]

    if cleaned:
        parts.append(cleaned)

    if report and report.sources:
        refs = _build_references(report.sources)
        if refs:
            parts.append(refs)

    assembled = "\n\n".join(parts) + "\n"

    # 更新 draft
    draft.markdown = assembled
    draft.metadata["assembled"] = True
    draft.metadata["original_chars"] = len(original)
    draft.metadata["assembled_chars"] = len(assembled)

    logger.info("assembler done: %s → %s chars", len(original), len(assembled))
    return {"draft": draft, "current_stage": "ASSEMBLING"}


def _build_header(title: str) -> str:
    return f"# {title.strip()}\n"


def _cleanup_markdown(markdown: str, title: str) -> str:
    text = markdown.strip()
    # 去掉模型常见前言
    text = _strip_model_preface(text)
    # 去掉与标题重复的一级标题
    text = _strip_duplicate_title(text, title)
    # 统一换行
    text = re.sub(r"\r\n?", "\n", text)
    # 压缩多余空行
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_model_preface(markdown: str) -> str:
    """去掉 LLM 常见的开头废话（"以下是修订后的文章..."）。"""
    lines = markdown.splitlines()
    while lines and _is_preface_line(lines[0].strip()):
        lines.pop(0)
    return "\n".join(lines)


def _is_preface_line(line: str) -> bool:
    if not line:
        return False
    return any(line.startswith(p) for p in _MODEL_PREFACE_PATTERNS)


def _strip_duplicate_title(markdown: str, title: str) -> str:
    """如果正文第一行是 `# 标题`（与 title 重复），移除。"""
    escaped = re.escape(title.strip())
    pattern = rf"^#\s+{escaped}\s*\n+"
    return re.sub(pattern, "", markdown, count=1)


def _build_references(sources) -> str:
    """从 ResearchReport.sources 构建参考文献 section。"""
    if not sources:
        return ""

    # 去重
    seen: set[str] = set()
    unique: list = []
    for s in sources:
        key = s.url or s.title
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(s)

    if not unique:
        return ""

    lines = ["## 参考资料", ""]
    for i, s in enumerate(unique, 1):
        title = s.title.strip() or f"参考资料 {i}"
        if s.url:
            lines.append(f"{i}. [{title}]({s.url})")
        else:
            lines.append(f"{i}. {title}")
    return "\n".join(lines)
