"""fetch_page 工具 —— 读取网页内容（Jina → HTTP 回退）。"""

from __future__ import annotations

import logging
import os
import re

import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

JINA_API_KEY = os.getenv("JINA_API_KEY", "")
JINA_BASE_URL = os.getenv("JINA_READER_BASE_URL", "https://r.jina.ai/")
TIMEOUT = 20
MAX_CHARS = 6000
MAX_RETRIES = 1


# ===== Service =====
async def _read_via_jina(url: str) -> str | None:
    if not JINA_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(
                f"{JINA_BASE_URL}{url}",
                headers={"Authorization": f"Bearer {JINA_API_KEY}"},
            )
            resp.raise_for_status()
            return resp.text[:MAX_CHARS]
    except Exception as e:
        logger.debug("Jina unavailable: %s", e)
        return None


async def _read_direct(url: str) -> str | None:
    for attempt in range(1 + MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
                resp = await client.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; Blog-Agent/0.1)"},
                )
                resp.raise_for_status()
        except Exception as e:
            if attempt < MAX_RETRIES:
                import asyncio
                await asyncio.sleep(0.5)
                continue
            return None
        else:
            break

    text = resp.text
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_CHARS]


def _extract_domain(url: str) -> str:
    m = re.match(r"https?://([^/]+)", url)
    return m.group(1) if m else ""


# ===== Tool =====
@tool
async def fetch_page(url: str) -> dict:
    """读取网页全文内容。

    输入一个 URL，返回该网页的文本内容（去除 HTML，最多 6000 字符）。
    用于深入阅读搜索到的相关资料。

    Args:
        url: 网页地址
    """
    logger.info("fetch_page: url=%r", url[:80])

    content = await _read_via_jina(url)
    provider = "jina"
    if content is None:
        content = await _read_direct(url)
        provider = "direct"

    if content is None:
        return {
            "ok": False,
            "url": url,
            "domain": _extract_domain(url),
            "content": "",
            "error": "fetch_failed",
        }

    logger.info("fetch_page ok: provider=%s chars=%d", provider, len(content))
    return {
        "ok": True,
        "url": url,
        "domain": _extract_domain(url),
        "provider": provider,
        "content": content,
    }
