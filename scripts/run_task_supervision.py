#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.supervision.core import handle_supervision_trigger


def main():
    parser = argparse.ArgumentParser(description='Run unified task supervision triggers.')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--trigger', required=True, choices=['on_task_ingested', 'on_task_changed', 'on_interruption_detected', 'on_interval', 'on_completion'])
    args = parser.parse_args()

    supervision = handle_supervision_trigger(root, args.task_id, args.trigger)

    out = root / 'tests' / 'TASK_SUPERVISION_RESULT.md'
    lines = ['# TASK_SUPERVISION_RESULT', '', '## summary']
    lines.append(f'- taskId: {args.task_id}')
    lines.append(f'- trigger: {args.trigger}')
    lines.append(f"- status: {supervision.get('status', 'unknown')}")
    lines.append(f"- stale: {str(supervision.get('stale', False)).lower()}")
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
