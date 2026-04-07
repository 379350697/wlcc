import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_ingest_decomposed_leaf_rejects_draft_and_accepts_ready(tmp_path: Path):
    draft_payload = tmp_path / "draft-leaf.json"
    ready_payload = tmp_path / "ready-leaf.json"

    draft_payload.write_text(
        json.dumps(
            {
                "taskId": "leaf-draft",
                "parentTaskId": "task-parent",
                "goal": "draft leaf should not enter wlcc",
                "allowedPaths": ["runtime/"],
                "doneWhen": ["final-result recorded"],
                "requiredEvidence": ["final-result"],
                "status": "draft",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    ready_payload.write_text(
        json.dumps(
            {
                "taskId": "leaf-ready",
                "parentTaskId": "task-parent",
                "goal": "ready leaf may enter wlcc",
                "allowedPaths": ["runtime/"],
                "doneWhen": ["final-result recorded", "gap-check recorded", "status-update recorded"],
                "requiredEvidence": ["final-result", "gap-check", "status-update"],
                "requiredTests": ["python3 -m pytest tests/runtime/test_decomposed_leaf_ingest.py -q"],
                "status": "ready",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    draft = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "ingest_decomposed_leaf.py"),
            "--payload-file",
            str(draft_payload),
            "--project-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert draft.returncode != 0

    ready = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "ingest_decomposed_leaf.py"),
            "--payload-file",
            str(ready_payload),
            "--project-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert ready.returncode == 0

    task_path = tmp_path / ".agent" / "state" / "tasks" / "leaf-ready.json"
    assert task_path.exists()
    task = json.loads(task_path.read_text(encoding="utf-8"))
    assert task["status"] == "ready"
    assert task["parentTaskId"] == "task-parent"


def test_ingest_decomposed_leaf_rejects_incomplete_ready_contract(tmp_path: Path):
    invalid_ready_payload = tmp_path / "invalid-ready-leaf.json"
    invalid_ready_payload.write_text(
        json.dumps(
            {
                "taskId": "leaf-invalid-ready",
                "parentTaskId": "",
                "goal": "ready leaf missing closure contract should fail ingest",
                "allowedPaths": ["runtime/"],
                "doneWhen": [],
                "requiredEvidence": [],
                "requiredTests": [],
                "status": "ready",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "ingest_decomposed_leaf.py"),
            "--payload-file",
            str(invalid_ready_payload),
            "--project-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "contract" in (completed.stderr + completed.stdout) or "parentTaskId" in (completed.stderr + completed.stdout)
