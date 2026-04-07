from __future__ import annotations

from pathlib import Path

from runtime.common.io import read_json, write_json
from runtime.common.paths import RuntimePaths
from runtime.common.time import now_iso
from runtime.contracts.task_contract import normalize_contract_dict
from runtime.evidence.ledger import record_progress_entries
from runtime.flow.store import ensure_task_flow, recompute_flow
from runtime.gates.delivery import evaluate_delivery_gate
from runtime.gates.progress import evaluate_progress_gate
from runtime.state.store import resolve_task_id
from runtime.supervision.core import judge_progress


MECHANIZED_LIFECYCLE_STATUSES = {"draft", "ready", "running", "verify", "closed", "blocked", "waiting-human"}


def _derive_lifecycle(candidate: dict, requested_status: str | None, requested_phase: str | None) -> str:
    status = str(requested_status or "").strip()
    phase = str(requested_phase or candidate.get("phase", "") or "").strip()
    current = str(candidate.get("lifecycle", "legacy") or "legacy").strip()

    if status in MECHANIZED_LIFECYCLE_STATUSES:
        return status
    if phase == "verify" and current in MECHANIZED_LIFECYCLE_STATUSES | {"active", "ingested", "legacy"}:
        return "verify"
    if phase in {"analyze", "plan", "implement"} and current == "ready":
        return "running"
    return current


def apply_progress_update(
    root: Path,
    task_id: str,
    *,
    latest_result: str,
    next_step: str,
    blocker: str,
    phase: str | None,
    turn_delta: int,
    changed_files: list[str],
    tests_run: list[str],
    evidence_ids: list[str],
    status: str | None,
) -> dict:
    paths = RuntimePaths(root)
    resolved_task_id = resolve_task_id(paths, task_id)
    task_path = paths.tasks_state_dir / f"{resolved_task_id}.json"
    supervision_path = paths.supervision_state_dir / f"{resolved_task_id}.json"
    task = read_json(task_path, None)
    if task is None:
        raise SystemExit(f"missing task: {task_id}")
    task.update(normalize_contract_dict(task))

    if turn_delta < 0:
        raise SystemExit("[progress runtime] rejected: turn-delta must be non-negative")
    if not changed_files and not tests_run and not evidence_ids:
        raise SystemExit("[progress runtime] rejected: at least one changed-file, test-run, or evidence-id is required")

    delivery_result = evaluate_delivery_gate(resolved_task_id, latest_result, root, task.get("kind", "sample"))
    if not delivery_result["passed"]:
        raise SystemExit(f"[delivery gate] rejected: {delivery_result['reason']}")

    progress_result = evaluate_progress_gate(latest_result, next_step)
    if not progress_result["passed"]:
        raise SystemExit(f"[progress reply gate] rejected: {progress_result['reason']}")

    candidate = dict(task)
    candidate["latestResult"] = latest_result
    candidate["nextStep"] = next_step
    candidate["blocker"] = blocker
    candidate["updatedAt"] = now_iso()
    candidate["phase"] = phase or candidate.get("phase", "analyze")
    candidate["turnCount"] = int(candidate.get("turnCount", 0)) + turn_delta
    if candidate["turnCount"] > int(candidate.get("maxTurns", 8)):
        raise SystemExit(f"[progress runtime] rejected: turn budget exceeded ({candidate['turnCount']}/{candidate.get('maxTurns', 8)})")
    candidate["changedFiles"] = list(changed_files)
    candidate["testsRun"] = list(tests_run)
    candidate["evidenceIds"] = list(evidence_ids)
    candidate["finalReplyEligible"] = False
    if status:
        candidate["status"] = status
    candidate["lifecycle"] = _derive_lifecycle(candidate, status, phase)
    if not status and candidate["lifecycle"] in {"running", "verify", "blocked", "waiting-human", "closed"}:
        candidate["status"] = candidate["lifecycle"]
    if candidate["lifecycle"] in {"ready", "running", "verify", "blocked", "waiting-human"}:
        candidate["eligibleForScheduling"] = candidate["lifecycle"] != "draft"
    elif candidate["lifecycle"] == "closed":
        candidate["eligibleForScheduling"] = False

    supervision = read_json(supervision_path, {"taskId": resolved_task_id})
    precheck = judge_progress(candidate, root, supervision)
    if not precheck["allowed"]:
        raise SystemExit(f"supervisor precheck rejected: {precheck['reason']}")

    write_json(task_path, candidate)
    if candidate.get("taskFlowId"):
        ensure_task_flow(paths, candidate)
        recompute_flow(paths, str(candidate["taskFlowId"]))
    record_progress_entries(
        root,
        resolved_task_id,
        latest_result=latest_result,
        next_step=next_step,
        changed_files=changed_files,
        tests_run=tests_run,
        evidence_ids=evidence_ids,
        phase=str(candidate.get("phase", "analyze")),
        status=str(candidate.get("status", "")),
        lifecycle=str(candidate.get("lifecycle", "legacy")),
        turn_count=int(candidate.get("turnCount", 0) or 0),
    )
    return {
        "task": candidate,
        "taskId": resolved_task_id,
        "deliveryResult": delivery_result,
        "progressResult": progress_result,
        "precheck": precheck,
    }
