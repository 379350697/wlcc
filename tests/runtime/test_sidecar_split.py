from pathlib import Path

from runtime.common.models import TaskState
from runtime.common.paths import RuntimePaths
from runtime.common.time import now_iso
from runtime.scheduling.next_task import build_next_task_from_state_dir
from runtime.sidecar.heartbeat_summary import build_heartbeat_summary
from runtime.sidecar.tasks_view import render_state_views_for_root
from runtime.state.store import write_task_state
from runtime.supervision.core import handle_supervision_trigger


def seed_real_task(root: Path, task_id: str = "real-sidecar-demo") -> RuntimePaths:
    paths = RuntimePaths(root)
    write_task_state(
        paths,
        TaskState(
            taskId=task_id,
            project="demo",
            goal="prove sidecar split",
            status="doing",
            priority="P1",
            latestResult="implemented runtime path",
            blocker="none",
            nextStep="verify sidecars later",
            lastSuccess="write core state",
            lastFailure="none",
            updatedAt=now_iso(),
            kind="real",
            source="test",
            executionMode="live",
            ownerContext="test",
            supervisionState="active",
            eligibleForScheduling=True,
            isPrimaryTrack=True,
            lifecycle="active",
            title=task_id,
        ),
    )
    return paths


def test_next_task_core_write_does_not_require_task_markdown_sidecars(tmp_path: Path):
    paths = seed_real_task(tmp_path)

    build_next_task_from_state_dir(
        paths.tasks_state_dir,
        paths.state_dir / "next-task.json",
        paths.agent_dir / "NEXT_TASK.md",
        paths.state_dir / "next-task-input.json",
    )

    assert (paths.state_dir / "next-task.json").exists()
    assert (paths.agent_dir / "NEXT_TASK.md").exists()
    assert not (paths.agent_dir / "tasks" / "real-sidecar-demo.md").exists()
    assert not (paths.agent_dir / "resume" / "real-sidecar-demo-resume.md").exists()


def test_supervision_core_does_not_require_heartbeat_summary(tmp_path: Path):
    seed_real_task(tmp_path)

    supervision = handle_supervision_trigger(tmp_path, "real-sidecar-demo", "on_interval")

    assert supervision["status"] == "active"
    assert (tmp_path / ".agent" / "heartbeat" / "latest-heartbeat.json").exists()
    assert not (tmp_path / ".agent" / "heartbeat" / "heartbeat-summary.json").exists()


def test_sidecars_can_be_materialized_later(tmp_path: Path):
    paths = seed_real_task(tmp_path)
    build_next_task_from_state_dir(
        paths.tasks_state_dir,
        paths.state_dir / "next-task.json",
        paths.agent_dir / "NEXT_TASK.md",
    )
    handle_supervision_trigger(tmp_path, "real-sidecar-demo", "on_interval")

    render_state_views_for_root(tmp_path)
    build_heartbeat_summary(tmp_path)

    assert (paths.agent_dir / "tasks" / "real-sidecar-demo.md").exists()
    assert (paths.agent_dir / "resume" / "real-sidecar-demo-resume.md").exists()
    assert (tmp_path / ".agent" / "heartbeat" / "heartbeat-summary.json").exists()
