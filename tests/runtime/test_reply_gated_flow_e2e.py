import json
import subprocess
import sys
from pathlib import Path

from runtime.reply.presenter import present_reply
from runtime.sidecar.tasks_view import check_state_view_consistency, render_state_views_for_root


ROOT = Path(__file__).resolve().parents[2]


def test_render_state_views_writes_flow_markdown_summary(tmp_path: Path):
    tasks_dir = tmp_path / ".agent" / "state" / "tasks"
    flows_dir = tmp_path / ".agent" / "state" / "flows"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    flows_dir.mkdir(parents=True, exist_ok=True)

    (tasks_dir / "leaf-1.json").write_text(
        json.dumps(
            {
                "taskId": "leaf-1",
                "project": "wlcc",
                "goal": "render a flow summary",
                "status": "verify",
                "priority": "P0",
                "dependencies": [],
                "override": "none",
                "latestResult": "verify status recorded",
                "blocker": "无",
                "nextStep": "close the current leaf",
                "lastSuccess": "progress recorded",
                "lastFailure": "无",
                "updatedAt": "2026-04-07T14:00:00",
                "taskLevel": "leaf",
                "taskFlowId": "flow-1",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (flows_dir / "flow-1.json").write_text(
        json.dumps(
            {
                "taskFlowId": "flow-1",
                "ownerSessionId": "session-123",
                "entryMode": "wlcc-live",
                "goal": "render a flow summary",
                "status": "active",
                "currentLeafTaskId": "leaf-1",
                "closedLeafCount": 0,
                "openLeafCount": 1,
                "lastClosureTaskId": None,
                "lastStatusUpdateAt": "2026-04-07T14:00:00",
                "replyMode": "restricted",
                "createdAt": "2026-04-07T14:00:00",
                "updatedAt": "2026-04-07T14:00:00",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    render_state_views_for_root(tmp_path)

    flow_md = tmp_path / ".agent" / "flows" / "flow-1.md"
    assert flow_md.exists()
    text = flow_md.read_text(encoding="utf-8")
    assert "- taskFlowId: flow-1" in text
    assert "- status: active" in text
    assert "- currentLeafTaskId: leaf-1" in text


def test_render_state_views_for_single_task_refreshes_flow_sidecar_and_consistency(tmp_path: Path):
    tasks_dir = tmp_path / ".agent" / "state" / "tasks"
    flows_dir = tmp_path / ".agent" / "state" / "flows"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    flows_dir.mkdir(parents=True, exist_ok=True)

    (tasks_dir / "leaf-1.json").write_text(
        json.dumps(
            {
                "taskId": "leaf-1",
                "project": "wlcc",
                "goal": "refresh one flow summary",
                "status": "running",
                "priority": "P0",
                "dependencies": [],
                "override": "none",
                "latestResult": "running status recorded",
                "blocker": "无",
                "nextStep": "keep running",
                "lastSuccess": "ingest complete",
                "lastFailure": "无",
                "updatedAt": "2026-04-07T14:10:00",
                "taskLevel": "leaf",
                "taskFlowId": "flow-1",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (flows_dir / "flow-1.json").write_text(
        json.dumps(
            {
                "taskFlowId": "flow-1",
                "ownerSessionId": "session-123",
                "entryMode": "wlcc-live",
                "goal": "refresh one flow summary",
                "status": "active",
                "currentLeafTaskId": "leaf-1",
                "closedLeafCount": 0,
                "openLeafCount": 1,
                "lastClosureTaskId": None,
                "lastStatusUpdateAt": "2026-04-07T14:10:00",
                "replyMode": "restricted",
                "createdAt": "2026-04-07T14:10:00",
                "updatedAt": "2026-04-07T14:10:00",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    render_state_views_for_root(tmp_path, "leaf-1")

    flow_md = tmp_path / ".agent" / "flows" / "flow-1.md"
    assert flow_md.exists()
    issues, _ = check_state_view_consistency(tmp_path)
    assert issues == []


def test_check_reply_exit_cli_prints_structured_verdict_json(tmp_path: Path):
    tasks_dir = tmp_path / ".agent" / "state" / "tasks"
    flows_dir = tmp_path / ".agent" / "state" / "flows"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    flows_dir.mkdir(parents=True, exist_ok=True)

    (tasks_dir / "leaf-1.json").write_text(
        json.dumps(
            {
                "taskId": "leaf-1",
                "project": "wlcc",
                "goal": "check reply exit",
                "status": "verify",
                "lifecycle": "verify",
                "kind": "real",
                "taskLevel": "leaf",
                "taskFlowId": "flow-1",
                "evidenceIds": ["final-result"],
                "updatedAt": "2026-04-07T14:00:00",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (flows_dir / "flow-1.json").write_text(
        json.dumps(
            {
                "taskFlowId": "flow-1",
                "ownerSessionId": "session-123",
                "entryMode": "wlcc-live",
                "goal": "check reply exit",
                "status": "active",
                "currentLeafTaskId": "leaf-1",
                "closedLeafCount": 0,
                "openLeafCount": 1,
                "lastClosureTaskId": None,
                "lastStatusUpdateAt": "2026-04-07T14:00:00",
                "replyMode": "restricted",
                "createdAt": "2026-04-07T14:00:00",
                "updatedAt": "2026-04-07T14:00:00",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check_reply_exit.py"),
            "--project-root",
            str(tmp_path),
            "--task-id",
            "leaf-1",
            "--reply-kind",
            "status",
            "--structured",
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    payload = json.loads(completed.stdout)
    assert payload["decision"] == "allow-status-reply"
    assert payload["allowed"] is True


def test_present_reply_for_blocked_flow_returns_unblock_request():
    task = {
        "taskId": "leaf-blocked",
        "goal": "wait for a missing secret",
        "status": "blocked",
        "blocker": "missing production API token",
        "nextStep": "ask for the token explicitly",
    }
    flow = {
        "taskFlowId": "flow-1",
        "status": "blocked",
        "currentLeafTaskId": "leaf-blocked",
    }
    verdict = {
        "allowed": True,
        "decision": "allow-blocked-reply",
        "reason": "ok",
    }

    presented = present_reply(task=task, flow=flow, verdict=verdict)

    assert presented["mode"] == "blocked"
    assert "missing production API token" in presented["text"]
    assert "ask for the token explicitly" in presented["text"]
