"""Version reporting utilities."""
from __future__ import annotations

from datetime import datetime, timezone

from .models import VersionResponse


class VersionService:
    """Keep track of service metadata and uptime."""

    def __init__(self, *, service: str, version: str, commit: str) -> None:
        self._service = service
        self._version = version
        self._commit = commit
        self._start_time = datetime.now(timezone.utc)

    def get_version(self) -> VersionResponse:
        uptime = int((datetime.now(timezone.utc) - self._start_time).total_seconds())
        return VersionResponse(
            service=self._service,
            version=self._version,
            commit=self._commit,
            uptime_seconds=uptime,
        )


__all__ = ["VersionService"]
