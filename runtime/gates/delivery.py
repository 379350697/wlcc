from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

EMPTY_PHRASES = frozenset({
    '已完成', '完成', '推进中', '继续', '进行中', '正在处理',
    'done', 'completed', 'in progress', 'continue', 'ok', 'wip',
})

HEARTBEAT_FRESHNESS_THRESHOLD = 300


def check_not_empty_phrase(latest_result: str) -> dict | None:
    normalized = latest_result.strip().lower()
    if normalized in EMPTY_PHRASES or len(normalized) < 5:
        return None
    return {'type': 'content', 'detail': 'latest_result is substantive'}


def check_file_exists(latest_result: str, project_root: Path) -> dict | None:
    candidate = project_root / latest_result.strip()
    if candidate.exists() and candidate.is_file():
        return {'type': 'file-exists', 'path': str(candidate.relative_to(project_root))}

    for token in latest_result.split():
        token = token.strip('`"\'()[]{}')
        if not token or token.startswith('-'):
            continue
        candidate = project_root / token
        if candidate.exists() and candidate.is_file():
            return {'type': 'file-exists', 'path': str(candidate.relative_to(project_root))}

    return None


def _heartbeat_timestamp(hb: dict) -> str:
    return hb.get('emittedAt') or hb.get('timestamp') or ''


def check_heartbeat_fresh(task_id: str, project_root: Path) -> dict | None:
    hb_dir = project_root / '.agent' / 'heartbeat'
    if not hb_dir.exists():
        return None

    hb_files = sorted(hb_dir.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not hb_files:
        return None

    try:
        hb = json.loads(hb_files[0].read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return None

    if hb.get('currentTask') != task_id:
        return None

    timestamp_str = _heartbeat_timestamp(hb)
    if not timestamp_str:
        return None

    try:
        hb_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        age_seconds = (datetime.now(hb_time.tzinfo) - hb_time).total_seconds()
    except (ValueError, TypeError):
        age_seconds = datetime.now().timestamp() - hb_files[0].stat().st_mtime

    if age_seconds <= HEARTBEAT_FRESHNESS_THRESHOLD:
        return {'type': 'heartbeat-fresh', 'age_seconds': round(age_seconds)}

    return None


def check_files_changed(task_id: str, project_root: Path) -> dict | None:
    task_path = project_root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
    if not task_path.exists():
        return None

    try:
        json.loads(task_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return None

    baseline = task_path.stat().st_mtime
    scan_dirs = [
        project_root / '.agent' / 'state',
        project_root / '.agent' / 'tasks',
        project_root / '.agent' / 'resume',
        project_root / 'tests',
    ]

    changed_count = 0
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for f in scan_dir.rglob('*'):
            if f.is_file() and f.stat().st_mtime > baseline:
                changed_count += 1
                if changed_count >= 3:
                    break
        if changed_count >= 3:
            break

    if changed_count > 0:
        return {'type': 'file-changes', 'count': changed_count}

    return None


def evaluate_delivery_gate(task_id: str, latest_result: str, project_root: Path,
                           task_kind: str = 'sample') -> dict:
    min_evidence = 2 if task_kind == 'real' else 1
    collectors = [
        ('content', lambda: check_not_empty_phrase(latest_result)),
        ('file', lambda: check_file_exists(latest_result, project_root)),
        ('heartbeat', lambda: check_heartbeat_fresh(task_id, project_root)),
        ('file-change', lambda: check_files_changed(task_id, project_root)),
    ]

    evidence = []
    for _name, collector in collectors:
        try:
            result = collector()
            if result is not None:
                evidence.append(result)
        except Exception:
            pass

    passed = len(evidence) >= min_evidence
    reason = 'ok' if passed else f'insufficient evidence: {len(evidence)}/{min_evidence}'
    return {
        'passed': passed,
        'reason': reason,
        'evidence': evidence,
        'required': min_evidence,
        'collected': len(evidence),
    }

