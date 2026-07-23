"""BlogGraph 主 State。"""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

from .schemas import ArticleDraft, BlogOutline, BlogRequirement, FactCheckReport, ResearchReport, ReviewReport, TopicBrief, WritingDefaults


class BlogState(TypedDict):
    """博客创作工作流主 State。"""

    # 消息历史
    messages: Annotated[list, add_messages]

    # 当前轮用户输入
    user_input: str

    # 意图分类
    intent: str  # BLOG_CREATION | NON_BLOG | UNCLEAR

    # 工作流阶段
    current_stage: str  # "" | "DISCUSS_TOPIC" | "REQUIREMENT_ANALYSIS" | "WAITING_INPUT"

    # discuss_topic 输出
    topic_brief: TopicBrief | None

    # requirement_analyzer 输出
    requirement: BlogRequirement | None
    requirement_status: str  # "" | "COMPLETE" | "INCOMPLETE"

    # 写作默认值
    writing_defaults: WritingDefaults | None

    # research 输出
    research_notes: str                    # 中间笔记（markdown）
    research_report: ResearchReport | None # 结构化研究报告

    # planner 输出
    outline: BlogOutline | None

    # writer 输出
    draft: ArticleDraft | None

    # reviewer 输出
    review: ReviewReport | None

    # revision 计数（reviewer → revision 循环上限控制）
    revision_count: int

    # factcheck 输出
    fact_check: FactCheckReport | None
