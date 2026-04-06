from pathlib import Path

from runtime.common.io import append_line, read_json, write_json
from runtime.common.paths import RuntimePaths


def test_runtime_paths_resolve_state_dirs(tmp_path: Path):
    paths = RuntimePaths(tmp_path)
    assert paths.tasks_state_dir == tmp_path / ".agent" / "state" / "tasks"
    assert paths.supervision_state_dir == tmp_path / ".agent" / "state" / "supervision"
    assert paths.index_path == tmp_path / ".agent" / "state" / "index.json"


def test_json_round_trip_and_append_line(tmp_path: Path):
    payload = {"hello": "world"}
    path = tmp_path / "nested" / "data.json"
    write_json(path, payload)
    assert read_json(path) == payload

    log_path = tmp_path / "logs" / "events.log"
    append_line(log_path, "line-one")
    append_line(log_path, "line-two")
    assert log_path.read_text(encoding="utf-8").splitlines() == ["line-one", "line-two"]

