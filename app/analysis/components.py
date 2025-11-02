"""Reusable component generators for the analysis pipeline."""
from __future__ import annotations

import hashlib
import random
from typing import Iterable, List

from ..models import (
    AnalysisKeyPoints,
    AnalysisTask,
    AnalysisWeights,
    CapabilityProfile,
    CapabilityRationales,
    LogicAxes,
    Material,
    RepresentativeOutputs,
    Suggestions,
    SummarySection,
    ensure_weights_sum,
)


def hash_material_prompt(material_ids: Iterable[str]) -> str:
    """Return a stable hash for the ordered material identifiers."""
    joined = ":".join(sorted(material_ids))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def generate_weights(seed: int) -> AnalysisWeights:
    rnd = random.Random(seed)
    weights = AnalysisWeights(
        research=rnd.uniform(0.45, 0.75),
        teaching=rnd.uniform(0.15, 0.35),
        service=rnd.uniform(0.05, 0.25),
        topics=["智能推荐可信度", "教育知识图谱", "教学行为分析"],
    )
    return ensure_weights_sum(weights)


def generate_capability_profile(seed: int) -> CapabilityProfile:
    rnd = random.Random(seed)
    return CapabilityProfile(
        originality=rnd.randint(70, 95),
        engineering=rnd.randint(65, 90),
        talent_training=rnd.randint(60, 88),
        organization=rnd.randint(60, 90),
        rationales=CapabilityRationales(
            originality="在教育场景中提出多模态语义对齐方法并被广泛引用",
            engineering="建设教学数据治理平台，实现多校部署",
            talent_training="指导研究生多次获得省级优秀毕业论文",
            organization="牵头跨学院协作项目，建立标准化评审流程",
        ),
    )


def generate_logic_axes() -> LogicAxes:
    return LogicAxes(
        themes=["智能推荐可信与可解释", "教育场景知识图谱", "多源学习行为融合"],
        methods=["跨模态语义对齐", "证据链追踪", "数据驱动评估"],
        evidence=["ESI 高被引论文 4 篇", "省部级奖励 3 项", "国家级重点项目 1 项"],
    )


def generate_representative_outputs() -> RepresentativeOutputs:
    return RepresentativeOutputs(
        papers_5y=24,
        ccf_a=6,
        awards=["省部级二等奖（第一完成人）"],
        projects=["国家重点研发计划子课题", "省科技厅重大专项"],
        teaching_highlights=["课堂数据闭环驱动教学迭代", "博士生省优博 2 名"],
    )


def generate_suggestions() -> Suggestions:
    return Suggestions(
        avoidance=[
            "回避同单位专家及附属单位",
            "近五年合作（论文/项目）需人工确认并回避",
            "导师-学生或直接隶属关系需回避",
        ],
        assignment=[
            "优先匹配计算机科学与技术/人工智能方向专家",
            "结合地域与职称结构优化评审席位",
        ],
        notes="AI 仅提供建议，需人工复核",
    )


def extract_key_points(materials: List[Material]) -> AnalysisKeyPoints:
    organization = None
    disciplines: list[str] = []
    keywords: list[str] = []
    for mat in materials:
        meta = mat.meta
        if not organization and meta.department:
            organization = meta.department
        if meta.position_applied:
            keywords.append(meta.position_applied)
        discipline = meta.department or mat.type.upper()
        if discipline not in disciplines:
            disciplines.append(discipline)

    return AnalysisKeyPoints(
        organization=organization or "未知单位",
        disciplines=disciplines or ["GENERAL"],
        keywords=keywords or ["学术成果", "教学贡献"],
    )


def build_summary_sections(language: str) -> List[SummarySection]:
    if language == "en-US":
        return [
            SummarySection(
                title="Academic Background & Fit",
                content=(
                    "Synthesised by the LLM: the applicant specialises in trustworthy "
                    "recommendation and educational data governance with clear alignment "
                    "to strategic national projects."
                ),
            ),
            SummarySection(
                title="Research Innovation",
                content=(
                    "LLM review highlights interpretable evidence-chain methods with high "
                    "impact publications and recognised awards."
                ),
            ),
            SummarySection(
                title="Representative Achievements",
                content=(
                    "Key deliverables include authorised patents, critical grants, and "
                    "evidence-backed teaching effectiveness."
                ),
            ),
        ]

    return [
        SummarySection(
            title="学术背景与岗位适配",
            content=(
                "大模型梳理后确认候选人长期深耕智能推荐与教育数据治理，可独立主持国家级项目，与岗位需求高度契合。"
            ),
        ),
        SummarySection(
            title="科研创新与影响力",
            content=(
                "语言模型评估显示其提出的可解释证据链方法具备行业影响力，并支撑多项高水平成果。"
            ),
        ),
        SummarySection(
            title="代表性成果与实践优化",
            content=(
                "专利、重大项目落地与教学闭环是亮点，可通过跨校数据联动进一步优化推广路径。"
            ),
        ),
    ]

