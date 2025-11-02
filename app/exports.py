"""Export handling for analysis results."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .models import ExportRequest, ExportStatus
from .storage import AnalysisResultStore, ExportStore


class ExportManagerError(Exception):
    """Raised when export operations fail."""


class ExportManager:
    """Create export jobs and render formatted downloads."""

    def __init__(self, store: ExportStore, result_store: AnalysisResultStore) -> None:
        self._store = store
        self._result_store = result_store

    def create(self, request: ExportRequest) -> ExportStatus:
        result = self._result_store.get(request.result_id)
        if not result:
            raise ExportManagerError("结果不存在")

        export = ExportStatus(
            id=f"exp_{uuid4().hex[:8]}",
            result_id=request.result_id,
            format=request.format,
            filename=request.filename or f"评审摘要_{request.result_id}.{request.format}",
            created_at=datetime.now(timezone.utc),
        )
        self._store.save(export)
        return export

    def download(self, export_id: str) -> str:
        export = self._store.get(export_id)
        if not export:
            raise ExportManagerError("导出不存在")

        result = self._result_store.get(export.result_id)
        if not result:
            raise ExportManagerError("结果不存在")

        lines = [f"导出文件：{export.filename}", "", "=== 结构化摘要 ==="]
        for section in result.summary_sections:
            lines.append(f"## {section.title}")
            lines.append(section.content)
            lines.append("")

        lines.append("=== 分析过程 ===")
        for step in result.analysis_steps:
            lines.append(f"### {step.name}")
            lines.append(f"目标：{step.objective}")
            lines.append(f"结论：{step.findings}")
            if step.optimizations:
                lines.append("优化建议：")
                for item in step.optimizations:
                    lines.append(f"- {item}")
            lines.append("")

        return "\n".join(lines).strip()


__all__ = ["ExportManager", "ExportManagerError"]
