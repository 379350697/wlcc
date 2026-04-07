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
    )

    task_path, index_path = write_task_state(paths, task)
    assert task_path.exists()
    assert index_path.exists()

    loaded = load_task_state(paths, "task-1")
    assert loaded["taskId"] == "task-1"
    assert loaded["status"] == "doing"
    assert loaded["updatedAt"] == "2026-04-06T12:00:00"
    assert loaded["eligibleForScheduling"] is False


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
