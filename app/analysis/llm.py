"""LLM abstractions used by the analysis workflow."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List

from ..models import AnalysisStep, AnalysisTask, CapabilityProfile, Material, Suggestions


@dataclass
class SimulatedLLM:
    """Deterministic stand-in for a large language model.

    The implementation consumes the task seed to keep the test environment stable
    while still reflecting how a LangGraph pipeline would coordinate with an LLM.
    """

    seed: int

    def _random(self) -> random.Random:
        return random.Random(self.seed)

    def draft_steps(
        self,
        *,
        task: AnalysisTask,
        materials: List[Material],
        capability: CapabilityProfile,
        suggestions: Suggestions,
    ) -> List[AnalysisStep]:
        rnd = self._random()
        material_names = ", ".join(mat.name for mat in materials)
        applicant = materials[0].meta.applicant_name if materials else "候选人"
        coverage = 70 + rnd.randint(0, 20)
        innovation = 65 + rnd.randint(0, 25)

        return [
            AnalysisStep(
                name="材料快速理解",
                objective="梳理上传文件的结构化要点，定位岗位匹配证据",
                findings=(
                    f"LangGraph 节点整合 {len(materials)} 份材料（{material_names}），"
                    f"提取候选人 {applicant} 的核心经历并量化覆盖度 {coverage}%。"
                ),
                optimizations=[
                    "建议补充最近两年的具体量化成果佐证",
                    "可上传教学或产业合作附件，提升多维度表现",
                ],
            ),
            AnalysisStep(
                name="能力评估与风险扫描",
                objective="从科研、教学、服务三维度量化能力并识别潜在风险",
                findings=(
                    "大模型基于知识图谱推理科研创新指数 "
                    f"{capability.originality}，并结合跨项目数据识别合作风险低。"
                ),
                optimizations=[
                    "针对教学指标，可引入学生反馈与毕业率提升数据",
                    "建立定期的成果复盘节奏，强化持续创新能力",
                ],
            ),
            AnalysisStep(
                name="匹配度优化建议",
                objective="输出专家分配与回避策略，辅助人工决策优化",
                findings=(
                    "LangGraph 汇总的分配策略建议优先匹配 AI 与教育技术方向专家，"
                    f"并自动生成 {len(suggestions.avoidance)} 条回避清单。"
                ),
                optimizations=[
                    "结合专家画像库动态更新回避名单",
                    "在评审阶段引入实时反馈，进一步优化席位配置",
                ],
            ),
        ]

    def build_summary_sections(self, language: str) -> List[str]:  # pragma: no cover - helper
        if language == "en-US":
            return [
                "Focuses on trustworthy recommendation and education data governance.",
                "Highlights interpretable evidence-chain research recognised by awards.",
                "Delivers patents, major grants, and repeatable teaching improvements.",
            ]
        return [
            "长期深耕智能推荐与教育数据治理，可支撑大规模项目落地。",
            "提出可解释证据链方法，科研成果转化潜力强。",
            "教学成果闭环明显，具备跨单位推广条件。",
        ]

