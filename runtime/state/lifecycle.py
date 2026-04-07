import json
from datetime import datetime
from pathlib import Path

from runtime.common.io import read_json, write_json
from runtime.common.time import now_iso
from runtime.common.paths import RuntimePaths
from runtime.state.store import load_task_state, resolve_task_id


MECHANIZED = {"draft", "ready", "running", "verify", "closed"}


ALLOWED = {
    "new",
    "ingested",
    "active",
    "blocked",
    "waiting-human",
    "handoff",
    "done",
    "archived",
    "legacy",
    "draft",
    "ready",
    "running",
    "verify",
    "closed",
}
TRANSITIONS = {
    "new": {"ingested"},
    "ingested": {"active", "ready", "blocked", "waiting-human", "handoff"},
    "active": {"blocked", "waiting-human", "handoff", "done"},
    "blocked": {"active", "waiting-human", "handoff"},
    "waiting-human": {"active", "handoff", "done"},
    "handoff": {"active", "waiting-human", "done"},
    "done": {"archived"},
    "archived": set(),
    "legacy": {"ingested", "active", "blocked", "waiting-human", "handoff", "done"},
    "draft": {"ready", "blocked", "waiting-human"},
    "ready": {"running", "blocked", "waiting-human", "handoff"},
    "running": {"verify", "blocked", "waiting-human", "handoff", "closed"},
    "verify": {"running", "blocked", "waiting-human", "handoff", "closed"},
    "closed": {"archived"},
}
SUPERVISION_MAP = {
    "new": "new",
    "ingested": "ingested",
    "active": "active",
    "blocked": "blocked",
    "waiting-human": "waiting-human",
    "handoff": "handoff",
    "done": "done",
    "archived": "archived",
    "legacy": "legacy",
    "draft": "ingested",
    "ready": "ready",
    "running": "active",
    "verify": "active",
    "closed": "done",
}
DELIVERY_REQUIRED_TARGETS = {"done", "handoff", "closed"}


EMPTY_PHRASES = frozenset({
    "已完成", "完成", "推进中", "继续", "进行中", "正在处理",
    "done", "completed", "in progress", "continue", "ok", "wip",
})


def _check_not_empty_phrase(latest_result: str) -> dict | None:
    normalized = latest_result.strip().lower()
    if normalized in EMPTY_PHRASES or len(normalized) < 5:
        return None
    return {"type": "content", "detail": "latest_result is substantive"}


def _check_file_exists(latest_result: str, project_root: Path) -> dict | None:
    candidate = project_root / latest_result.strip()
    if candidate.exists() and candidate.is_file():
        return {"type": "file-exists", "path": str(candidate.relative_to(project_root))}

    for token in latest_result.split():
        token = token.strip('`"\'()[]{}')
        if not token or token.startswith("-"):
            continue
        candidate = project_root / token
        if candidate.exists() and candidate.is_file():
            return {"type": "file-exists", "path": str(candidate.relative_to(project_root))}
    return None


def _check_heartbeat_fresh(task_id: str, project_root: Path) -> dict | None:
    hb_dir = project_root / ".agent" / "heartbeat"
    if not hb_dir.exists():
        return None
    hb_files = sorted(hb_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not hb_files:
        return None
    try:
        hb = json.loads(hb_files[0].read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if isinstance(hb, list):
        hb = next(
            (item for item in reversed(hb) if isinstance(item, dict) and item.get("currentTask") == task_id),
            None,
        )
    if not isinstance(hb, dict):
        return None
    if hb.get("currentTask") != task_id:
        return None
    timestamp_str = hb.get("emittedAt") or hb.get("timestamp") or ""
    if not timestamp_str:
        return None
    try:
        hb_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        age_seconds = (datetime.now(hb_time.tzinfo) - hb_time).total_seconds()
    except (ValueError, TypeError):
        age_seconds = (datetime.now().timestamp() - hb_files[0].stat().st_mtime)
    if age_seconds <= 300:
        return {"type": "heartbeat-fresh", "age_seconds": round(age_seconds)}
    return None


def _check_files_changed(task_id: str, project_root: Path) -> dict | None:
    task_path = project_root / ".agent" / "state" / "tasks" / f"{task_id}.json"
    if not task_path.exists():
        return None
    baseline = task_path.stat().st_mtime
    scan_dirs = [
        project_root / ".agent" / "state",
        project_root / ".agent" / "tasks",
        project_root / ".agent" / "resume",
        project_root / "tests",
    ]
    changed_count = 0
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for f in scan_dir.rglob("*"):
            if f.is_file() and f.stat().st_mtime > baseline:
                changed_count += 1
                if changed_count >= 3:
                    break
        if changed_count >= 3:
            break
    if changed_count > 0:
        return {"type": "file-changes", "count": changed_count}
    return None


def _evaluate_delivery_gate(task_id: str, latest_result: str, project_root: Path, task_kind: str) -> dict:
    min_evidence = 2 if task_kind == "real" else 1
    collectors = [
        _check_not_empty_phrase(latest_result),
        _check_file_exists(latest_result, project_root),
        _check_heartbeat_fresh(task_id, project_root),
        _check_files_changed(task_id, project_root),
    ]
    evidence = [item for item in collectors if item is not None]
    passed = len(evidence) >= min_evidence
    return {
        "passed": passed,
        "reason": "ok" if passed else f"insufficient evidence: {len(evidence)}/{min_evidence}",
        "evidence": evidence,
        "required": min_evidence,
        "collected": len(evidence),
    }


def transition_lifecycle(paths: RuntimePaths, task_id: str, target: str) -> tuple[dict, dict, str]:
    if target not in ALLOWED:
        raise SystemExit(f"invalid lifecycle target: {target}")

    resolved_task_id = resolve_task_id(paths, task_id)
    task = load_task_state(paths, resolved_task_id)
    current = task.get("lifecycle", "legacy")
    if target not in TRANSITIONS.get(current, set()):
        raise SystemExit(f"illegal lifecycle transition: {current} -> {target}")

    if target in DELIVERY_REQUIRED_TARGETS:
        task_kind = task.get("kind", "sample")
        result = _evaluate_delivery_gate(task_id, task.get("latestResult", ""), paths.root, task_kind)
        if not result["passed"]:
            raise SystemExit(result["reason"])

    task["lifecycle"] = target
    if target in MECHANIZED | {"blocked", "waiting-human"}:
        task["status"] = target
    elif target == "done" and str(task.get("status", "")).strip() != "closed":
        task["status"] = "done"
    task["supervisionState"] = SUPERVISION_MAP[target]
    if target in {"closed", "archived"}:
        task["eligibleForScheduling"] = False
        if target == "archived":
            task["isPrimaryTrack"] = False
    elif target in {"ingested", "active", "ready", "running", "verify", "blocked", "waiting-human", "handoff"} and task.get("kind") == "real":
        task["eligibleForScheduling"] = target in {"ingested", "active", "blocked", "waiting-human", "handoff"}
        if target in {"ready", "running", "verify"}:
            task["eligibleForScheduling"] = True
    task["updatedAt"] = now_iso()
    task_path = paths.tasks_state_dir / f"{resolved_task_id}.json"
    write_json(task_path, task)

    supervision_path = paths.supervision_state_dir / f"{resolved_task_id}.json"
    supervision = read_json(supervision_path, {"taskId": resolved_task_id})
    supervision["status"] = SUPERVISION_MAP[target]
    supervision["updatedAt"] = task["updatedAt"]
    supervision["stale"] = target in {"blocked", "waiting-human"}
    write_json(supervision_path, supervision)
    return task, supervision, current
