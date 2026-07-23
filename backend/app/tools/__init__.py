"""Agent 工具集。"""

from .baidu_search import baidu_search
from .fetch_page import fetch_page
from .web_search import web_search

__all__ = ["web_search", "baidu_search", "fetch_page", "RESEARCH_TOOLS"]

RESEARCH_TOOLS = [web_search, baidu_search, fetch_page]
