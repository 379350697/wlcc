"""Sidecar rendering and reporting services."""

from __future__ import annotations

import json
from pathlib import Path

from runtime.common.io import write_json
from runtime.resume import build_resume_state_payload, collect_context_payload
from runtime.sidecar.heartbeat_summary import build_heartbeat_summary
from runtime.sidecar.observability import build_observability_dashboard
from runtime.sidecar.tasks_view import check_state_view_consistency, render_state_views_for_root


def _read_text(path: Path) -> str | None:
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return None


def _read_required_text(path: Path) -> str:
    return _read_text(path) or "MISSING"


def _parse_event_blocks(path: Path) -> list[dict]:
    text = _read_text(path)
    if not text:
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


def write_retrieve_context_output(root: Path, task_id: str, output: Path | None = None) -> tuple[dict, Path]:
    payload = collect_context_payload(root, task_id)
    output = output or root / "tests" / "RETRIEVE_CONTEXT_OUTPUT.json"
    write_json(output, payload)
    return payload, output


def write_resume_state_output(root: Path, task_ids: list[str], output: Path) -> tuple[dict, Path]:
    payload = build_resume_state_payload(root, task_ids)
    write_json(output, payload)
    return payload, output
