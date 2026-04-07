import json
import subprocess
import sys
from pathlib import Path

from runtime.close_runtime import apply_close_update
from runtime.decomposition.models import LeafBundle
from runtime.decomposition.promotion import promote_leaf_bundle
from runtime.progress_runtime import apply_progress_update


ROOT = Path(__file__).resolve().parents[2]


def test_ingest_decomposed_leaf_creates_flow_record(tmp_path: Path):
    promotion = promote_leaf_bundle(
        LeafBundle(
            taskId="leaf-flow-1",
            parentTaskId="task-parent",
            goal="bind first leaf into canonical flow",
            allowedPaths=["runtime/"],
            doneWhen=["final-result recorded", "no-test-required"],
            requiredEvidence=["final-result"],
            requiredTests=[],
            status="draft",
            priority="P0",
            estimatedTurns=2,
            estimatedMinutes=8,
            splitConfidence=0.9,
        )
    )
    assert promotion.promoted is True
    leaf = promotion.leaf

    payload_file = tmp_path / "leaf-flow-1.json"
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
    flow_path = tmp_path / ".agent" / "state" / "flows" / "task-parent.json"
    assert flow_path.exists()

    flow = json.loads(flow_path.read_text(encoding="utf-8"))
    assert flow["taskFlowId"] == "task-parent"
    assert flow["currentLeafTaskId"] == "leaf-flow-1"
    assert flow["status"] == "active"


def test_progress_and_close_recompute_flow_state(tmp_path: Path):
    changed_file = tmp_path / "runtime" / "flow" / "store.py"
    changed_file.parent.mkdir(parents=True, exist_ok=True)
    changed_file.write_text("flow store evidence\n", encoding="utf-8")
    (tmp_path / "tests").mkdir(parents=True, exist_ok=True)
    task_path = tmp_path / ".agent" / "state" / "tasks" / "leaf-flow-2.json"
    task_path.parent.mkdir(parents=True, exist_ok=True)
    task_path.write_text(
        json.dumps(
                {
                    "taskId": "leaf-flow-2",
                    "project": "wlcc",
                    "goal": "close current flow leaf",
                    "status": "ready",
                    "priority": "P0",
                    "dependencies": [],
                    "override": "none",
                    "latestResult": "ready leaf prepared for flow close",
                    "nextStep": "move into verify",
                    "lastSuccess": "ingest complete",
                    "lastFailure": "无",
                    "lifecycle": "ready",
                    "kind": "real",
                    "taskLevel": "leaf",
                "taskFlowId": "task-parent",
                "phase": "implement",
                "doneWhen": ["final-result recorded", "gap-check recorded", "status-update recorded"],
                "requiredEvidence": ["final-result", "gap-check", "status-update"],
                "requiredTests": [],
                "allowedPaths": ["runtime/"],
                "updatedAt": "2026-04-07T13:00:00",
                "turnCount": 0,
                "maxTurns": 8,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    supervision_path = tmp_path / ".agent" / "state" / "supervision" / "leaf-flow-2.json"
    supervision_path.parent.mkdir(parents=True, exist_ok=True)
    supervision_path.write_text(
        json.dumps(
            {
                "taskId": "leaf-flow-2",
                "status": "ready",
                "lastEvidenceCount": 0,
                "lastTestsCount": 0,
                "lastPhase": "implement",
                "lastTurnCount": 0,
                "weakProgressCount": 0,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    heartbeat_path = tmp_path / ".agent" / "heartbeat" / "flow.json"
    heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
    heartbeat_path.write_text(
        json.dumps(
            {
                "currentTask": "leaf-flow-2",
                "emittedAt": "2026-04-07T13:00:00",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    flow_path = tmp_path / ".agent" / "state" / "flows" / "task-parent.json"
    flow_path.parent.mkdir(parents=True, exist_ok=True)
    flow_path.write_text(
        json.dumps(
            {
                "taskFlowId": "task-parent",
                "ownerSessionId": "",
                "entryMode": "wlcc-live",
                "goal": "close current flow leaf",
                "status": "draft",
                "currentLeafTaskId": None,
                "closedLeafCount": 0,
                "openLeafCount": 0,
                "lastClosureTaskId": None,
                "lastStatusUpdateAt": "",
                "replyMode": "restricted",
                "createdAt": "2026-04-07T13:00:00",
                "updatedAt": "2026-04-07T13:00:00",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    progressed = apply_progress_update(
        tmp_path,
        "leaf-flow-2",
        latest_result="runtime/flow/store.py now has final-result, gap-check, and status-update evidence",
        next_step="close the current leaf",
        blocker="无",
        phase="verify",
        turn_delta=1,
        changed_files=["runtime/flow/store.py"],
        tests_run=[],
        evidence_ids=["final-result", "gap-check", "status-update"],
        status="verify",
    )

    flow_after_progress = json.loads(flow_path.read_text(encoding="utf-8"))
    assert progressed["task"]["taskFlowId"] == "task-parent"
    assert flow_after_progress["currentLeafTaskId"] == "leaf-flow-2"
    assert flow_after_progress["status"] == "active"

    closed = apply_close_update(tmp_path, "leaf-flow-2", final_result="leaf closed with full flow evidence")

    flow_after_close = json.loads(flow_path.read_text(encoding="utf-8"))
    assert closed["task"]["finalReplyEligible"] is True
    assert flow_after_close["closedLeafCount"] == 1
    assert flow_after_close["openLeafCount"] == 0
    assert flow_after_close["lastClosureTaskId"] == "leaf-flow-2"
    assert flow_after_close["status"] == "completed"
