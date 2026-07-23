"""Pydantic / 结构化输出 schemas。

包含意图分类 schema、需求分析的 BlogRequirement 等。
"""

from typing import Literal

from pydantic import BaseModel, Field

# ===== 意图分类 =====
INTENT_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "blog_intent",
        "schema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": ["BLOG_CREATION", "NON_BLOG", "UNCLEAR"],
                },
                "reason": {"type": "string"},
            },
            "required": ["intent", "reason"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}

# ===== 需求分析 =====
BlogType = Literal[
    "tutorial", "project_review", "technical_note",
    "concept_explainer", "opinion", "personal_story", "other",
]
TechnicalDepth = Literal["beginner", "intermediate", "advanced"]
RequirementStatus = Literal["COMPLETE", "INCOMPLETE"]
MaterialType = Literal["experience", "opinion", "data", "example", "code", "note", "other"]


class TopicBrief(BaseModel):
    """discuss_topic 输出的主题摘要。"""
    topic: str = ""
    direction: str = ""
    blog_type_hint: str | None = None
    confirmed: bool = False


class PersonalMaterial(BaseModel):
    content: str
    material_type: MaterialType = "other"


class BlogRequirement(BaseModel):
    """需求分析的结构化输出。"""

    # 文章定位
    topic: str
    direction: str
    blog_type: BlogType
    core_thesis: str | None = None

    # 写作对象与目的
    target_audience: str | None = None
    writing_goal: str | None = None
    reader_takeaway: str | None = None

    # 内容规格
    target_length: int = Field(default=2500, ge=500, le=15000)
    language: str = "zh-CN"
    tone: str = "专业、自然、通俗"
    technical_depth: TechnicalDepth = "intermediate"
    use_first_person: bool = True

    # 用户素材（只从用户实际输入提取，不编造）
    personal_materials: list[PersonalMaterial] = []
    reference_materials: list[str] = []

    # 后续流程需求
    need_external_research: bool = Field(
        default=True,
        description=(
            "是否需要搜索外部资料。默认总是 True，即使用户提供了素材也要搜索——"
            "用户素材是补充，不是替代。仅在用户明确说'不要联网搜索，只基于我给的素材创作'时设为 False。"
        ),
    )
    need_code_examples: bool = False
    need_code_validation: bool = False

    # 约束
    must_include: list[str] = []
    must_avoid: list[str] = []
    assumptions: list[str] = []       # 推断的内容
    inferred_fields: list[str] = []   # 哪些字段是推断的
    defaulted_fields: list[str] = []  # 哪些字段用了默认值

    # 完整性
    missing_fields: list[str] = []
    next_question: str | None = None
    status: RequirementStatus


class WritingDefaults(BaseModel):
    """个人写作默认配置。"""
    language: str = "zh-CN"
    target_length: int = 2500
    tone: str = "专业、自然、通俗"
    technical_depth: TechnicalDepth = "intermediate"
    use_markdown: bool = True
    use_first_person: bool = True


# ===== 研究 =====
class ResearchSource(BaseModel):
    """单个研究来源。"""
    title: str
    url: str
    summary: str = ""
    source_type: str = "web"
    quality: str = "medium"  # high | medium | low


class ResearchFinding(BaseModel):
    """单个研究发现，每个结论必须关联来源。"""
    topic: str
    conclusion: str
    source_indices: list[int] = []  # 引用 ResearchReport.sources 的下标


class ResearchReport(BaseModel):
    """结构化研究报告。"""
    research_questions: list[str] = []
    findings: list[ResearchFinding] = []
    sources: list[ResearchSource] = []
    missing_information: list[str] = []
    writing_suggestions: str = ""
    confidence: str = "medium"  # high | medium | low


class ResearchContext(BaseModel):
    """研究 Agent 的输入上下文——从 BlogRequirement 提取。"""
    topic: str
    direction: str
    audience: str = ""
    blog_type: str = ""
    technical_depth: str = "intermediate"
    need_code: bool = False
    user_materials: list[str] = []


# ===== 规划 =====
class OutlineSection(BaseModel):
    """大纲中的一节。"""
    order: int
    title: str
    purpose: str = ""          # 这一节为什么存在（回答什么问题）
    key_points: list[str] = []  # 核心内容要点
    estimated_words: int = 500  # 预估字数


class BlogOutline(BaseModel):
    """结构化文章大纲。"""
    title: str
    subtitle: str = ""
    introduction_goal: str = ""    # 开头要达到什么效果
    sections: list[OutlineSection] = []
    conclusion_goal: str = ""      # 结尾要传达什么
    article_style: str = ""        # 风格描述


# ===== 写作 =====
class ArticleSection(BaseModel):
    """文章中的一个章节。"""
    title: str
    markdown: str
    summary: str = ""   # 叙事上下文（一句摘要，供后续章节避免重复）
    order: int = 0


class ArticleDraft(BaseModel):
    """Writer 输出的完整文章草稿。"""
    title: str
    markdown: str                          # 完整正文
    sections: list[ArticleSection] = []    # 逐章节明细
    tags: list[str] = []
    metadata: dict = {}


# ===== 审核 =====
IssueSeverity = Literal["high", "medium", "low"]
IssueType = Literal["coherence", "accuracy", "structure", "readability", "practicality", "style", "other"]


class ReviewIssue(BaseModel):
    """审核中发现的问题。"""
    severity: IssueSeverity = "medium"
    location: str = ""          # 章节或位置描述
    issue_type: IssueType = "other"
    description: str
    suggestion: str = ""


class ReviewReport(BaseModel):
    """综合审核报告（合并 ThreadChecker + Reviewer）。"""
    score: int = 0                    # 综合评分 0-100
    approved: bool = False
    coherence_score: int = 0         # 跨章节连贯性评分 0-100
    has_blocking_issues: bool = False
    issues: list[ReviewIssue] = []
    summary: str = ""


# ===== 修订 =====
class RevisedDraft(BaseModel):
    """Revision 节点输出的修订稿。JSON 包裹避免 Markdown 解析歧义。"""
    title: str
    markdown: str
    tags: list[str] = []


# ===== 事实核查 =====
FactCheckVerdict = Literal["supported", "contradicted", "unverified"]


class FactCheckClaim(BaseModel):
    """被核查的单条事实声明。"""
    claim: str
    verdict: FactCheckVerdict = "unverified"
    evidence: str = ""
    source_title: str | None = None
    source_url: str | None = None
    suggestion: str = ""


class FactCheckReport(BaseModel):
    """事实核查报告。"""
    overall_score: int = 0
    supported: int = 0
    contradicted: int = 0
    unverified: int = 0
    claims: list[FactCheckClaim] = []
    summary: str = ""
