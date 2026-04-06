"""Context collection helpers for resume and retrieval flows."""

from __future__ import annotations

import json
from pathlib import Path


def read_text(path: Path):
    return path.read_text(encoding="utf-8").strip() if path.exists() else None


def collect_context_payload(root: Path, task_id: str) -> dict:
    fact_sources = [root / name for name in ("README.md", "STATUS.md", "DECISIONS.md", "TASKS.md", "INCIDENTS.md")]
    task_state_sources = [
        root / ".agent" / "state" / "tasks" / f"{task_id}.json",
        root / ".agent" / "tasks" / f"{task_id}.md",
        root / ".agent" / "resume" / f"{task_id}-resume.md",
        root / ".agent" / "state" / "next-task.json",
        root / ".agent" / "NEXT_TASK.md",
    ]
    summary_sources = [root / "memory" / "session" / "SESSION_SUMMARY.md", root / "FINAL_DELIVERY_SUMMARY.md"]
    used = []
    degraded = False
    result = {"facts": [], "task_state": [], "summary": [], "chat": []}
    for path in fact_sources:
        content = read_text(path)
        if content:
            result["facts"].append({"source": str(path.relative_to(root)), "content": content[:300]})
            used.append(str(path.relative_to(root)))
    canonical_found = False
    markdown_fallback_used = False
    current_task_kind = "unknown"
    for path in task_state_sources:
        content = read_text(path)
        if content:
            if path.suffix == ".json":
                parsed = json.loads(content)
                if path.name == f"{task_id}.json":
                    current_task_kind = parsed.get("kind", "unknown")
                result["task_state"].append({"source": str(path.relative_to(root)), "content": parsed})
                canonical_found = True
            else:
                result["task_state"].append({"source": str(path.relative_to(root)), "content": content[:300]})
                markdown_fallback_used = True
            used.append(str(path.relative_to(root)))
    if not canonical_found and markdown_fallback_used:
        degraded = True
    for path in summary_sources:
        content = read_text(path)
        if content:
            result["summary"].append({"source": str(path.relative_to(root)), "content": content[:300]})
            used.append(str(path.relative_to(root)))
    result["meta"] = {
        "priority": ["facts", "task_state", "summary", "chat"],
        "usedSources": used,
        "degradedFallback": degraded,
        "taskKind": current_task_kind,
    }
    return result
