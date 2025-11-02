"""Material management handling upload and retrieval responsibilities."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Sequence, Tuple
from uuid import uuid4

from .models import ALLOWED_MATERIAL_TYPES, Material, MaterialMeta, MaterialUploadResponse
from .storage import MaterialStore


class MaterialManagerError(Exception):
    """Raised when material operations fail validation."""


class MaterialManager:
    """Create and retrieve materials while enforcing validation rules."""

    def __init__(self, store: MaterialStore) -> None:
        self._store = store

    @staticmethod
    def _detect_material_type(filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        mapping = {"pdf": "pdf", "docx": "docx", "txt": "txt", "png": "image", "jpg": "image", "jpeg": "image"}
        return mapping.get(ext, "other")

    @staticmethod
    def _hash_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def upload(self, files: Sequence[Tuple[str, bytes]], meta: Optional[dict]) -> MaterialUploadResponse:
        if not files:
            raise MaterialManagerError("至少上传一个文件")

        try:
            meta_obj = MaterialMeta(**(meta or {}))
        except TypeError as exc:  # pragma: no cover - defensive path
            raise MaterialManagerError(f"元信息格式错误: {exc}") from exc

        materials: List[Material] = []
        for filename, content in files:
            material_type = self._detect_material_type(filename)
            if material_type not in ALLOWED_MATERIAL_TYPES:
                raise MaterialManagerError(f"暂不支持的文件类型: {filename}")

            material = Material(
                id=f"mat_{uuid4().hex[:8]}",
                name=filename,
                type=material_type,
                size_bytes=len(content),
                hash_sha256=self._hash_bytes(content),
                meta=meta_obj,
                created_at=datetime.now(timezone.utc),
            )
            self._store.save(material)
            materials.append(material)

        return MaterialUploadResponse(materials)

    def exists(self, material_id: str) -> bool:
        return self._store.get(material_id) is not None

    def fetch(self, material_ids: Iterable[str]) -> List[Material]:
        return self._store.list_by_ids(list(material_ids))


__all__ = ["MaterialManager", "MaterialManagerError"]
