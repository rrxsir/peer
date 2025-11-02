"""In-memory storage for the peer review service."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .models import AnalysisResult, AnalysisTask, ExportStatus, Material


@dataclass
class MaterialStore:
    _materials: Dict[str, Material] = field(default_factory=dict)

    def save(self, material: Material) -> None:
        self._materials[material.id] = material

    def get(self, material_id: str) -> Optional[Material]:
        return self._materials.get(material_id)

    def list_by_ids(self, material_ids: list[str]) -> list[Material]:
        return [self._materials[m_id] for m_id in material_ids if m_id in self._materials]


@dataclass
class AnalysisTaskStore:
    _tasks: Dict[str, AnalysisTask] = field(default_factory=dict)

    def save(self, task: AnalysisTask) -> None:
        self._tasks[task.id] = task

    def get(self, task_id: str) -> Optional[AnalysisTask]:
        return self._tasks.get(task_id)


@dataclass
class AnalysisResultStore:
    _results: Dict[str, AnalysisResult] = field(default_factory=dict)

    def save(self, result: AnalysisResult) -> None:
        self._results[result.id] = result

    def get(self, result_id: str) -> Optional[AnalysisResult]:
        return self._results.get(result_id)


@dataclass
class ExportStore:
    _exports: Dict[str, ExportStatus] = field(default_factory=dict)

    def save(self, export: ExportStatus) -> None:
        self._exports[export.id] = export

    def get(self, export_id: str) -> Optional[ExportStatus]:
        return self._exports.get(export_id)
