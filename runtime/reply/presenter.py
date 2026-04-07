from __future__ import annotations


def present_reply(*, task: dict, flow: dict | None, verdict: dict) -> dict:
    flow = dict(flow or {})
    decision = str(verdict.get("decision", "") or "")

    if decision == "allow-final-reply":
        return {
            "mode": "final",
            "text": "\n".join(
                [
                    f"taskFlowId: {flow.get('taskFlowId', task.get('taskFlowId', ''))}",
                    f"taskId: {task.get('taskId', '')}",
                    f"finalResult: {task.get('latestResult', '')}",
                ]
            ),
        }

    if decision == "allow-blocked-reply":
        return {
            "mode": "blocked",
            "text": "\n".join(
                [
                    f"taskFlowId: {flow.get('taskFlowId', task.get('taskFlowId', ''))}",
                    f"taskId: {task.get('taskId', '')}",
                    f"blocker: {task.get('blocker', 'unknown')}",
                    f"nextStep: {task.get('nextStep', '')}",
                ]
            ),
        }

    if decision == "allow-status-reply":
        return {
            "mode": "status",
            "text": "\n".join(
                [
                    f"taskFlowId: {flow.get('taskFlowId', task.get('taskFlowId', ''))}",
                    f"taskId: {task.get('taskId', '')}",
                    f"status: {task.get('status', task.get('lifecycle', 'unknown'))}",
                    f"nextStep: {task.get('nextStep', '')}",
                ]
            ),
        }

    return {
        "mode": "rejected",
        "text": verdict.get("reason", "reply rejected"),
    }
