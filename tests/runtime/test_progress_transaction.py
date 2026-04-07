import json
from pathlib import Path

import pytest

from runtime.evidence.ledger import load_evidence_entries
from runtime.progress_runtime import apply_progress_update
from runtime.supervision.core import save_json


def test_apply_progress_update_does_not_persist_when_preflight_rejects(tmp_path: Path):
    task_id = "txn-task"
    task_path = tmp_path / ".agent" / "state" / "tasks" / f"{task_id}.json"
    supervision_path = tmp_path / ".agent" / "state" / "supervision" / f"{task_id}.json"
    evidence_path = tmp_path / ".agent" / "state" / "evidence" / f"{task_id}.json"
    task_path.parent.mkdir(parents=True, exist_ok=True)

    save_json(
        task_path,
        {
            "taskId": task_id,
            "kind": "sample",
            "status": "running",
            "latestResult": "existing result",
            "nextStep": "existing next step",
            "blocker": "none",
            "phase": "implement",
            "turnCount": 1,
            "maxTurns": 8,
            "testsRun": [],
        },
    )
    save_json(
        supervision_path,
        {
            "taskId": task_id,
            "status": "active",
            "lastEvidenceCount": 2,
            "lastTestsCount": 0,
            "lastPhase": "implement",
            "lastTurnCount": 1,
            "weakProgressCount": 0,
        },
    )
    save_json(
        evidence_path,
        {
            "taskId": task_id,
            "version": 1,
            "updatedAt": "2026-04-07T10:00:00",
            "entries": [
                {
                    "evidenceType": "content",
                    "source": "delivery.evaluate_delivery_gate",
                    "summary": "latest_result is substantive",
                    "details": {"detail": "latest_result is substantive"},
                    "recordedAt": "2026-04-07T10:00:00",
                },
                {
                    "evidenceType": "delivery-verdict",
                    "source": "delivery.evaluate_delivery_gate",
                    "summary": "ok",
                    "details": {
                        "passed": True,
                        "required": 1,
                        "collected": 1,
                        "taskKind": "sample",
                    },
                    "recordedAt": "2026-04-07T10:00:00",
                },
            ],
        },
    )
    save_json(
        task_path,
        {
            "taskId": task_id,
            "kind": "sample",
            "status": "running",
            "latestResult": "existing result",
            "nextStep": "existing next step",
            "blocker": "none",
            "phase": "implement",
            "turnCount": 1,
            "maxTurns": 8,
            "testsRun": [],
        },
    )

    with pytest.raises(SystemExit, match="supervisor precheck rejected: weak-progress"):
        apply_progress_update(
            tmp_path,
            task_id,
            latest_result="existing result still looks substantive",
            next_step="continue the current leaf with no new evidence",
            blocker="none",
            phase="implement",
            turn_delta=1,
            changed_files=["runtime/progress_runtime.py"],
            tests_run=[],
            evidence_ids=[],
            status="running",
        )

    saved = json.loads(task_path.read_text(encoding="utf-8"))
    assert saved["latestResult"] == "existing result"
    assert saved["nextStep"] == "existing next step"
    assert saved["turnCount"] == 1


def test_apply_progress_update_records_progress_and_closure_artifacts_in_ledger(tmp_path: Path):
    task_id = "txn-task-ledger"
    task_path = tmp_path / ".agent" / "state" / "tasks" / f"{task_id}.json"
    supervision_path = tmp_path / ".agent" / "state" / "supervision" / f"{task_id}.json"
    task_path.parent.mkdir(parents=True, exist_ok=True)
    result_file = tmp_path / "tests" / "progress-result.md"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text("progress artifact\n", encoding="utf-8")

    save_json(
        task_path,
        {
            "taskId": task_id,
            "kind": "real",
            "taskLevel": "leaf",
            "status": "running",
            "lifecycle": "running",
            "latestResult": "existing result",
            "nextStep": "existing next step",
            "blocker": "none",
            "phase": "implement",
            "turnCount": 1,
            "maxTurns": 8,
            "testsRun": [],
            "allowedPaths": ["runtime/"],
            "doneWhen": ["final-result recorded", "gap-check recorded", "status-update recorded"],
            "requiredEvidence": ["final-result", "gap-check", "status-update"],
        },
    )
    save_json(
        supervision_path,
        {
            "taskId": task_id,
            "status": "active",
            "lastEvidenceCount": 0,
            "lastTestsCount": 0,
            "lastPhase": "implement",
            "lastTurnCount": 1,
            "weakProgressCount": 0,
        },
    )

    result = apply_progress_update(
        tmp_path,
        task_id,
        latest_result="tests/progress-result.md recorded concrete progress with final-result, gap-check, and status-update",
        next_step="move current leaf into verify",
        blocker="none",
        phase="verify",
        turn_delta=1,
        changed_files=["runtime/progress_runtime.py"],
        tests_run=["python3 -m pytest tests/runtime/test_progress_transaction.py -q"],
        evidence_ids=["final-result", "gap-check", "status-update"],
        status="verify",
    )

    task = result["task"]
    assert task["phase"] == "verify"
    assert task["status"] == "verify"

    progress_entries = load_evidence_entries(tmp_path, task_id, {"progress-update"})
    artifact_entries = load_evidence_entries(tmp_path, task_id, {"artifact-emitted"})
    test_entries = load_evidence_entries(tmp_path, task_id, {"test-run"})

    assert progress_entries
    assert artifact_entries
    assert {entry["details"]["artifactId"] for entry in artifact_entries} >= {"final-result", "gap-check", "status-update"}
    assert test_entries


def test_apply_progress_update_promotes_ready_leaf_to_running_when_status_omitted(tmp_path: Path):
    task_id = "txn-task-auto-running"
    task_path = tmp_path / ".agent" / "state" / "tasks" / f"{task_id}.json"
    supervision_path = tmp_path / ".agent" / "state" / "supervision" / f"{task_id}.json"
    task_path.parent.mkdir(parents=True, exist_ok=True)
    changed_file = tmp_path / "runtime" / "auto_running.py"
    changed_file.parent.mkdir(parents=True, exist_ok=True)
    changed_file.write_text("print('auto running')\n", encoding="utf-8")

    save_json(
        task_path,
        {
            "taskId": task_id,
            "kind": "real",
            "taskLevel": "leaf",
            "status": "ready",
            "lifecycle": "ready",
            "latestResult": "seed result",
            "nextStep": "start current leaf execution",
            "blocker": "none",
            "phase": "implement",
            "turnCount": 0,
            "maxTurns": 8,
            "testsRun": [],
            "allowedPaths": ["runtime/"],
            "doneWhen": ["final-result recorded"],
            "requiredEvidence": ["final-result"],
        },
    )
    save_json(
        supervision_path,
        {
            "taskId": task_id,
            "status": "ready",
            "lastEvidenceCount": 0,
            "lastTestsCount": 0,
            "lastPhase": "implement",
            "lastTurnCount": 0,
            "weakProgressCount": 0,
        },
    )

    result = apply_progress_update(
        tmp_path,
        task_id,
        latest_result="runtime/auto_running.py concrete progress recorded with evidence",
        next_step="continue implementing the current bounded leaf",
        blocker="none",
        phase="implement",
        turn_delta=1,
        changed_files=["runtime/auto_running.py"],
        tests_run=[],
        evidence_ids=["final-result"],
        status=None,
    )

    assert result["task"]["status"] == "running"
    assert result["task"]["lifecycle"] == "running"
