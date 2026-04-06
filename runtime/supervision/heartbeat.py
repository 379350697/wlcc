"""Heartbeat primitives for runtime supervision."""
import json
from datetime import datetime
from pathlib import Path


def _read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def build_human_summary(heartbeat: dict) -> str:
    return f"[{heartbeat['triggerReason']}] {heartbeat['stage']} | task={heartbeat['currentTask']} | next={heartbeat['nextStep']} | blocker={heartbeat['riskOrBlocker']}"


def should_throttle(previous: dict | None, heartbeat: dict, throttle_seconds: int) -> bool:
    if not previous:
        return False
    previous_key = (
        previous.get('stage'), previous.get('currentTask'), previous.get('nextStep'), previous.get('triggerReason'), previous.get('riskOrBlocker'), previous.get('requiresHuman'),
    )
    current_key = (
        heartbeat.get('stage'), heartbeat.get('currentTask'), heartbeat.get('nextStep'), heartbeat.get('triggerReason'), heartbeat.get('riskOrBlocker'), heartbeat.get('requiresHuman'),
    )
    if previous_key != current_key:
        return False
    previous_time = previous.get('emittedAt') or previous.get('timestamp')
    if not previous_time:
        return False
    try:
        delta = datetime.now() - datetime.fromisoformat(previous_time)
    except ValueError:
        return False
    return delta.total_seconds() < throttle_seconds


def append_history(path: Path, heartbeat: dict):
    history = _read_json(path, [])
    history.append(heartbeat)
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return history


def write_markdown_result(root: Path, heartbeat: dict, throttled: bool) -> Path:
    lines = ['# HEARTBEAT_RESULT', '', '## summary']
    lines.append(f"- stage: {heartbeat['stage']}")
    lines.append(f"- currentTask: {heartbeat['currentTask']}")
    lines.append(f"- riskOrBlocker: {heartbeat['riskOrBlocker']}")
    lines.append(f"- nextStep: {heartbeat['nextStep']}")
    lines.append(f"- requiresHuman: {str(heartbeat['requiresHuman']).lower()}")
    lines.append(f"- triggerReason: {heartbeat['triggerReason']}")
    lines.append(f"- emittedAt: {heartbeat['emittedAt']}")
    lines.append(f"- throttled: {str(throttled).lower()}")
    lines.append('')
    lines.append('## completedItems')
    if heartbeat['completedItems']:
        lines.extend(f"- {item}" for item in heartbeat['completedItems'])
    else:
        lines.append('- none')
    lines.append('')
    lines.append('## humanSummary')
    lines.append(f"- {heartbeat['humanSummary']}")
    out_md = root / 'tests' / 'HEARTBEAT_RESULT.md'
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return out_md


def emit_heartbeat_record(root: Path, payload: dict, throttle_seconds: int = 60, write_markdown: bool = True) -> dict:
    heartbeat_dir = root / '.agent' / 'heartbeat'
    heartbeat_dir.mkdir(parents=True, exist_ok=True)
    latest_path = heartbeat_dir / 'latest-heartbeat.json'
    history_path = heartbeat_dir / 'heartbeat-history.json'
    heartbeat = {
        'stage': payload['stage'],
        'completedItems': payload.get('completedItems', []),
        'currentTask': payload['currentTask'],
        'riskOrBlocker': payload.get('riskOrBlocker', 'none'),
        'nextStep': payload['nextStep'],
        'requiresHuman': payload.get('requiresHuman', False),
        'triggerReason': payload['triggerReason'],
        'emittedAt': datetime.now().isoformat(timespec='seconds'),
    }
    heartbeat['humanSummary'] = build_human_summary(heartbeat)
    previous = _read_json(latest_path, None)
    throttled = should_throttle(previous, heartbeat, throttle_seconds)
    heartbeat['throttled'] = throttled
    latest_path.write_text(json.dumps(heartbeat, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not throttled:
        append_history(history_path, heartbeat)
    if write_markdown:
        write_markdown_result(root, heartbeat, throttled)
    return heartbeat
