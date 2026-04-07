import json
from pathlib import Path

from runtime.common.paths import RuntimePaths
from runtime.flow.models import TaskFlowRecord
from runtime.flow.store import bind_task_to_flow, create_task_flow, load_task_flow, recompute_flow


def test_create_task_flow_persists_owner_and_reply_mode(tmp_path: Path):
    paths = RuntimePaths(tmp_path)
    flow = TaskFlowRecord(
        taskFlowId="flow-1",
        ownerSessionId="session-123",
        goal="close one bounded execution flow",
        status="active",
        currentLeafTaskId="leaf-1",
        closedLeafCount=0,
        openLeafCount=1,
        replyMode="restricted",
        createdAt="2026-04-07T12:00:00",
        updatedAt="2026-04-07T12:00:00",
    )

    flow_path = create_task_flow(paths, flow)

    assert flow_path.exists()
    saved = json.loads(flow_path.read_text(encoding="utf-8"))
    assert saved["ownerSessionId"] == "session-123"
    assert saved["currentLeafTaskId"] == "leaf-1"
    assert saved["replyMode"] == "restricted"


def test_bind_task_to_flow_updates_task_metadata(tmp_path: Path):
    paths = RuntimePaths(tmp_path)
    task_path = paths.tasks_state_dir / "leaf-1.json"
    task_path.parent.mkdir(parents=True, exist_ok=True)
    task_path.write_text(
        json.dumps(
            {
                "taskId": "leaf-1",
                "project": "wlcc",
                "goal": "do one thing",
                "status": "ready",
                "kind": "real",
                "taskLevel": "leaf",
                "phase": "analyze",
                "doneWhen": ["final-result recorded"],
                "requiredEvidence": ["final-result"],
                "allowedPaths": ["runtime/"],
                "updatedAt": "2026-04-07T12:00:00",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    bind_task_to_flow(paths, "leaf-1", "flow-1", owner_session_id="session-123")

    saved = json.loads(task_path.read_text(encoding="utf-8"))
    assert saved["taskFlowId"] == "flow-1"
    assert saved["ownerSessionId"] == "session-123"


def test_recompute_flow_derives_counts_and_status_from_owned_leaves(tmp_path: Path):
    paths = RuntimePaths(tmp_path)
    create_task_flow(
        paths,
        TaskFlowRecord(
            taskFlowId="flow-1",
            ownerSessionId="session-123",
            goal="close one bounded execution flow",
            status="draft",
            currentLeafTaskId=None,
            createdAt="2026-04-07T12:00:00",
            updatedAt="2026-04-07T12:00:00",
        ),
    )

    _write_task(
        paths.tasks_state_dir / "leaf-1.json",
        {
            "taskId": "leaf-1",
            "status": "running",
            "lifecycle": "running",
            "taskLevel": "leaf",
            "taskFlowId": "flow-1",
            "updatedAt": "2026-04-07T12:10:00",
        },
    )
    _write_task(
        paths.tasks_state_dir / "leaf-2.json",
        {
            "taskId": "leaf-2",
            "status": "closed",
            "lifecycle": "archived",
            "taskLevel": "leaf",
            "taskFlowId": "flow-1",
            "updatedAt": "2026-04-07T12:05:00",
        },
    )

    recomputed = recompute_flow(paths, "flow-1")

    assert recomputed["status"] == "active"
    assert recomputed["currentLeafTaskId"] == "leaf-1"
    assert recomputed["openLeafCount"] == 1
    assert recomputed["closedLeafCount"] == 1
    assert recomputed["lastClosureTaskId"] == "leaf-2"

    loaded = load_task_flow(paths, "flow-1")
    assert loaded["status"] == "active"


def _write_task(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
