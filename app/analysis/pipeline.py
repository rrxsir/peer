"""LangGraph-based analysis pipeline orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from ..models import (
    AnalysisKeyPoints,
    AnalysisStep,
    AnalysisTask,
    AnalysisWeights,
    CapabilityProfile,
    LogicAxes,
    Material,
    RepresentativeOutputs,
    Suggestions,
    SummarySection,
)
from . import components
from .llm import SimulatedLLM

try:  # pragma: no cover - optional dependency
    from langgraph.graph import END, START, Graph
except Exception:  # pragma: no cover - best effort fallback
    Graph = None  # type: ignore[assignment]
    START = "__start__"
    END = "__end__"


@dataclass
class AnalysisPipelineOutput:
    weights: AnalysisWeights
    key_points: AnalysisKeyPoints
    logic_axes: LogicAxes
    capability_profile: CapabilityProfile
    representative_outputs: RepresentativeOutputs
    suggestions: Suggestions
    summary_sections: List[SummarySection]
    analysis_steps: List[AnalysisStep]


class LangGraphAnalysisPipeline:
    """Run the analysis workflow using a LangGraph graph when available."""

    def __init__(
        self,
        llm_factory: Optional[Callable[[int], SimulatedLLM]] = None,
    ) -> None:
        self._llm_factory = llm_factory or (lambda seed: SimulatedLLM(seed))
        self._graph = self._build_graph()

    def run(self, *, task: AnalysisTask, materials: List[Material], language: str) -> AnalysisPipelineOutput:
        seed = sum(len(mat.name) for mat in materials) or 1
        context = {
            "task": task,
            "materials": materials,
            "language": language,
            "seed": seed,
        }
        if self._graph is not None:  # pragma: no cover - depends on optional dependency
            compiled = self._graph
            result = compiled.invoke(context)
        else:
            result = self._execute_fallback(context)
        return result

    # ------------------------------------------------------------------
    # Graph construction helpers
    # ------------------------------------------------------------------
    def _build_graph(self):  # pragma: no cover - exercised only with langgraph installed
        if Graph is None:
            return None
        graph = Graph()
        graph.add_node("ingest", self._node_ingest)
        graph.add_node("plan", self._node_plan)
        graph.add_node("evaluate", self._node_evaluate)
        graph.add_node("optimise", self._node_optimise)

        graph.add_edge(START, "ingest")
        graph.add_edge("ingest", "plan")
        graph.add_edge("plan", "evaluate")
        graph.add_edge("evaluate", "optimise")
        graph.add_edge("optimise", END)
        return graph.compile()

    # ------------------------------------------------------------------
    # Fallback execution (used in tests when langgraph is unavailable)
    # ------------------------------------------------------------------
    def _execute_fallback(self, context: dict) -> AnalysisPipelineOutput:
        stage_one = self._node_ingest(context)
        stage_two = self._node_plan(stage_one)
        stage_three = self._node_evaluate(stage_two)
        return self._node_optimise(stage_three)

    # ------------------------------------------------------------------
    # Node implementations
    # ------------------------------------------------------------------
    def _node_ingest(self, context: dict) -> dict:
        materials: List[Material] = context["materials"]
        key_points = components.extract_key_points(materials)
        return {**context, "key_points": key_points}

    def _node_plan(self, context: dict) -> dict:
        seed: int = context["seed"]
        llm = self._llm_factory(seed)
        context["llm"] = llm
        return context

    def _node_evaluate(self, context: dict) -> dict:
        seed: int = context["seed"]
        task: AnalysisTask = context["task"]
        materials: List[Material] = context["materials"]
        language: str = context["language"]
        llm: SimulatedLLM = context["llm"]
        key_points: AnalysisKeyPoints = context["key_points"]

        weights = components.generate_weights(seed)
        capability = components.generate_capability_profile(seed)
        logic_axes = components.generate_logic_axes()
        representative_outputs = components.generate_representative_outputs()
        suggestions = components.generate_suggestions()
        summary_sections = components.build_summary_sections(language)
        analysis_steps = llm.draft_steps(
            task=task,
            materials=materials,
            capability=capability,
            suggestions=suggestions,
        )

        return {
            **context,
            "weights": weights,
            "capability": capability,
            "logic_axes": logic_axes,
            "representative_outputs": representative_outputs,
            "suggestions": suggestions,
            "summary_sections": summary_sections,
            "analysis_steps": analysis_steps,
        }

    def _node_optimise(self, context: dict) -> AnalysisPipelineOutput:
        return AnalysisPipelineOutput(
            weights=context["weights"],
            key_points=context["key_points"],
            logic_axes=context["logic_axes"],
            capability_profile=context["capability"],
            representative_outputs=context["representative_outputs"],
            suggestions=context["suggestions"],
            summary_sections=context["summary_sections"],
            analysis_steps=context["analysis_steps"],
        )


__all__ = ["AnalysisPipelineOutput", "LangGraphAnalysisPipeline"]
