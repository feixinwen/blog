"""baidu_search 工具 —— 百度搜索（通过千帆 AI Search API）。

Endpoint: POST https://qianfan.baidubce.com/v2/ai_search/web_search
免费额度: 100 次/天
"""

from __future__ import annotations

import logging
import os
import re
from typing import Literal

import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

BAIDU_API_KEY = os.getenv("BAIDU_SEARCH_API_KEY", "")
BAIDU_BASE_URL = "https://qianfan.baidubce.com/v2/ai_search/web_search"
MAX_RETRIES = 2
RETRY_BACKOFF = 0.5

TimeFilter = Literal["week", "month", "semiyear", "year"]


# ===== Service =====
async def _baidu_search(
    query: str,
    top_k: int = 5,
    recency: TimeFilter | None = None,
    site: str | None = None,
) -> dict:
    """调用千帆 AI Search。

    返回:
        {"ok": True, "results": [...], "query": ..., "provider": "baidu"}
        或
        {"ok": False, "error": "...", "query": ...}
    """
    if not BAIDU_API_KEY:
        return {"ok": False, "error": "baidu_search_unavailable", "query": query, "results": []}

    headers = {
        "X-Appbuilder-Authorization": f"Bearer {BAIDU_API_KEY}",
        "Content-Type": "application/json",
    }

    # 构建请求体
    body: dict = {
        "messages": [{"content": query, "role": "user"}],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": min(top_k, 50)}],
    }
    if recency:
        body["search_recency_filter"] = recency
    if site:
        body["search_filter"] = {"match": {"site": [site]}}

    last_error = ""
    for attempt in range(1 + MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(BAIDU_BASE_URL, json=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as e:
            last_error = str(e)
            if e.response.status_code in (401, 403):
                break
            if e.response.status_code != 429:
                break
        except httpx.TimeoutException as e:
            last_error = f"timeout: {e}"
        except Exception as e:
            last_error = str(e)
            break
        else:
            results = []
            for ref in data.get("references", [])[:top_k]:
                results.append({
                    "position": ref.get("id", 0),
                    "title": ref.get("title", ""),
                    "url": ref.get("url", ""),
                    "snippet": (ref.get("content") or "")[:500],
                    "domain": _extract_domain(ref.get("url", "")),
                    "site_name": ref.get("website", ""),
                    "date": ref.get("date", ""),
                    "authority_score": ref.get("authority_score"),
                })
            logger.info("baidu_search ok: query=%r results=%d", query[:80], len(results))
            return {"ok": True, "query": query, "provider": "baidu", "results": results}

        import asyncio
        if attempt < MAX_RETRIES:
            await asyncio.sleep(RETRY_BACKOFF * (2 ** attempt))

    logger.warning("baidu_search failed: query=%r error=%s", query[:80], last_error)
    return {"ok": False, "error": last_error, "query": query, "results": []}


def _extract_domain(url: str) -> str:
    m = re.match(r"https?://([^/]+)", url)
    return m.group(1) if m else ""


# ===== Tool =====
@tool
async def baidu_search(
    query: str,
    top_k: int = 5,
    recency: Literal["week", "month", "semiyear", "year", "any"] = "any",
    site: str | None = None,
) -> dict:
    """通过百度搜索中文/国内技术资料。

    特别适合：中文技术社区（CSDN、博客园、掘金）、
    国内开源项目、中文官方文档。

    Args:
        query: 搜索关键词（中英文均可）
        top_k: 返回条数（1-50）
        recency: 时间过滤（week/month/semiyear/year/any）
        site: 限定站点域名，如 "blog.csdn.net"
    """
    logger.info("baidu_search: query=%r top_k=%s recency=%s", query[:80], top_k, recency)
    result = await _baidu_search(
        query,
        top_k=min(top_k, 50),
        recency=recency if recency != "any" else None,
        site=site,
    )
    logger.info("baidu_search: ok=%s results=%s", result.get("ok"), len(result.get("results", [])))
    return result
