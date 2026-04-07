import json
from datetime import datetime, timezone
from pathlib import Path

from runtime.common.models import TaskState
from runtime.common.paths import RuntimePaths
from runtime.state.lifecycle import transition_lifecycle
from runtime.state.store import load_task_state, resolve_task_id, write_task_state


def test_write_task_state_creates_index_and_task(tmp_path: Path):
    paths = RuntimePaths(tmp_path)
    task = TaskState(
        taskId="task-1",
        project="demo",
        goal="do thing",
        status="doing",
        updatedAt="2026-04-06T12:00:00",
        taskFlowId="flow-1",
        ownerSessionId="session-123",
    )

    task_path, index_path = write_task_state(paths, task)
    assert task_path.exists()
    assert index_path.exists()

    loaded = load_task_state(paths, "task-1")
    assert loaded["taskId"] == "task-1"
    assert loaded["status"] == "doing"
    assert loaded["updatedAt"] == "2026-04-06T12:00:00"
    assert loaded["eligibleForScheduling"] is False
    assert loaded["taskFlowId"] == "flow-1"
    assert loaded["ownerSessionId"] == "session-123"


def test_transition_lifecycle_updates_task_and_supervision(tmp_path: Path):
    paths = RuntimePaths(tmp_path)
    task = TaskState(
        taskId="task-2",
        project="demo",
        goal="do thing",
        status="doing",
        kind="real",
        lifecycle="active",
        latestResult="real output",
        updatedAt="2026-04-06T12:00:00",
        eligibleForScheduling=True,
        isPrimaryTrack=True,
    )
    write_task_state(paths, task)

    updated_task, supervision, current = transition_lifecycle(paths, "task-2", "blocked")
    assert updated_task["lifecycle"] == "blocked"
    assert updated_task["supervisionState"] == "blocked"
    assert updated_task["eligibleForScheduling"] is True
    assert supervision["status"] == "blocked"
    assert supervision["stale"] is True
    assert current == "active"


def test_transition_lifecycle_supports_mechanized_execution_states(tmp_path: Path):
    paths = RuntimePaths(tmp_path)
    artifact = tmp_path / "tests" / "close-note.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text("close evidence\n", encoding="utf-8")
    heartbeat = tmp_path / ".agent" / "heartbeat" / "hb.json"
    heartbeat.parent.mkdir(parents=True, exist_ok=True)
    heartbeat.write_text(
        json.dumps(
            {
                "currentTask": "task-mechanized",
                "emittedAt": datetime.now(timezone.utc).isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    task = TaskState(
        taskId="task-mechanized",
        project="demo",
        goal="do one bounded leaf",
        status="ready",
        kind="real",
        lifecycle="ready",
        latestResult="tests/close-note.md real output",
        updatedAt="2026-04-06T12:00:00",
        eligibleForScheduling=True,
        isPrimaryTrack=True,
        allowedPaths=["runtime/"],
        doneWhen=["final-result recorded"],
        requiredEvidence=["final-result"],
    )
    write_task_state(paths, task)

    running_task, _, current = transition_lifecycle(paths, "task-mechanized", "running")
    assert current == "ready"
    assert running_task["lifecycle"] == "running"
    assert running_task["status"] == "running"
    assert running_task["eligibleForScheduling"] is True

    verify_task, _, _ = transition_lifecycle(paths, "task-mechanized", "verify")
    assert verify_task["lifecycle"] == "verify"
    assert verify_task["status"] == "verify"

    closed_task, _, _ = transition_lifecycle(paths, "task-mechanized", "closed")
    assert closed_task["lifecycle"] == "closed"
    assert closed_task["status"] == "closed"
    assert closed_task["eligibleForScheduling"] is False


def test_resolve_task_id_accepts_bare_real_task_alias(tmp_path: Path):
    paths = RuntimePaths(tmp_path)
    task = TaskState(
        taskId="real-task-3",
        project="demo",
        goal="do thing",
        status="doing",
        kind="real",
        lifecycle="active",
        updatedAt="2026-04-06T12:00:00",
        eligibleForScheduling=True,
        isPrimaryTrack=True,
    )
    write_task_state(paths, task)

    assert resolve_task_id(paths, "task-3") == "real-task-3"
    loaded = load_task_state(paths, "task-3")
    assert loaded["taskId"] == "real-task-3"


def test_write_task_state_recovers_from_corrupted_index(tmp_path: Path):
    paths = RuntimePaths(tmp_path)
    paths.state_dir.mkdir(parents=True, exist_ok=True)
    paths.index_path.write_text('{"tasks": ["broken"], "updatedAt": "2026-04-07T00:00:00"}\n}\n', encoding='utf-8')

    task = TaskState(
        taskId="task-4",
        project="demo",
        goal="repair corrupted index",
        status="doing",
        updatedAt="2026-04-07T12:00:00",
    )

    _, index_path = write_task_state(paths, task)

    loaded_index = index_path.read_text(encoding='utf-8')
    assert '"task-4"' in loaded_index
