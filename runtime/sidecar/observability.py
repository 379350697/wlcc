"""Observability dashboard sidecar service."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from runtime.common.io import read_json, write_json


def _read_text(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return "MISSING"


def _parse_event_blocks(path: Path) -> list[dict]:
    text = _read_text(path)
    if not text or text == "MISSING":
        return []
    blocks = []
    for block in text.split("## Event"):
        block = block.strip()
        if not block:
            continue
        item = {}
        for line in block.splitlines():
            line = line.strip()
            if not line.startswith("- ") or ": " not in line:
                continue
            key, value = line[2:].split(": ", 1)
            item[key] = value
        blocks.append(item)
    return blocks


def build_observability_dashboard(root: Path) -> tuple[dict, list[Path]]:
    audit_dir = root / ".agent" / "audit"
    loop_dir = root / ".agent" / "loop"
    logs_dir = root / ".agent" / "logs"

    audit_dir.mkdir(parents=True, exist_ok=True)

    loop_last_run = read_json(loop_dir / "last-run.json", {}) or {}
    check_summary = read_json(loop_dir / "check-summary.json", {}) or {}
    retry_state = read_json(loop_dir / "retry-state.json", {}) or {}
    failure_control = read_json(loop_dir / "failure-control.json", {}) or {}
    heartbeat_summary = read_json(root / ".agent" / "heartbeat" / "heartbeat-summary.json", {}) or {}
    system_healthcheck = _read_text(root / "tests" / "SYSTEM_HEALTHCHECK_RESULT.md")
    event_blocks = _parse_event_blocks(logs_dir / "EVENT_LOG.md")

    failure_counter = Counter()
    rollback_events = []
    retry_reorder_events = []
    check_failures = []

    for event in event_blocks:
        event_type = event.get("type", "unknown")
        result = event.get("result", "unknown")
        note = event.get("note", "")
        target = event.get("target", "unknown")
        if result == "failure" or "failure" in note or "rollback" in note or "risk" in note:
            failure_counter[target] += 1
        if "rollback" in note.lower() or event_type == "rollback":
            rollback_events.append(event)
        if event_type in {"task-loop-step", "task-update"} and any(token in note.lower() for token in ("retry", "reorder", "rollback")):
            retry_reorder_events.append(event)

    for item in check_summary.get("checks", []):
        if item.get("status") != "continue":
            check_failures.append({"name": item.get("name", "unknown"), "status": item.get("status", "unknown")})

    failure_clusters = [{"target": target, "count": count} for target, count in failure_counter.most_common()]
    loop_history = [
        step
        for step in loop_last_run.get("steps", [])
        if step.get("taskId", "").startswith("real-") or step.get("taskId") == "real-task-runtime-mainline"
    ]
    dashboard = {
        "loopHistory": loop_history,
        "checkHistory": check_summary.get("checks", []),
        "failureClusters": failure_clusters,
        "retryReorderRollbackHistory": {
            "retryState": retry_state,
            "latestFailureControl": failure_control,
            "matchedEvents": retry_reorder_events,
            "rollbackEvents": rollback_events,
        },
        "systemHealthSummary": {
            "heartbeatSummary": heartbeat_summary,
            "systemHealthcheck": system_healthcheck,
            "eventCount": len(event_blocks),
            "checkFailures": check_failures,
        },
    }

    dashboard_json = audit_dir / "observability-dashboard.json"
    dashboard_md = audit_dir / "OBSERVABILITY_DASHBOARD.md"
    write_json(dashboard_json, dashboard)

    lines = ["# OBSERVABILITY_DASHBOARD", "", "## loop_history"]
    if loop_history:
        last = loop_history[-1]
        lines.append(f"- steps: {len(loop_history)}")
        lines.append(f"- lastTask: {last.get('taskId', 'unknown')}")
        lines.append(f"- lastFailureControl: {last.get('failureControl', 'unknown')}")
        lines.append(f"- lastRiskEscalation: {last.get('riskEscalation', 'unknown')}")
    else:
        lines.append("- none")
    lines.extend(["", "## check_history"])
    if dashboard["checkHistory"]:
        for item in dashboard["checkHistory"]:
            lines.append(f"- {item.get('name', 'unknown')}: {item.get('status', 'unknown')}")
    else:
        lines.append("- none")
    lines.extend(["", "## failure_clusters"])
    if failure_clusters:
        for item in failure_clusters[:10]:
            lines.append(f"- {item['target']}: {item['count']}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## retry_reorder_rollback_history",
            f"- retryStateTasks: {len(retry_state)}",
            f"- latestFailureDecision: {failure_control.get('decision', 'none')}",
            f"- matchedEvents: {len(retry_reorder_events)}",
            f"- rollbackEvents: {len(rollback_events)}",
            "",
            "## runtime_scope",
            "- defaultScope: real-task-first",
            f"- realFailureClusterCount: {len([item for item in failure_clusters if str(item.get('target', '')).startswith('real-')])}",
            "",
            "## system_health_summary",
            f"- heartbeatHistoryCount: {heartbeat_summary.get('historyCount', 0)}",
            f"- heartbeatRequiresHumanCount: {heartbeat_summary.get('requiresHumanCount', 0)}",
            f"- eventCount: {len(event_blocks)}",
            f"- checkFailureCount: {len(check_failures)}",
        ]
    )
    if "## Overall" in system_healthcheck:
        overall_line = system_healthcheck.split("## Overall", 1)[1].strip().splitlines()[0].strip()
        lines.append(f"- systemHealthcheck: {overall_line}")
    dashboard_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dashboard, [dashboard_json, dashboard_md]
