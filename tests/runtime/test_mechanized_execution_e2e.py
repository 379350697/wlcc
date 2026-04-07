import json
import subprocess
import sys
from pathlib import Path

import pytest

from runtime.close_runtime import apply_close_update
from runtime.decomposition.models import LeafBundle
from runtime.decomposition.promotion import promote_leaf_bundle
from runtime.progress_runtime import apply_progress_update


ROOT = Path(__file__).resolve().parents[2]


def _ingest_leaf(tmp_path: Path, leaf: LeafBundle) -> None:
    payload_file = tmp_path / f"{leaf.taskId}.json"
    payload_file.write_text(json.dumps(leaf.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "ingest_decomposed_leaf.py"),
            "--payload-file",
            str(payload_file),
            "--project-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout


def test_mechanized_execution_e2e_releases_next_leaf_only_after_closed(tmp_path: Path):
    first_draft = LeafBundle(
        taskId="leaf-1",
        parentTaskId="task-parent",
        goal="implement first bounded leaf",
        allowedPaths=["runtime/"],
        doneWhen=["final-result recorded", "gap-check recorded", "status-update recorded"],
        requiredEvidence=["final-result", "gap-check", "status-update"],
        requiredTests=["python3 -m pytest tests/runtime/test_mechanized_execution_e2e.py -q"],
        status="draft",
        priority="P0",
        estimatedTurns=3,
        estimatedMinutes=12,
        splitConfidence=0.95,
    )
    second_draft = LeafBundle(
        taskId="leaf-2",
        parentTaskId="task-parent",
        goal="implement second bounded leaf",
        allowedPaths=["runtime/"],
        doneWhen=["final-result recorded", "gap-check recorded", "status-update recorded"],
        requiredEvidence=["final-result", "gap-check", "status-update"],
        requiredTests=["python3 -m pytest tests/runtime/test_mechanized_execution_e2e.py -q"],
        status="draft",
        priority="P1",
        estimatedTurns=2,
        estimatedMinutes=10,
        splitConfidence=0.9,
    )

    first_ready = promote_leaf_bundle(first_draft)
    second_ready = promote_leaf_bundle(second_draft)
    assert first_ready.promoted is True
    assert second_ready.promoted is True

    _ingest_leaf(tmp_path, first_ready.leaf)
    _ingest_leaf(tmp_path, second_ready.leaf)

    with pytest.raises(SystemExit, match="completion gate"):
        apply_close_update(tmp_path, "leaf-1", final_result="should fail before closure artifacts")

    apply_progress_update(
        tmp_path,
        "leaf-1",
        latest_result="leaf-1 now has final-result, gap-check, status-update, and test evidence",
        next_step="run close on the current leaf",
        blocker="无",
        phase="verify",
        turn_delta=1,
        changed_files=["runtime/decomposition/models.py"],
        tests_run=["python3 -m pytest tests/runtime/test_mechanized_execution_e2e.py -q"],
        evidence_ids=["final-result", "gap-check", "status-update"],
        status="running",
    )

    closed = apply_close_update(tmp_path, "leaf-1", final_result="leaf-1 closed with mechanized evidence")

    assert closed["task"]["lifecycle"] == "archived"
    assert closed["task"]["eligibleForScheduling"] is False

    next_task_path = tmp_path / ".agent" / "state" / "next-task.json"
    next_task = json.loads(next_task_path.read_text(encoding="utf-8"))
    assert next_task["nextTaskId"] == "leaf-2"
    assert next_task["decisionType"] == "switch-next"
