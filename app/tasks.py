"""Task lifecycle management for analysis jobs."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Optional
from uuid import uuid4

from .models import AnalysisTask, AnalysisTaskOptions
from .storage import AnalysisTaskStore, MaterialStore


class TaskManagerError(Exception):
    """Raised when task validation fails."""


class TaskManager:
    """Create, persist, and update analysis tasks."""

    def __init__(self, store: AnalysisTaskStore, material_store: MaterialStore) -> None:
        self._store = store
        self._material_store = material_store

    def create_task(self, material_ids: Iterable[str], options: Optional[dict]) -> AnalysisTask:
        material_ids = list(material_ids)
        if not material_ids:
            raise TaskManagerError("materials 不能为空")

        for material_id in material_ids:
            if not self._material_store.get(material_id):
                raise TaskManagerError(f"材料 {material_id} 不存在")

        try:
            options_obj = AnalysisTaskOptions(**options) if options else None
        except ValueError as exc:
            raise TaskManagerError(str(exc)) from exc
        now = datetime.now(timezone.utc)
        task = AnalysisTask(
            id=f"tsk_{uuid4().hex[:8]}",
            status="queued",
            materials=material_ids,
            created_at=now,
            updated_at=now,
            options=options_obj,
        )
        self._store.save(task)
        return task

    def mark_running(self, task_id: str) -> AnalysisTask:
        task = self.require(task_id)
        task.status = "running"
        task.updated_at = datetime.now(timezone.utc)
        self._store.save(task)
        return task

    def mark_succeeded(self, task_id: str, result_id: str) -> AnalysisTask:
        task = self.require(task_id)
        task.status = "succeeded"
        task.result_id = result_id
        task.error_message = None
        task.updated_at = datetime.now(timezone.utc)
        self._store.save(task)
        return task

    def mark_failed(self, task_id: str, message: str) -> AnalysisTask:
        task = self.require(task_id)
        task.status = "failed"
        task.error_message = message
        task.updated_at = datetime.now(timezone.utc)
        self._store.save(task)
        return task

    def get(self, task_id: str) -> Optional[AnalysisTask]:
        return self._store.get(task_id)

    def require(self, task_id: str) -> AnalysisTask:
        task = self._store.get(task_id)
        if not task:
            raise TaskManagerError("任务不存在")
        return task


__all__ = ["TaskManager", "TaskManagerError"]
