from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvidenceRecord:
    evidenceType: str
    source: str
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    recordedAt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidenceType": self.evidenceType,
            "source": self.source,
            "summary": self.summary,
            "details": dict(self.details),
            "recordedAt": self.recordedAt,
        }


@dataclass
class TaskState:
    taskId: str
    project: str
    goal: str
    status: str
    priority: str = "P2"
    dependencies: list[str] = field(default_factory=list)
    override: str = "none"
    latestResult: str = ""
    blocker: str = "无"
    nextStep: str = ""
    lastSuccess: str = ""
    lastFailure: str = ""
    updatedAt: str = ""
    kind: str = "sample"
    source: str = "legacy"
    executionMode: str = "sample-only"
    ownerContext: str = "unknown"
    supervisionState: str = "legacy"
    eligibleForScheduling: bool = False
    isPrimaryTrack: bool = False
    lifecycle: str = "legacy"
    title: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskId": self.taskId,
            "project": self.project,
            "goal": self.goal,
            "status": self.status,
            "priority": self.priority,
            "dependencies": list(self.dependencies),
            "override": self.override,
            "latestResult": self.latestResult,
            "blocker": self.blocker,
            "nextStep": self.nextStep,
            "lastSuccess": self.lastSuccess,
            "lastFailure": self.lastFailure,
            "updatedAt": self.updatedAt,
            "kind": self.kind,
            "source": self.source,
            "executionMode": self.executionMode,
            "ownerContext": self.ownerContext,
            "supervisionState": self.supervisionState,
            "eligibleForScheduling": self.eligibleForScheduling,
            "isPrimaryTrack": self.isPrimaryTrack,
            "lifecycle": self.lifecycle,
            "title": self.title,
        }
