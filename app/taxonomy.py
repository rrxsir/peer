"""Discipline taxonomy provider."""
from __future__ import annotations

from typing import List

from .models import TaxonomyResponse


class TaxonomyService:
    """Return supported disciplines for the platform."""

    def __init__(self, disciplines: List[str]) -> None:
        self._disciplines = disciplines

    def list_disciplines(self) -> TaxonomyResponse:
        return TaxonomyResponse(list(self._disciplines))


__all__ = ["TaxonomyService"]
