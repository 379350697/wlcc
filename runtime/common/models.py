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
    taskLevel: str = "leaf"
    parentTaskId: str = ""
    taskFlowId: str = ""
    ownerSessionId: str = ""
    phase: str = "analyze"
    doneWhen: list[str] = field(default_factory=list)
    requiredEvidence: list[str] = field(default_factory=lambda: ["state-update"])
    requiredTests: list[str] = field(default_factory=list)
    allowedPaths: list[str] = field(default_factory=lambda: ["."])
    forbiddenPaths: list[str] = field(default_factory=list)
    maxTurns: int = 8
    maxMinutes: int = 20
    turnCount: int = 0
    riskLevel: str = "medium"
    estimatedTurns: int = 0
    estimatedMinutes: int = 0
    splitConfidence: float = 0.0
    finalReplyEligible: bool = False

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
            "taskLevel": self.taskLevel,
            "parentTaskId": self.parentTaskId,
            "taskFlowId": self.taskFlowId,
            "ownerSessionId": self.ownerSessionId,
            "phase": self.phase,
            "doneWhen": list(self.doneWhen),
            "requiredEvidence": list(self.requiredEvidence),
            "requiredTests": list(self.requiredTests),
            "allowedPaths": list(self.allowedPaths),
            "forbiddenPaths": list(self.forbiddenPaths),
            "maxTurns": self.maxTurns,
            "maxMinutes": self.maxMinutes,
            "turnCount": self.turnCount,
            "riskLevel": self.riskLevel,
            "estimatedTurns": self.estimatedTurns,
            "estimatedMinutes": self.estimatedMinutes,
            "splitConfidence": self.splitConfidence,
            "finalReplyEligible": self.finalReplyEligible,
        }
