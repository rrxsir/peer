"""High-level workflow that produces and stores analysis results."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import List

from ..models import AnalysisResult, AnalysisTask, Material
from ..storage import AnalysisResultStore
from .components import hash_material_prompt
from .pipeline import LangGraphAnalysisPipeline


class AnalysisWorkflow:
    """Execute the LangGraph pipeline and persist the resulting artefacts."""

    def __init__(self, pipeline: LangGraphAnalysisPipeline, result_store: AnalysisResultStore) -> None:
        self._pipeline = pipeline
        self._result_store = result_store

    def run(self, *, task: AnalysisTask, materials: List[Material], language: str) -> AnalysisResult:
        output = self._pipeline.run(task=task, materials=materials, language=language)
        now = datetime.now(timezone.utc)
        result = AnalysisResult(
            id=f"ars_{hashlib.sha1(task.id.encode()).hexdigest()[:8]}",
            materials=list(task.materials),
            weights=output.weights,
            key_points=output.key_points,
            logic_axes=output.logic_axes,
            capability_profile=output.capability_profile,
            representative_outputs=output.representative_outputs,
            suggestions=output.suggestions,
            summary_sections=output.summary_sections,
            analysis_steps=output.analysis_steps,
            created_at=now,
            model="langgraph-llm-sim-v1",
            prompt_hash=hash_material_prompt(task.materials),
            dataset_version="2025.10",
        )
        self._result_store.save(result)
        return result


__all__ = ["AnalysisWorkflow"]
