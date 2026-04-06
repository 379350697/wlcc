#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


root = Path(__file__).resolve().parent.parent


def now_text():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def build_human_summary(heartbeat):
    return f"[{heartbeat['triggerReason']}] {heartbeat['stage']} | task={heartbeat['currentTask']} | next={heartbeat['nextStep']} | blocker={heartbeat['riskOrBlocker']}"


def should_throttle(previous, heartbeat, throttle_seconds: int):
    if not previous:
        return False
    previous_key = (
        previous.get('stage'),
        previous.get('currentTask'),
        previous.get('nextStep'),
        previous.get('triggerReason'),
        previous.get('riskOrBlocker'),
        previous.get('requiresHuman'),
    )
    current_key = (
        heartbeat.get('stage'),
        heartbeat.get('currentTask'),
        heartbeat.get('nextStep'),
        heartbeat.get('triggerReason'),
        heartbeat.get('riskOrBlocker'),
        heartbeat.get('requiresHuman'),
    )
    if previous_key != current_key:
        return False
    previous_time = previous.get('emittedAt')
    if not previous_time:
        return False
    try:
        delta = datetime.now() - datetime.fromisoformat(previous_time)
    except ValueError:
        return False
    return delta.total_seconds() < throttle_seconds


def append_history(path: Path, heartbeat):
    history = load_json(path, [])
    history.append(heartbeat)
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return history


def write_markdown_result(heartbeat, throttled: bool):
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
    out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return out_md


def main():
    parser = argparse.ArgumentParser(description='Emit structured heartbeat report for long-chain autonomy.')
    parser.add_argument('--stage', required=True)
    parser.add_argument('--current-task', required=True)
    parser.add_argument('--next-step', required=True)
    parser.add_argument('--trigger-reason', required=True)
    parser.add_argument('--requires-human', action='store_true')
    parser.add_argument('--completed-items', nargs='*', default=[])
    parser.add_argument('--risk-or-blocker', default='none')
    parser.add_argument('--throttle-seconds', type=int, default=60)
    args = parser.parse_args()

    heartbeat_dir = root / '.agent' / 'heartbeat'
    heartbeat_dir.mkdir(parents=True, exist_ok=True)
    latest_path = heartbeat_dir / 'latest-heartbeat.json'
    history_path = heartbeat_dir / 'heartbeat-history.json'

    heartbeat = {
        'stage': args.stage,
        'completedItems': args.completed_items,
        'currentTask': args.current_task,
        'riskOrBlocker': args.risk_or_blocker,
        'nextStep': args.next_step,
        'requiresHuman': args.requires_human,
        'triggerReason': args.trigger_reason,
        'emittedAt': datetime.now().isoformat(timespec='seconds'),
    }
    heartbeat['humanSummary'] = build_human_summary(heartbeat)

    previous = load_json(latest_path, None)
    throttled = should_throttle(previous, heartbeat, args.throttle_seconds)
    heartbeat['throttled'] = throttled

    latest_path.write_text(json.dumps(heartbeat, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not throttled:
        append_history(history_path, heartbeat)

    out_md = write_markdown_result(heartbeat, throttled)
    print(f'OK: wrote {latest_path}')
    print(f'OK: wrote {history_path}')
    print(f'OK: wrote {out_md}')


if __name__ == '__main__':
    main()
