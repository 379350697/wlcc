from __future__ import annotations

from dataclasses import dataclass, field


def _clean_list(values) -> list[str]:
    cleaned = []
    for value in values or []:
        text = str(value).strip()
        if text:
            cleaned.append(text)
    return cleaned


@dataclass
class LeafBundle:
    taskId: str
    parentTaskId: str
    goal: str
    allowedPaths: list[str] = field(default_factory=list)
    doneWhen: list[str] = field(default_factory=list)
    requiredEvidence: list[str] = field(default_factory=list)
    requiredTests: list[str] = field(default_factory=list)
    status: str = "draft"
    priority: str = "P2"
    riskLevel: str = "medium"
    estimatedTurns: int = 0
    estimatedMinutes: int = 0
    splitConfidence: float = 0.0

    @property
    def is_schedulable(self) -> bool:
        return self.status in {"ready", "running", "verify"}

    def to_dict(self) -> dict:
        return {
            "taskId": self.taskId,
            "parentTaskId": self.parentTaskId,
            "taskLevel": "leaf",
            "goal": self.goal,
            "allowedPaths": list(self.allowedPaths),
            "doneWhen": list(self.doneWhen),
            "requiredEvidence": list(self.requiredEvidence),
            "requiredTests": list(self.requiredTests),
            "status": self.status,
            "priority": self.priority,
            "riskLevel": self.riskLevel,
            "estimatedTurns": self.estimatedTurns,
            "estimatedMinutes": self.estimatedMinutes,
            "splitConfidence": self.splitConfidence,
        }

    def to_task_contract(self) -> dict:
        return self.to_dict()

    @classmethod
    def from_dict(cls, payload: dict) -> "LeafBundle":
        return cls(
            taskId=str(payload.get("taskId", "")).strip(),
            parentTaskId=str(payload.get("parentTaskId", "")).strip(),
            goal=str(payload.get("goal", "")).strip(),
            allowedPaths=_clean_list(payload.get("allowedPaths")),
            doneWhen=_clean_list(payload.get("doneWhen")),
            requiredEvidence=_clean_list(payload.get("requiredEvidence")),
            requiredTests=_clean_list(payload.get("requiredTests")),
            status=str(payload.get("status", "draft") or "draft").strip(),
            priority=str(payload.get("priority", "P2") or "P2").strip(),
            riskLevel=str(payload.get("riskLevel", "medium") or "medium").strip(),
            estimatedTurns=max(0, int(payload.get("estimatedTurns", 0) or 0)),
            estimatedMinutes=max(0, int(payload.get("estimatedMinutes", 0) or 0)),
            splitConfidence=float(payload.get("splitConfidence", 0.0) or 0.0),
        )


@dataclass
class TaskBundle:
    taskId: str
    goal: str
    children: list[LeafBundle] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "taskId": self.taskId,
            "goal": self.goal,
            "children": [child.to_dict() for child in self.children],
        }


@dataclass
class EpicBundle:
    epicId: str
    goal: str
    tasks: list[TaskBundle] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "epicId": self.epicId,
            "goal": self.goal,
            "tasks": [task.to_dict() for task in self.tasks],
        }
