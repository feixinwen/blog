"""主图构建 — 只负责连接节点，不写业务逻辑。"""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .nodes.chat_response import clarify_intent, discuss_topic, fallback_response
from .nodes.clarify_requirement import clarify_requirement
from .nodes.intent_classifier import classify_intent
from .nodes.planner import planner
from .nodes.requirement_analyzer import analyze_requirement
from .nodes.research import research
from .nodes.assembler import assembler
from .nodes.factcheck import factcheck
from .nodes.reviewer import reviewer
from .nodes.revision import revision
from .nodes.writer import writer
from .routes import route_after_discuss, route_after_review, route_intent, route_requirement, route_research
from .state import BlogState

logger = logging.getLogger(__name__)

STAGE_MESSAGES: dict[str, str] = {
    "classify_intent": "正在分析意图...",
    "discuss_topic": "正在讨论主题...",
    "requirement_analyzer": "正在分析需求...",
    "clarify_requirement": "正在收集更多信息...",
    "research": "正在搜索资料...",
    "planner": "正在规划大纲...",
    "writer": "正在撰写文章...",
    "reviewer": "正在审核质量...",
    "revision": "正在修订文章...",
    "factcheck": "正在核查事实...",
    "assembler": "正在整理排版...",
}


class BlogGraph:
    """LangGraph 驱动的博客创作助手主图。"""

    def __init__(self) -> None:
        self._memory = MemorySaver()
        self._graph = self._build().compile(checkpointer=self._memory)

    # ===== 流式入口 =====
    async def stream(
        self, message: str, *, thread_id: str = "default"
    ) -> AsyncGenerator[str, None]:
        logger.info("BlogGraph stream: thread=%s msg=%s", thread_id, message[:50])
        config = {"configurable": {"thread_id": thread_id}}

        full_text = ""
        async for event in self._graph.astream_events(
            {
                "messages": [HumanMessage(content=message)],
                "user_input": message,
                "intent": "",
                "current_stage": "",
                "topic_brief": None,
                "requirement": None,
                "requirement_status": "",
                "writing_defaults": None,
                "outline": None,
                "draft": None,
                "review": None,
                "revision_count": 0,
                "fact_check": None,
                "research_notes": "",
                "research_report": None,
            },
            config,
            version="v2",
        ):
            kind = event.get("event")
            name = event.get("name", "")

            # 节点进度推送
            if kind == "on_chain_start" and name in STAGE_MESSAGES:
                yield f"data: {_sse({'stage': name, 'status': 'started', 'message': STAGE_MESSAGES[name]})}\n\n"
            elif kind == "on_chain_end" and name in STAGE_MESSAGES:
                yield f"data: {_sse({'stage': name, 'status': 'completed'})}\n\n"

            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    full_text += chunk.content
                    yield f"data: {_sse({'token': chunk.content})}\n\n"

        yield f"data: {_sse({'done': True})}\n\n"

        # 最终草稿推送给前端
        try:
            snapshot = self._graph.get_state(config)
            if snapshot.values:
                draft = snapshot.values.get("draft")
                if draft and draft.markdown:
                    yield f"data: {_sse({'article': {'title': draft.title, 'content': draft.markdown, 'summary': draft.sections[0].summary if draft.sections else '', 'tags': draft.tags}})}\n\n"
        except Exception:
            logger.exception("Failed to extract final draft from graph state")

        yield "data: [DONE]\n\n"

    # ===== 建图 =====
    def _build(self) -> StateGraph:
        graph = StateGraph(BlogState)

        # 节点
        graph.add_node("classify_intent", classify_intent)
        graph.add_node("fallback_response", fallback_response)
        graph.add_node("clarify_intent", clarify_intent)
        graph.add_node("discuss_topic", discuss_topic)
        graph.add_node("requirement_analyzer", analyze_requirement)
        graph.add_node("clarify_requirement", clarify_requirement)
        graph.add_node("research", research)
        graph.add_node("planner", planner)
        graph.add_node("writer", writer)
        graph.add_node("reviewer", reviewer)
        graph.add_node("revision", revision)
        graph.add_node("factcheck", factcheck)
        graph.add_node("assembler", assembler)

        # 入口 → 意图分类
        graph.add_edge(START, "classify_intent")
        graph.add_conditional_edges("classify_intent", route_intent, {
            "BLOG_CREATION": "discuss_topic",
            "NON_BLOG": "fallback_response",
            "UNCLEAR": "clarify_intent",
            "requirement_analyzer": "requirement_analyzer",
        })

        # fallback / clarify → END
        graph.add_edge("fallback_response", END)
        graph.add_edge("clarify_intent", END)

        # discuss_topic → 是否 [GENERATE]
        graph.add_conditional_edges("discuss_topic", route_after_discuss, {
            "requirement_analyzer": "requirement_analyzer",
            "END": END,
        })

        # requirement_analyzer → COMPLETE → research_router → research/planner
        graph.add_conditional_edges("requirement_analyzer", route_requirement, {
            "clarify_requirement": "clarify_requirement",
            "research_router": "research_router",
        })

        # clarify_requirement → END
        graph.add_edge("clarify_requirement", END)

        # 伪节点 research_router（LangGraph 需要实体节点来路由）
        # 用 no-op 节点 + 立即条件边实现
        def _no_op(state: BlogState) -> dict:
            return {}
        graph.add_node("research_router", _no_op)
        graph.add_conditional_edges("research_router", route_research, {
            "research": "research",
            "planner": "planner",
        })

        # research → planner → writer → reviewer ⇄ revision → factcheck → assembler → END
        graph.add_edge("research", "planner")
        graph.add_edge("planner", "writer")
        graph.add_edge("writer", "reviewer")
        graph.add_conditional_edges("reviewer", route_after_review, {
            "revision": "revision",
            "factcheck": "factcheck",
        })
        graph.add_edge("revision", "reviewer")
        graph.add_edge("factcheck", "assembler")
        graph.add_edge("assembler", END)

        return graph


def _sse(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)


_blog_graph: BlogGraph | None = None


def get_blog_graph() -> BlogGraph:
    global _blog_graph
    if _blog_graph is None:
        _blog_graph = BlogGraph()
    return _blog_graph
