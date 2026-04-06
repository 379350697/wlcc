"""Heartbeat summary sidecar service."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from runtime.common.io import read_json, write_json


def _extract_day(timestamp: str) -> str:
    if not timestamp:
        return "unknown"
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return "unknown"


def _normalize_heartbeat_history(history: object) -> list[dict]:
    if isinstance(history, list):
        return [item for item in history if isinstance(item, dict)]
    if isinstance(history, dict):
        return [history]
    return []


def build_heartbeat_summary(root: Path) -> tuple[dict, list[Path]]:
    heartbeat_dir = root / ".agent" / "heartbeat"
    history = _normalize_heartbeat_history(read_json(heartbeat_dir / "heartbeat-history.json", []))
    latest = read_json(heartbeat_dir / "latest-heartbeat.json", {}) or {}

    by_stage = Counter()
    by_day = Counter()
    anomalies = []
    requires_human_count = 0

    for item in history:
        by_stage[item.get("stage", "unknown")] += 1
        by_day[_extract_day(item.get("emittedAt") or item.get("timestamp") or "")] += 1
        if item.get("requiresHuman"):
            requires_human_count += 1
        trigger = item.get("triggerReason", "unknown")
        if trigger in {"stage-complete-stop", "risk-stop", "wait-confirmation", "degraded-continue", "anomaly-stop"}:
            anomalies.append(
                {
                    "emittedAt": item.get("emittedAt") or item.get("timestamp") or "unknown",
                    "triggerReason": trigger,
                    "currentTask": item.get("currentTask", "unknown"),
                    "humanSummary": item.get("humanSummary", ""),
                }
            )

    summary = {
        "latest": latest,
        "historyCount": len(history),
        "requiresHumanCount": requires_human_count,
        "stageSummary": [{"stage": stage, "count": count} for stage, count in sorted(by_stage.items())],
        "dailySummary": [{"day": day, "count": count} for day, count in sorted(by_day.items())],
        "anomalyHeartbeats": anomalies,
    }

    summary_path = heartbeat_dir / "heartbeat-summary.json"
    summary_md_path = root / "tests" / "HEARTBEAT_SUMMARY_RESULT.md"
    write_json(summary_path, summary)

    lines = ["# HEARTBEAT_SUMMARY_RESULT", "", "## latest"]
    if latest:
        lines.append(f"- stage: {latest.get('stage', 'unknown')}")
        lines.append(f"- currentTask: {latest.get('currentTask', 'unknown')}")
        lines.append(f"- triggerReason: {latest.get('triggerReason', 'unknown')}")
        lines.append(f"- humanSummary: {latest.get('humanSummary', 'none')}")
    else:
        lines.append("- none")
    lines.extend(["", "## summary", f"- historyCount: {len(history)}", f"- requiresHumanCount: {requires_human_count}", "", "## dailySummary"])
    if summary["dailySummary"]:
        for item in summary["dailySummary"]:
            lines.append(f"- {item['day']}: {item['count']}")
    else:
        lines.append("- none")
    lines.extend(["", "## stageSummary"])
    if summary["stageSummary"]:
        for item in summary["stageSummary"]:
            lines.append(f"- {item['stage']}: {item['count']}")
    else:
        lines.append("- none")
    lines.extend(["", "## anomalyHeartbeats"])
    if anomalies:
        for item in anomalies[-10:]:
            lines.append(f"- {item['emittedAt']} | {item['triggerReason']} | {item['currentTask']} | {item['humanSummary']}")
    else:
        lines.append("- none")
    summary_md_path.parent.mkdir(parents=True, exist_ok=True)
    summary_md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary, [summary_path, summary_md_path]
