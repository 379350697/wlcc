"""Context collection helpers for resume and retrieval flows."""

from __future__ import annotations

from pathlib import Path

from runtime.context.package import collect_context_sources, package_context_payload


def collect_context_payload(root: Path, task_id: str) -> dict:
    raw_payload = collect_context_sources(root, task_id)
    return package_context_payload(raw_payload).payload
