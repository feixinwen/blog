"""web_search 工具 —— Google 搜索（通过 Serper API）。"""

from __future__ import annotations

import logging
import os
import re
from typing import Literal

import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
SERPER_BASE_URL = os.getenv("SERPER_BASE_URL", "https://google.serper.dev/search")

# 重试配置
MAX_RETRIES = 2
RETRY_BACKOFF = 0.5  # 秒


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[一-鿿]", text))


# ===== Service =====
async def _serper_search(
    query: str,
    limit: int = 5,
    language: str = "auto",
    region: str = "auto",
) -> dict:
    """调用 Serper API。

    返回:
        {"ok": True, "results": [...], "query": ..., "provider": "serper"}
        或
        {"ok": False, "error": "...", "query": ...}
    """
    if not SERPER_API_KEY:
        return {"ok": False, "error": "search_unavailable", "query": query, "results": []}

    # 语言/地区：不根据中文强绑 cn，保持国际结果
    if language == "auto":
        hl = "zh-cn" if _contains_cjk(query) else "en"
    else:
        hl = "zh-cn" if language == "zh" else "en"
    gl = "cn" if region == "cn" else "us"

    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "gl": gl, "hl": hl, "num": min(limit, 10)}

    last_error = ""

    for attempt in range(1 + MAX_RETRIES):  # 1 次主请求 + 2 次重试
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(SERPER_BASE_URL, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as e:
            last_error = str(e)
            if e.response.status_code in (401, 403):  # 认证问题，不重试
                break
            if e.response.status_code != 429:  # 非限流不重试
                break
        except httpx.TimeoutException as e:
            last_error = f"timeout: {e}"
        except Exception as e:
            last_error = str(e)
            break
        else:
            # 成功
            results = []
            for i, item in enumerate(data.get("organic", [])[:limit]):
                url = item.get("link", "")
                domain = _extract_domain(url)
                results.append({
                    "position": i + 1,
                    "title": item.get("title", ""),
                    "url": url,
                    "snippet": item.get("snippet", ""),
                    "domain": domain,
                })
            logger.info(
                "serper_search ok: query=%r results=%d",
                query[:80], len(results),
            )
            return {"ok": True, "query": query, "provider": "serper", "results": results}

        # 重试等待
        if attempt < MAX_RETRIES:
            import asyncio
            await asyncio.sleep(RETRY_BACKOFF * (2 ** attempt))

    logger.warning("serper_search failed: query=%r error=%s", query[:80], last_error)
    return {"ok": False, "error": last_error, "query": query, "results": []}


def _extract_domain(url: str) -> str:
    m = re.match(r"https?://([^/]+)", url)
    return m.group(1) if m else ""


# ===== Tool =====
@tool
async def web_search(
    query: str,
    max_results: int = 5,
    language: Literal["auto", "zh", "en"] = "auto",
    region: Literal["auto", "cn", "us"] = "auto",
) -> dict:
    """搜索网页获取写作参考资料。

    Args:
        query: 搜索关键词（中英文均可）
        max_results: 返回结果数量（1-10）
        language: 搜索语言偏好（auto=自动，zh=中文，en=英文）
        region: 地域偏好（auto=自动，cn=中国，us=美国/国际）
    """
    logger.info("web_search: query=%r max_results=%s language=%s", query[:80], max_results, language)
    result = await _serper_search(query, limit=min(max_results, 10), language=language, region=region)
    logger.info("web_search: ok=%s results=%s", result.get("ok"), len(result.get("results", [])))
    return result
