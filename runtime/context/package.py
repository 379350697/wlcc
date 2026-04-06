from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime.context.budget import (
    DEFAULT_CONTEXT_BUDGET_CHARS,
    DEFAULT_SECTION_BUDGETS,
    clip_item_content,
    clip_text,
    estimate_serialized_chars,
)


@dataclass(frozen=True)
class ContextPackage:
    payload: dict[str, Any]
    meta: dict[str, Any]


def read_text(path: Path) -> str | None:
    return path.read_text(encoding='utf-8').strip() if path.exists() else None


def read_json(path: Path) -> dict[str, Any] | None:
    content = read_text(path)
    if not content:
        return None
    try:
        parsed = json.loads(content)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _section_items_with_sources(root: Path, sources: list[Path], is_task_state: bool = False) -> tuple[list[dict], list[str], bool, str]:
    items: list[dict] = []
    used_sources: list[str] = []
    canonical_found = False
    markdown_fallback_used = False
    task_kind = 'unknown'

    for path in sources:
        content = read_text(path)
        if not content:
            continue
        rel = str(path.relative_to(root))
        if path.suffix == '.json':
            parsed = read_json(path)
            if parsed is None:
                continue
            if is_task_state and path.name.endswith('.json'):
                task_kind = parsed.get('kind', task_kind)
            items.append({'source': rel, 'content': parsed})
            canonical_found = True
        else:
            items.append({'source': rel, 'content': content})
            markdown_fallback_used = True
        used_sources.append(rel)

    return items, used_sources, (not canonical_found and markdown_fallback_used), task_kind


def collect_context_sources(root: Path, task_id: str) -> dict[str, Any]:
    fact_sources = [root / name for name in ('README.md', 'STATUS.md', 'DECISIONS.md', 'TASKS.md', 'INCIDENTS.md')]
    task_state_sources = [
        root / '.agent' / 'state' / 'tasks' / f'{task_id}.json',
        root / '.agent' / 'tasks' / f'{task_id}.md',
        root / '.agent' / 'resume' / f'{task_id}-resume.md',
        root / '.agent' / 'state' / 'next-task.json',
        root / '.agent' / 'NEXT_TASK.md',
    ]
    summary_sources = [root / 'memory' / 'session' / 'SESSION_SUMMARY.md', root / 'FINAL_DELIVERY_SUMMARY.md']

    facts, fact_used, _, _ = _section_items_with_sources(root, fact_sources)
    task_state, task_used, degraded_fallback, task_kind = _section_items_with_sources(root, task_state_sources, is_task_state=True)
    summary, summary_used, _, _ = _section_items_with_sources(root, summary_sources)

    return {
        'facts': facts,
        'task_state': task_state,
        'summary': summary,
        'chat': [],
        'meta': {
            'priority': ['facts', 'task_state', 'summary', 'chat'],
            'usedSources': fact_used + task_used + summary_used,
            'degradedFallback': degraded_fallback,
            'taskKind': task_kind,
        },
    }


def _apply_item_budget(items: list[dict], max_items: int, string_limit: int) -> tuple[list[dict], bool]:
    trimmed = False
    kept = []
    for item in items[:max_items]:
        normalized = dict(item)
        content = normalized.get('content')
        clipped, did_clip = clip_item_content(content, string_limit)
        if did_clip:
            trimmed = True
        normalized['content'] = clipped
        kept.append(normalized)
    if len(items) > max_items:
        trimmed = True
    return kept, trimmed


def package_context_payload(payload: dict[str, Any], budget_chars: int = DEFAULT_CONTEXT_BUDGET_CHARS) -> ContextPackage:
    if payload.get('meta', {}).get('packageVersion') == 1 and 'contextBudgetChars' in payload.get('meta', {}):
        return ContextPackage(payload=payload, meta=dict(payload.get('meta', {})))

    facts = list(payload.get('facts', []))
    task_state = list(payload.get('task_state', []))
    summary = list(payload.get('summary', []))
    chat = list(payload.get('chat', []))
    meta = dict(payload.get('meta', {}))

    fact_limit = DEFAULT_SECTION_BUDGETS['facts']
    task_state_limit = DEFAULT_SECTION_BUDGETS['task_state']
    summary_limit = DEFAULT_SECTION_BUDGETS['summary']
    chat_limit = DEFAULT_SECTION_BUDGETS['chat']

    packaged_facts, facts_trimmed = _apply_item_budget(facts, 5, fact_limit)
    packaged_task_state, task_state_trimmed = _apply_item_budget(task_state, 5, task_state_limit)
    packaged_summary, summary_trimmed = _apply_item_budget(summary, 2, summary_limit)
    packaged_chat, chat_trimmed = _apply_item_budget(chat, 2, chat_limit)

    packaged = {
        'facts': packaged_facts,
        'task_state': packaged_task_state,
        'summary': packaged_summary,
        'chat': packaged_chat,
    }

    serialized_chars = estimate_serialized_chars(packaged)
    total_trimmed = facts_trimmed or task_state_trimmed or summary_trimmed or chat_trimmed or serialized_chars > budget_chars

    if serialized_chars > budget_chars:
        while serialized_chars > budget_chars and packaged_summary:
            packaged_summary.pop()
            total_trimmed = True
            serialized_chars = estimate_serialized_chars({**packaged, 'summary': packaged_summary})
        while serialized_chars > budget_chars and packaged_chat:
            packaged_chat.pop()
            total_trimmed = True
            serialized_chars = estimate_serialized_chars({**packaged, 'summary': packaged_summary, 'chat': packaged_chat})

    packaged['summary'] = packaged_summary
    packaged['chat'] = packaged_chat

    if serialized_chars > budget_chars:
        for section_name in ('facts', 'task_state'):
            section_items = list(packaged[section_name])
            for index in range(len(section_items) - 1, -1, -1):
                item = dict(section_items[index])
                if isinstance(item.get('content'), str):
                    clipped, did_clip = clip_text(item['content'], 120)
                    if did_clip:
                        item['content'] = clipped
                        section_items[index] = item
                        total_trimmed = True
                        serialized_chars = estimate_serialized_chars({**packaged, section_name: section_items})
                        if serialized_chars <= budget_chars:
                            packaged[section_name] = section_items
                            break
            packaged[section_name] = section_items
            if serialized_chars <= budget_chars:
                break

    meta.update({
        'packageVersion': 1,
        'contextBudgetChars': budget_chars,
        'contextTrimmed': total_trimmed,
        'sectionBudgets': dict(DEFAULT_SECTION_BUDGETS),
    })

    meta['packagedChars'] = 0
    meta['contextBudgetExceeded'] = False
    for _ in range(3):
        packaged['meta'] = meta
        current_serialized_chars = estimate_serialized_chars(packaged)
        if meta['packagedChars'] == current_serialized_chars and meta['contextBudgetExceeded'] == (current_serialized_chars > budget_chars):
            break
        meta['packagedChars'] = current_serialized_chars
        meta['contextBudgetExceeded'] = current_serialized_chars > budget_chars
    packaged['meta'] = meta
    return ContextPackage(payload=packaged, meta=meta)
