"""条件路由函数 — 纯函数，不调 LLM。"""

import logging

from .state import BlogState

logger = logging.getLogger(__name__)


def route_intent(state: BlogState) -> str:
    """根据意图和当前阶段路由。"""
    stage = state.get("current_stage", "")
    intent = state.get("intent", "UNCLEAR")

    if stage == "WAITING_INPUT":
        logger.info("route: intent=%s stage=WAITING_INPUT → requirement_analyzer", intent)
        return "requirement_analyzer"

    logger.info("route: intent=%s → %s", intent, intent)
    return intent


def route_after_discuss(state: BlogState) -> str:
    """discuss_topic 之后：是否需要进入需求分析。"""
    stage = state.get("current_stage", "")
    dest = "requirement_analyzer" if stage == "REQUIREMENT_ANALYSIS" else "END"
    logger.info("route: after discuss stage=%s → %s", stage, dest)
    return dest


def route_requirement(state: BlogState) -> str:
    """需求分析之后：完整 → 研究路由，不完整 → 澄清。"""
    req = state.get("requirement")
    status = req.status if req else "no_requirement"
    dest = "clarify_requirement" if (req is None or req.status == "INCOMPLETE") else "research_router"
    logger.info("route: requirement status=%s → %s", status, dest)
    return dest


def route_research(state: BlogState) -> str:
    """博客创作总是需要搜索研究——LLM 内部知识不足以支撑高质量博客。

    need_external_research 字段保留供未来场景使用
    （例如用户提供完整素材、明确要求不搜索时）。
    """
    dest = "research"
    logger.info("route: → research（博客创作默认搜索）")
    return dest


def route_after_review(state: BlogState) -> str:
    """审核之后：分数不达标且未达最大修订次数 → 修订，否则 → 事实核查。"""
    review = state.get("review")
    revision_count = state.get("revision_count", 0)
    max_revisions = 1

    if review:
        logger.info(
            "route: review score=%s approved=%s revisions=%s/%s",
            review.score, review.approved, revision_count, max_revisions,
        )
    should_revise = review and review.score < 85 and revision_count < max_revisions
    dest = "revision" if should_revise else "factcheck"
    logger.info("route: after review → %s", dest)
    return dest
