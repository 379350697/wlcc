from __future__ import annotations

from runtime.gates.closure_artifacts import evaluate_closure_artifacts


OPEN_LEAF_STATUSES = {"ready", "running", "verify", "doing"}
BLOCKED_STATUSES = {"blocked", "waiting-human"}
CLOSED_TASK_STATUSES = {"closed", "done"}
CLOSED_LIFECYCLES = {"closed", "archived"}


def _text(value: object) -> str:
    return str(value or "").strip()


def _is_structured(payload: dict) -> bool:
    return bool(payload.get("structured"))


def _has_closure_truth(task: dict) -> bool:
    closure_result = evaluate_closure_artifacts(
        task,
        {"evidenceIds": task.get("evidenceIds", [])},
    )
    return closure_result["passed"]


def _is_closed(task: dict) -> bool:
    status = _text(task.get("status"))
    lifecycle = _text(task.get("lifecycle"))
    return status in CLOSED_TASK_STATUSES or lifecycle in CLOSED_LIFECYCLES


def _is_final_reply_allowed(task: dict) -> bool:
    if not _is_closed(task):
        return False
    return _has_closure_truth(task)


def evaluate_reply_exit_gate(*, task: dict | None, flow: dict | None, payload: dict | None) -> dict:
    payload = dict(payload or {})
    task = dict(task or {})
    flow = dict(flow or {})

    reply_kind = _text(payload.get("replyKind")).lower() or "final"
    task_status = _text(task.get("status"))
    lifecycle = _text(task.get("lifecycle"))
    flow_status = _text(flow.get("status"))

    if not task:
        return {
            "allowed": False,
            "decision": "reject-open-leaf",
            "reason": "missing active leaf truth",
            "taskId": None,
            "taskStatus": "",
            "flowStatus": flow_status,
        }

    if reply_kind == "final":
        allowed = _is_final_reply_allowed(task)
        return {
            "allowed": allowed,
            "decision": "allow-final-reply" if allowed else "reject-open-leaf",
            "reason": "ok" if allowed else "open leaf cannot emit final reply",
            "taskId": task.get("taskId"),
            "taskStatus": task_status or lifecycle,
            "flowStatus": flow_status,
        }

    if reply_kind == "blocked":
        blocker = _text(task.get("blocker"))
        requested_input = _text(payload.get("requestedInput"))
        allowed = (
            _is_structured(payload)
            and (task_status in BLOCKED_STATUSES or lifecycle in BLOCKED_STATUSES or flow_status in BLOCKED_STATUSES)
            and bool(blocker)
            and len(requested_input) >= 10
        )
        return {
            "allowed": allowed,
            "decision": "allow-blocked-reply" if allowed else "reject-open-leaf",
            "reason": "ok" if allowed else "blocked reply requires structured blocker truth",
            "taskId": task.get("taskId"),
            "taskStatus": task_status or lifecycle,
            "flowStatus": flow_status,
        }

    if reply_kind == "status":
        allowed = _is_structured(payload) and (
            task_status in OPEN_LEAF_STATUSES
            or lifecycle in OPEN_LEAF_STATUSES
            or flow_status == "active"
        )
        return {
            "allowed": allowed,
            "decision": "allow-status-reply" if allowed else "reject-open-leaf",
            "reason": "ok" if allowed else "open leaf status replies must be structured",
            "taskId": task.get("taskId"),
            "taskStatus": task_status or lifecycle,
            "flowStatus": flow_status,
        }

    return {
        "allowed": False,
        "decision": "reject-open-leaf",
        "reason": f"unsupported reply kind: {reply_kind}",
        "taskId": task.get("taskId"),
        "taskStatus": task_status or lifecycle,
        "flowStatus": flow_status,
    }
