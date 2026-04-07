import json
from pathlib import Path

from runtime.supervision.heartbeat import emit_heartbeat_record


def test_emit_heartbeat_tolerates_corrupted_latest_file(tmp_path: Path):
    heartbeat_dir = tmp_path / ".agent" / "heartbeat"
    heartbeat_dir.mkdir(parents=True, exist_ok=True)
    (heartbeat_dir / "latest-heartbeat.json").write_text(
        '{"stage":"bad"}\n{"extra":"corruption"}\n',
        encoding="utf-8",
    )

    heartbeat = emit_heartbeat_record(
        tmp_path,
        {
            "stage": "lifecycle-active",
            "currentTask": "task-1",
            "nextStep": "continue current leaf",
            "triggerReason": "periodic-step",
            "riskOrBlocker": "none",
        },
        throttle_seconds=0,
    )

    latest = json.loads((heartbeat_dir / "latest-heartbeat.json").read_text(encoding="utf-8"))
    assert heartbeat["currentTask"] == "task-1"
    assert latest["currentTask"] == "task-1"
