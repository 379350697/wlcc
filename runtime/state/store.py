import json
from pathlib import Path

from runtime.common.io import read_json, write_json
from runtime.common.models import TaskState
from runtime.contracts.task_contract import normalize_contract_dict, validate_contract_dict
from runtime.common.paths import RuntimePaths


ALLOWED_STATUS = {
    "todo",
    "doing",
    "blocked",
    "done",
    "draft",
    "ready",
    "running",
    "verify",
    "closed",
    "waiting-human",
}
ALLOWED_PRIORITY = {"P0", "P1", "P2", "P3"}
ALLOWED_OVERRIDE = {"none", "force-run", "force-hold"}


def validate_task_state(task: TaskState) -> None:
    if task.status not in ALLOWED_STATUS:
        raise SystemExit(f"invalid status: {task.status}")
    if task.priority not in ALLOWED_PRIORITY:
        raise SystemExit(f"invalid priority: {task.priority}")
    if task.override not in ALLOWED_OVERRIDE:
        raise SystemExit(f"invalid override: {task.override}")
    if task.kind == "real":
        verdict = validate_contract_dict(task.to_dict())
        if not verdict.passed:
            raise SystemExit(f"invalid task contract: {verdict.reason}")


def task_state_path(paths: RuntimePaths, task_id: str) -> Path:
    return paths.tasks_state_dir / f"{task_id}.json"


def candidate_task_ids(task_id: str) -> list[str]:
    candidates = [task_id]
    if not task_id.startswith("real-"):
        candidates.append(f"real-{task_id}")
    return candidates


def resolve_task_id(paths: RuntimePaths, task_id: str) -> str:
    for candidate in candidate_task_ids(task_id):
        if task_state_path(paths, candidate).exists():
            return candidate
    raise SystemExit(f"missing task: {task_id}")


def write_task_state(paths: RuntimePaths, task: TaskState) -> tuple[Path, Path]:
    validate_task_state(task)

    task_path = task_state_path(paths, task.taskId)
    write_json(task_path, task.to_dict())

    index_path = paths.index_path
    try:
        index = read_json(index_path, None)
    except json.JSONDecodeError:
        index = None
    if not isinstance(index, dict) or not isinstance(index.get("tasks"), list):
        index = {"tasks": [], "updatedAt": task.updatedAt}

    if task.taskId not in index["tasks"]:
        index["tasks"].append(task.taskId)
    index["tasks"] = sorted(index["tasks"])
    index["updatedAt"] = task.updatedAt
    write_json(index_path, index)
    return task_path, index_path


def load_task_state(paths: RuntimePaths, task_id: str) -> dict:
    task_path = task_state_path(paths, resolve_task_id(paths, task_id))
    task = read_json(task_path, None)
    if task is None:
        raise SystemExit(f"missing task: {task_id}")
    task.update(normalize_contract_dict(task))
    return task
