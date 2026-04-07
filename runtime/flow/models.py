from __future__ import annotations

from dataclasses import dataclass
from typing import Any


OPEN_FLOW_STATUSES = {"ready", "running", "verify"}
BLOCKED_FLOW_STATUSES = {"blocked"}
WAITING_FLOW_STATUSES = {"waiting-human"}
CLOSED_FLOW_STATUSES = {"closed", "done", "archived"}


@dataclass
class TaskFlowRecord:
    taskFlowId: str
    ownerSessionId: str = ""
    entryMode: str = "wlcc-live"
    goal: str = ""
    status: str = "draft"
    currentLeafTaskId: str | None = None
    closedLeafCount: int = 0
    openLeafCount: int = 0
    lastClosureTaskId: str | None = None
    lastStatusUpdateAt: str = ""
    replyMode: str = "restricted"
    createdAt: str = ""
    updatedAt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskFlowId": self.taskFlowId,
            "ownerSessionId": self.ownerSessionId,
            "entryMode": self.entryMode,
            "goal": self.goal,
            "status": self.status,
            "currentLeafTaskId": self.currentLeafTaskId,
            "closedLeafCount": self.closedLeafCount,
            "openLeafCount": self.openLeafCount,
            "lastClosureTaskId": self.lastClosureTaskId,
            "lastStatusUpdateAt": self.lastStatusUpdateAt,
            "replyMode": self.replyMode,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }


def normalize_flow_dict(payload: dict | None) -> dict[str, Any]:
    payload = dict(payload or {})
    flow = TaskFlowRecord(
        taskFlowId=str(payload.get("taskFlowId", "") or ""),
        ownerSessionId=str(payload.get("ownerSessionId", "") or ""),
        entryMode=str(payload.get("entryMode", "wlcc-live") or "wlcc-live"),
        goal=str(payload.get("goal", "") or ""),
        status=str(payload.get("status", "draft") or "draft"),
        currentLeafTaskId=(None if payload.get("currentLeafTaskId") in {None, ""} else str(payload.get("currentLeafTaskId"))),
        closedLeafCount=max(int(payload.get("closedLeafCount", 0) or 0), 0),
        openLeafCount=max(int(payload.get("openLeafCount", 0) or 0), 0),
        lastClosureTaskId=(None if payload.get("lastClosureTaskId") in {None, ""} else str(payload.get("lastClosureTaskId"))),
        lastStatusUpdateAt=str(payload.get("lastStatusUpdateAt", "") or ""),
        replyMode=str(payload.get("replyMode", "restricted") or "restricted"),
        createdAt=str(payload.get("createdAt", "") or ""),
        updatedAt=str(payload.get("updatedAt", "") or ""),
    )
    return flow.to_dict()


def derive_flow_status(tasks: list[dict]) -> str:
    if not tasks:
        return "draft"

    statuses = {str(task.get("status", "") or "").strip() for task in tasks}
    lifecycles = {str(task.get("lifecycle", "") or "").strip() for task in tasks}

    if statuses & OPEN_FLOW_STATUSES or lifecycles & OPEN_FLOW_STATUSES:
        return "active"
    if statuses & WAITING_FLOW_STATUSES or lifecycles & WAITING_FLOW_STATUSES:
        return "waiting-human"
    if statuses & BLOCKED_FLOW_STATUSES or lifecycles & BLOCKED_FLOW_STATUSES:
        return "blocked"
    if statuses and statuses <= CLOSED_FLOW_STATUSES and (not lifecycles or lifecycles <= CLOSED_FLOW_STATUSES):
        return "completed"
    return "draft"
