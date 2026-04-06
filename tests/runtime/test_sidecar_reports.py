import json
from pathlib import Path

from runtime.common.io import write_json
from runtime.sidecar.reports import (
    build_heartbeat_summary,
    check_state_view_consistency,
    render_state_views_for_root,
    write_retrieve_context_output,
)


def make_task(root: Path, task_id: str = "demo-task") -> None:
    write_json(
        root / ".agent" / "state" / "tasks" / f"{task_id}.json",
        {
            "taskId": task_id,
            "project": "demo",
            "goal": "finish demo task",
            "status": "doing",
            "priority": "P1",
            "dependencies": [],
            "override": "none",
            "latestResult": "implemented runtime refactor",
            "blocker": "none",
            "nextStep": "verify outputs",
            "updatedAt": "2026-04-06T10:00:00",
            "lastSuccess": "refactor core path",
            "lastFailure": "none",
        },
    )


def test_write_retrieve_context_output_writes_json(tmp_path: Path):
    (tmp_path / "README.md").write_text("demo readme", encoding="utf-8")
    make_task(tmp_path)

    payload, output = write_retrieve_context_output(tmp_path, "demo-task")

    assert output.exists()
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["meta"]["taskKind"] == "unknown"
    assert payload["task_state"][0]["source"] == ".agent/state/tasks/demo-task.json"


def test_build_heartbeat_summary_supports_history_lists(tmp_path: Path):
    write_json(
        tmp_path / ".agent" / "heartbeat" / "heartbeat-history.json",
        [
            {
                "emittedAt": "2026-04-06T10:00:00+00:00",
                "stage": "active",
                "currentTask": "demo-task",
                "triggerReason": "periodic-step",
                "requiresHuman": False,
            },
            {
                "emittedAt": "2026-04-06T10:05:00+00:00",
                "stage": "handoff",
                "currentTask": "demo-task",
                "triggerReason": "stage-complete-stop",
                "requiresHuman": True,
            },
        ],
    )
    write_json(
        tmp_path / ".agent" / "heartbeat" / "latest-heartbeat.json",
        {"stage": "handoff", "currentTask": "demo-task", "triggerReason": "stage-complete-stop"},
    )

    summary, outputs = build_heartbeat_summary(tmp_path)

    assert summary["historyCount"] == 2
    assert summary["requiresHumanCount"] == 1
    assert summary["anomalyHeartbeats"][0]["triggerReason"] == "stage-complete-stop"
    assert all(path.exists() for path in outputs)


def test_render_and_check_state_views_round_trip(tmp_path: Path):
    make_task(tmp_path)

    render_state_views_for_root(tmp_path)
    issues, report = check_state_view_consistency(tmp_path)

    assert issues == []
    assert report.exists()
