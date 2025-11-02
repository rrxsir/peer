"""Dataclass models for the peer review material service."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


ALLOWED_LANGUAGES = {"zh-CN", "en-US"}
ALLOWED_PRIORITIES = {"normal", "high"}
ALLOWED_EXPORT_FORMATS = {"pdf", "docx", "md"}
ALLOWED_TASK_STATUS = {"queued", "running", "succeeded", "failed"}
ALLOWED_MATERIAL_TYPES = {"pdf", "docx", "txt", "image", "other"}


def _isoformat(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat() + "Z"


@dataclass
class MaterialMeta:
    applicant_name: Optional[str] = None
    department: Optional[str] = None
    position_applied: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "applicant_name": self.applicant_name,
            "department": self.department,
            "position_applied": self.position_applied,
        }


@dataclass
class Material:
    id: str
    name: str
    type: str
    size_bytes: int
    hash_sha256: str
    meta: MaterialMeta
    created_at: datetime

    def __post_init__(self) -> None:
        if self.type not in ALLOWED_MATERIAL_TYPES:
            raise ValueError(f"Unsupported material type: {self.type}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "size_bytes": self.size_bytes,
            "hash_sha256": self.hash_sha256,
            "meta": self.meta.to_dict(),
            "created_at": _isoformat(self.created_at),
        }


@dataclass
class MaterialUploadResponse:
    materials: List[Material]

    def to_dict(self) -> dict:
        return {"materials": [material.to_dict() for material in self.materials]}


@dataclass
class AnalysisTaskOptions:
    language: str = "zh-CN"
    priority: str = "normal"

    def __post_init__(self) -> None:
        if self.language not in ALLOWED_LANGUAGES:
            raise ValueError("language must be one of zh-CN or en-US")
        if self.priority not in ALLOWED_PRIORITIES:
            raise ValueError("priority must be normal or high")

    def to_dict(self) -> dict:
        return {"language": self.language, "priority": self.priority}


@dataclass
class AnalysisTask:
    id: str
    status: str
    materials: List[str]
    created_at: datetime
    updated_at: datetime
    options: Optional[AnalysisTaskOptions] = None
    result_id: Optional[str] = None
    error_message: Optional[str] = None

    def __post_init__(self) -> None:
        if self.status not in ALLOWED_TASK_STATUS:
            raise ValueError(f"Invalid task status: {self.status}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": self.status,
            "materials": list(self.materials),
            "created_at": _isoformat(self.created_at),
            "updated_at": _isoformat(self.updated_at),
            "options": self.options.to_dict() if self.options else None,
            "result_id": self.result_id,
            "error_message": self.error_message,
        }


@dataclass
class AnalysisWeights:
    research: float
    teaching: float
    service: float
    topics: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "research": round(self.research, 4),
            "teaching": round(self.teaching, 4),
            "service": round(self.service, 4),
            "topics": list(self.topics),
        }


@dataclass
class AnalysisKeyPoints:
    organization: Optional[str]
    disciplines: List[str]
    keywords: List[str]

    def to_dict(self) -> dict:
        return {
            "organization": self.organization,
            "disciplines": list(self.disciplines),
            "keywords": list(self.keywords),
        }


@dataclass
class LogicAxes:
    themes: List[str]
    methods: List[str]
    evidence: List[str]

    def to_dict(self) -> dict:
        return {
            "themes": list(self.themes),
            "methods": list(self.methods),
            "evidence": list(self.evidence),
        }


@dataclass
class CapabilityRationales:
    originality: Optional[str] = None
    engineering: Optional[str] = None
    talent_training: Optional[str] = None
    organization: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "originality": self.originality,
            "engineering": self.engineering,
            "talent_training": self.talent_training,
            "organization": self.organization,
        }


@dataclass
class CapabilityProfile:
    originality: int
    engineering: int
    talent_training: int
    organization: int
    rationales: CapabilityRationales = field(default_factory=CapabilityRationales)

    def to_dict(self) -> dict:
        return {
            "originality": self.originality,
            "engineering": self.engineering,
            "talent_training": self.talent_training,
            "organization": self.organization,
            "rationales": self.rationales.to_dict(),
        }


@dataclass
class RepresentativeOutputs:
    papers_5y: int
    ccf_a: int
    awards: List[str]
    projects: List[str]
    teaching_highlights: List[str]

    def to_dict(self) -> dict:
        return {
            "papers_5y": self.papers_5y,
            "ccf_a": self.ccf_a,
            "awards": list(self.awards),
            "projects": list(self.projects),
            "teaching_highlights": list(self.teaching_highlights),
        }


@dataclass
class Suggestions:
    avoidance: List[str]
    assignment: List[str]
    notes: Optional[str]

    def to_dict(self) -> dict:
        return {
            "avoidance": list(self.avoidance),
            "assignment": list(self.assignment),
            "notes": self.notes,
        }


@dataclass
class SummarySection:
    title: str
    content: str

    def to_dict(self) -> dict:
        return {"title": self.title, "content": self.content}


@dataclass
class AnalysisStep:
    name: str
    objective: str
    findings: str
    optimizations: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "objective": self.objective,
            "findings": self.findings,
            "optimizations": list(self.optimizations),
        }


@dataclass
class AnalysisResult:
    id: str
    materials: List[str]
    weights: AnalysisWeights
    key_points: AnalysisKeyPoints
    logic_axes: LogicAxes
    capability_profile: CapabilityProfile
    representative_outputs: RepresentativeOutputs
    suggestions: Suggestions
    summary_sections: List[SummarySection]
    analysis_steps: List[AnalysisStep]
    created_at: datetime
    model: str
    prompt_hash: str
    dataset_version: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "materials": list(self.materials),
            "weights": self.weights.to_dict(),
            "key_points": self.key_points.to_dict(),
            "logic_axes": self.logic_axes.to_dict(),
            "capability_profile": self.capability_profile.to_dict(),
            "representative_outputs": self.representative_outputs.to_dict(),
            "suggestions": self.suggestions.to_dict(),
            "summary_sections": [section.to_dict() for section in self.summary_sections],
            "analysis_steps": [step.to_dict() for step in self.analysis_steps],
            "created_at": _isoformat(self.created_at),
            "model": self.model,
            "prompt_hash": self.prompt_hash,
            "dataset_version": self.dataset_version,
        }


@dataclass
class AnalysisResultResponse:
    result: AnalysisResult

    def to_dict(self) -> dict:
        return {"result": self.result.to_dict()}


@dataclass
class ExportRequest:
    result_id: str
    format: str = "pdf"
    filename: Optional[str] = None

    def __post_init__(self) -> None:
        if self.format not in ALLOWED_EXPORT_FORMATS:
            raise ValueError("Unsupported export format")


@dataclass
class ExportStatus:
    id: str
    result_id: str
    format: str
    filename: str
    created_at: datetime
    download_url: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "result_id": self.result_id,
            "format": self.format,
            "filename": self.filename,
            "created_at": _isoformat(self.created_at),
            "download_url": self.download_url,
        }


@dataclass
class TaxonomyResponse:
    disciplines: List[str]

    def to_dict(self) -> dict:
        return {"disciplines": list(self.disciplines)}


@dataclass
class VersionResponse:
    service: str
    version: str
    commit: str
    uptime_seconds: int

    def to_dict(self) -> dict:
        return {
            "service": self.service,
            "version": self.version,
            "commit": self.commit,
            "uptime_seconds": self.uptime_seconds,
        }


@dataclass
class ErrorDetail:
    code: str
    message: str
    request_id: Optional[str] = None
    hint: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "request_id": self.request_id,
            "hint": self.hint,
        }


@dataclass
class ErrorResponse:
    error: ErrorDetail

    def to_dict(self) -> dict:
        return {"error": self.error.to_dict()}


def ensure_weights_sum(weights: AnalysisWeights) -> AnalysisWeights:
    total = weights.research + weights.teaching + weights.service
    if total and abs(total - 1.0) > 1e-6:
        factor = 1.0 / total
        weights.research *= factor
        weights.teaching *= factor
        weights.service *= factor
    return weights
