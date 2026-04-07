from __future__ import annotations

from datetime import datetime

from runtime.common.io import read_json, write_json
from runtime.common.paths import RuntimePaths
from runtime.events.bus import publish_runtime_event
from runtime.flow.models import CLOSED_FLOW_STATUSES, OPEN_FLOW_STATUSES, TaskFlowRecord, derive_flow_status, normalize_flow_dict
from runtime.state.store import resolve_task_id


def flow_state_path(paths: RuntimePaths, task_flow_id: str):
    return paths.flows_state_dir / f"{task_flow_id}.json"


def create_task_flow(paths: RuntimePaths, flow: TaskFlowRecord | dict) -> object:
    payload = normalize_flow_dict(flow.to_dict() if isinstance(flow, TaskFlowRecord) else flow)
    path = flow_state_path(paths, payload["taskFlowId"])
    created = not path.exists()
    write_json(path, payload)
    publish_runtime_event(
        "flow.created" if created else "flow.updated",
        payload["taskFlowId"],
        "flow",
        {"status": payload["status"], "currentLeafTaskId": payload["currentLeafTaskId"]},
    )
    return path


def load_task_flow(paths: RuntimePaths, task_flow_id: str) -> dict:
    path = flow_state_path(paths, task_flow_id)
    flow = read_json(path, None)
    if flow is None:
        raise SystemExit(f"missing task flow: {task_flow_id}")
    return normalize_flow_dict(flow)


def bind_task_to_flow(paths: RuntimePaths, task_id: str, task_flow_id: str, *, owner_session_id: str = "") -> dict:
    resolved_task_id = resolve_task_id(paths, task_id)
    task_path = paths.tasks_state_dir / f"{resolved_task_id}.json"
    task = read_json(task_path, None)
    if task is None:
        raise SystemExit(f"missing task: {task_id}")
    task["taskFlowId"] = task_flow_id
    if owner_session_id:
        task["ownerSessionId"] = owner_session_id
    write_json(task_path, task)
    publish_runtime_event(
        "flow.bound",
        resolved_task_id,
        "flow",
        {"taskFlowId": task_flow_id, "ownerSessionId": owner_session_id},
    )
    return task


def recompute_flow(paths: RuntimePaths, task_flow_id: str) -> dict:
    existing = load_task_flow(paths, task_flow_id)
    previous_status = existing.get("status")
    previous_current = existing.get("currentLeafTaskId")
    owned_tasks = []
    for path in sorted(paths.tasks_state_dir.glob("*.json")):
        task = read_json(path, None) or {}
        if str(task.get("taskFlowId", "") or "") != task_flow_id:
            continue
        if str(task.get("taskLevel", "leaf") or "leaf") != "leaf":
            continue
        owned_tasks.append(task)

    status = derive_flow_status(owned_tasks)
    open_tasks = [task for task in owned_tasks if _task_state(task) in OPEN_FLOW_STATUSES]
    closed_tasks = [task for task in owned_tasks if _task_state(task) in CLOSED_FLOW_STATUSES]
    current = _select_current_leaf(open_tasks)
    last_closed = _select_latest(closed_tasks)

    existing["status"] = status
    existing["openLeafCount"] = len(open_tasks)
    existing["closedLeafCount"] = len(closed_tasks)
    existing["currentLeafTaskId"] = current.get("taskId") if current else None
    existing["lastClosureTaskId"] = last_closed.get("taskId") if last_closed else None
    if current:
        existing["lastStatusUpdateAt"] = str(current.get("updatedAt", "") or "")
        existing["updatedAt"] = str(current.get("updatedAt", "") or existing.get("updatedAt", ""))
    elif last_closed:
        existing["lastStatusUpdateAt"] = str(last_closed.get("updatedAt", "") or "")
        existing["updatedAt"] = str(last_closed.get("updatedAt", "") or existing.get("updatedAt", ""))

    create_task_flow(paths, existing)
    if existing.get("status") != previous_status or existing.get("currentLeafTaskId") != previous_current:
        publish_runtime_event(
            "flow.status.changed",
            task_flow_id,
            "flow",
            {
                "status": existing.get("status"),
                "currentLeafTaskId": existing.get("currentLeafTaskId"),
                "closedLeafCount": existing.get("closedLeafCount", 0),
                "openLeafCount": existing.get("openLeafCount", 0),
            },
        )
    return existing


def ensure_task_flow(paths: RuntimePaths, task: dict) -> dict | None:
    task_flow_id = str(task.get("taskFlowId", "") or "").strip()
    if not task_flow_id:
        return None

    path = flow_state_path(paths, task_flow_id)
    if path.exists():
        return load_task_flow(paths, task_flow_id)

    seed = TaskFlowRecord(
        taskFlowId=task_flow_id,
        ownerSessionId=str(task.get("ownerSessionId", "") or ""),
        goal=str(task.get("goal", "") or ""),
        status="draft",
        currentLeafTaskId=str(task.get("taskId", "") or "") or None,
        createdAt=str(task.get("updatedAt", "") or ""),
        updatedAt=str(task.get("updatedAt", "") or ""),
    )
    create_task_flow(paths, seed)
    return seed.to_dict()


def _task_state(task: dict) -> str:
    lifecycle = str(task.get("lifecycle", "") or "").strip()
    status = str(task.get("status", "") or "").strip()
    return lifecycle or status


def _select_current_leaf(tasks: list[dict]) -> dict | None:
    if not tasks:
        return None
    return sorted(tasks, key=lambda task: (_sort_rank(task.get("updatedAt")), task.get("taskId", "")), reverse=True)[0]


def _select_latest(tasks: list[dict]) -> dict | None:
    if not tasks:
        return None
    return sorted(tasks, key=lambda task: (_sort_rank(task.get("updatedAt")), task.get("taskId", "")), reverse=True)[0]


def _sort_rank(text: object) -> float:
    value = str(text or "").strip()
    if not value:
        return float("-inf")
    try:
        return datetime.fromisoformat(value).timestamp()
    except ValueError:
        return float("-inf")
