from __future__ import annotations

import json
from typing import Any


DEFAULT_CONTEXT_BUDGET_CHARS = 2400
DEFAULT_SECTION_BUDGETS = {
    'facts': 800,
    'task_state': 1200,
    'summary': 300,
    'chat': 100,
}


def clip_text(text: str, limit: int, suffix: str = '... [truncated]') -> tuple[str, bool]:
    value = text.strip()
    if limit <= 0 or len(value) <= limit:
        return value, False
    if limit <= len(suffix):
        return value[:limit], True
    return value[: limit - len(suffix)] + suffix, True


def estimate_serialized_chars(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(',', ':')))


def clip_item_content(content: Any, limit: int) -> tuple[Any, bool]:
    if isinstance(content, str):
        return clip_text(content, limit)
    return content, False

