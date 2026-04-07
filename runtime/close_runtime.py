from __future__ import annotations

from pathlib import Path

from runtime.common.io import read_json, write_json
from runtime.common.paths import RuntimePaths
from runtime.common.time import now_iso
from runtime.contracts.task_contract import normalize_contract_dict
from runtime.gates.completion import evaluate_completion_gate
from runtime.scheduling.next_task import build_next_task_from_state_dir, write_state_views
from runtime.state.lifecycle import transition_lifecycle
from runtime.state.store import resolve_task_id
from runtime.supervision.core import handle_supervision_trigger


def apply_close_update(root: Path, task_id: str, *, final_result: str) -> dict:
    paths = RuntimePaths(root)
    resolved_task_id = resolve_task_id(paths, task_id)
    task_path = paths.tasks_state_dir / f"{resolved_task_id}.json"
    task = read_json(task_path, None)
    if task is None:
        raise SystemExit(f"missing task: {task_id}")
    task.update(normalize_contract_dict(task))
    if task.get("kind") != "real":
        raise SystemExit("close_task_runtime only supports kind=real")
    if task.get("taskLevel") != "leaf":
        raise SystemExit("close_task_runtime only supports taskLevel=leaf")

    completion_result = evaluate_completion_gate(
        task,
        {
            "evidenceIds": task.get("evidenceIds", []),
            "testsRun": task.get("testsRun", []),
            "changedFiles": task.get("changedFiles", []),
        },
    )
    if not completion_result["passed"]:
        raise SystemExit(f"[completion gate] rejected: {completion_result['reason']}")

    task["latestResult"] = final_result
    task["status"] = "closed"
    task["blocker"] = "无"
    task["nextStep"] = "archive"
    task["phase"] = "done"
    task["updatedAt"] = now_iso()
    write_json(task_path, task)

    handle_supervision_trigger(root, resolved_task_id, "on_completion")
    transition_lifecycle(paths, resolved_task_id, "closed")
    updated_task, _, _ = transition_lifecycle(paths, resolved_task_id, "archived")
    build_next_task_from_state_dir(
        paths.tasks_state_dir,
        paths.state_dir / "next-task.json",
        paths.agent_dir / "NEXT_TASK.md",
        paths.state_dir / "next-task-input.json",
    )
    write_state_views(paths.tasks_state_dir, paths.agent_dir / "tasks", paths.agent_dir / "resume", root / "TASKS.md")

    closure_note = root / ".agent" / "logs" / "CLOSURE_NOTE.md"
    closure_note.parent.mkdir(parents=True, exist_ok=True)
    with closure_note.open("a", encoding="utf-8") as handle:
        handle.write(f"- {now_iso()} | task={resolved_task_id} | finalResult={final_result}\n")

    return {
        "taskId": resolved_task_id,
        "task": updated_task,
        "completionResult": completion_result,
    }
