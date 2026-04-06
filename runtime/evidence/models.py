from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from runtime.common.models import EvidenceRecord


@dataclass
class EvidenceLedger:
    taskId: str
    version: int = 1
    updatedAt: str = ""
    entries: list[EvidenceRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskId": self.taskId,
            "version": self.version,
            "updatedAt": self.updatedAt,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidenceLedger":
        entries = []
        for item in payload.get("entries", []):
            if not isinstance(item, dict):
                continue
            entries.append(
                EvidenceRecord(
                    evidenceType=str(item.get("evidenceType", item.get("type", "unknown"))),
                    source=str(item.get("source", "unknown")),
                    summary=str(item.get("summary", "")),
                    details=dict(item.get("details", {})) if isinstance(item.get("details", {}), dict) else {},
                    recordedAt=str(item.get("recordedAt", "")),
                )
            )
        return cls(
            taskId=str(payload.get("taskId", payload.get("task_id", "unknown"))),
            version=int(payload.get("version", 1)),
            updatedAt=str(payload.get("updatedAt", "")),
            entries=entries,
        )
