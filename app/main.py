"""Peer review material service orchestrator built from dedicated components."""
from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple

from .analysis import AnalysisWorkflow, LangGraphAnalysisPipeline
from .exports import ExportManager, ExportManagerError
from .materials import MaterialManager, MaterialManagerError
from .models import (
    AnalysisResultResponse,
    AnalysisTask,
    ErrorDetail,
    ErrorResponse,
    ExportRequest,
    ExportStatus,
    MaterialUploadResponse,
    TaxonomyResponse,
    VersionResponse,
)
from .storage import AnalysisResultStore, AnalysisTaskStore, ExportStore, MaterialStore
from .tasks import TaskManager, TaskManagerError
from .taxonomy import TaxonomyService
from .versioning import VersionService


class ServiceError(Exception):
    """Custom exception carrying API error information."""

    def __init__(self, code: str, message: str, *, hint: Optional[str] = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(ErrorDetail(code=self.code, message=self.message, hint=self.hint))


class PeerReviewService:
    """High-level façade delegating work to single-responsibility managers."""

    def __init__(self, *, version: str = "1.0.0", commit: str = "dev") -> None:
        self.material_store = MaterialStore()
        self.task_store = AnalysisTaskStore()
        self.result_store = AnalysisResultStore()
        self.export_store = ExportStore()

        self.material_manager = MaterialManager(self.material_store)
        self.task_manager = TaskManager(self.task_store, self.material_store)
        self.analysis_workflow = AnalysisWorkflow(LangGraphAnalysisPipeline(), self.result_store)
        self.export_manager = ExportManager(self.export_store, self.result_store)
        self.taxonomy_service = TaxonomyService(
            [
                "计算机科学与技术",
                "人工智能",
                "数据挖掘",
                "自然语言处理",
                "教育技术学",
                "管理科学与工程",
            ]
        )
        self.version_service = VersionService(
            service="peerreview-material-nlp", version=version, commit=commit
        )

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------
    def upload_materials(
        self,
        files: Sequence[Tuple[str, bytes]],
        *,
        meta: Optional[dict] = None,
    ) -> MaterialUploadResponse:
        try:
            return self.material_manager.upload(files, meta)
        except MaterialManagerError as exc:
            message = str(exc)
            code = "unsupported_media_type" if "暂不支持" in message else "bad_request"
            raise ServiceError(code, message) from exc

    def create_task(self, material_ids: Iterable[str], options: Optional[dict] = None) -> AnalysisTask:
        try:
            task = self.task_manager.create_task(material_ids, options)
        except TaskManagerError as exc:
            message = str(exc)
            code = "not_found" if "不存在" in message else "bad_request"
            raise ServiceError(code, message) from exc

        running = self.task_manager.mark_running(task.id)
        materials = self.material_manager.fetch(running.materials)
        if len(materials) != len(running.materials):
            self.task_manager.mark_failed(running.id, "材料缺失")
            raise ServiceError("not_found", "材料缺失")

        language = running.options.language if running.options else "zh-CN"
        try:
            result = self.analysis_workflow.run(task=running, materials=materials, language=language)
        except Exception as exc:  # pragma: no cover - defensive guard
            self.task_manager.mark_failed(running.id, "分析失败")
            raise ServiceError("internal_error", "分析失败") from exc

        self.task_manager.mark_succeeded(running.id, result.id)
        return self.task_manager.require(running.id)

    def get_task(self, task_id: str) -> AnalysisTask:
        try:
            return self.task_manager.require(task_id)
        except TaskManagerError as exc:
            raise ServiceError("not_found", str(exc)) from exc

    def get_result(self, result_id: str) -> AnalysisResultResponse:
        result = self.result_store.get(result_id)
        if not result:
            raise ServiceError("not_found", "结果不存在")
        return AnalysisResultResponse(result)

    def create_export(self, request: ExportRequest) -> ExportStatus:
        try:
            return self.export_manager.create(request)
        except ExportManagerError as exc:
            message = str(exc)
            code = "not_found" if "不存在" in message else "bad_request"
            raise ServiceError(code, message) from exc

    def download_export(self, export_id: str) -> str:
        try:
            return self.export_manager.download(export_id)
        except ExportManagerError as exc:
            message = str(exc)
            code = "not_found" if "不存在" in message else "bad_request"
            raise ServiceError(code, message) from exc

    def list_disciplines(self) -> TaxonomyResponse:
        return self.taxonomy_service.list_disciplines()

    def get_version(self) -> VersionResponse:
        return self.version_service.get_version()


__all__ = ["PeerReviewService", "ServiceError"]
