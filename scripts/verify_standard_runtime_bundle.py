#!/usr/bin/env python3
"""Run the standard runtime verification bundle."""
import subprocess
from pathlib import Path


root = Path(__file__).resolve().parent.parent

CHECKS = [
    ("bootstrap-fixtures", ["python3", str(root / "scripts" / "bootstrap_runtime_fixtures.py")]),
    ("control-plane-smoke", ["python3", str(root / "scripts" / "test_control_plane_smoke.py")]),
    ("runtime-pytest", ["python3", "-m", "pytest", "tests/runtime", "-q"]),
    ("tool-harness", ["python3", str(root / "scripts" / "test_tool_harness.py")]),
    ("progress-task-runtime", ["python3", str(root / "scripts" / "test_progress_task_runtime.py")]),
    ("ingest-real-task", ["python3", str(root / "scripts" / "test_ingest_real_task.py")]),
    ("close-task-runtime", ["python3", str(root / "scripts" / "test_close_task_runtime.py")]),
    ("resume-real-task", ["python3", str(root / "scripts" / "test_resume_real_task.py")]),
    ("task-supervision", ["python3", str(root / "scripts" / "test_task_supervision.py")]),
    ("heartbeat-summary", ["python3", str(root / "scripts" / "test_heartbeat_summary.py")]),
    ("observability-dashboard", ["python3", str(root / "scripts" / "test_observability_dashboard.py")]),
    ("render-state-views", ["python3", str(root / "scripts" / "render_state_views.py"), "--project-root", str(root)]),
    ("state-view-consistency", ["python3", str(root / "scripts" / "check_state_view_consistency.py")]),
    ("retrieval-priority", ["python3", str(root / "scripts" / "check_retrieval_priority.py")]),
    ("system-healthcheck", ["python3", str(root / "scripts" / "system_healthcheck.py")]),
    ("phase2-mainline", ["python3", str(root / "scripts" / "check_phase2_mainline.py")]),
]


def main():
    results = []
    for name, command in CHECKS:
        completed = subprocess.run(command, capture_output=True, text=True)
        results.append(
            {
                "name": name,
                "ok": completed.returncode == 0,
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
            }
        )

    out = root / "tests" / "STANDARD_RUNTIME_BUNDLE_VERIFICATION.md"
    lines = ["# STANDARD_RUNTIME_BUNDLE_VERIFICATION", "", "## checks"]
    for item in results:
        lines.append(f"- {item['name']}: {'PASS' if item['ok'] else 'FAIL'}")
        if item["stdout"]:
            lines.append(f"  - stdout: {item['stdout'][:400]}")
        if item["stderr"]:
            lines.append(f"  - stderr: {item['stderr'][:400]}")
    overall = all(item["ok"] for item in results)
    lines.extend(["", "## overall", f"- status: {'PASS' if overall else 'FAIL'}"])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: wrote {out}")
    raise SystemExit(0 if overall else 1)


if __name__ == "__main__":
    main()
