#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent.parent
ALLOWED = {'new', 'ingested', 'active', 'blocked', 'waiting-human', 'handoff', 'done', 'archived', 'legacy'}
TRANSITIONS = {
    'new': {'ingested'},
    'ingested': {'active', 'blocked', 'waiting-human', 'handoff'},
    'active': {'blocked', 'waiting-human', 'handoff', 'done'},
    'blocked': {'active', 'waiting-human', 'handoff'},
    'waiting-human': {'active', 'handoff', 'done'},
    'handoff': {'active', 'waiting-human', 'done'},
    'done': {'archived'},
    'archived': set(),
    'legacy': {'ingested', 'active', 'blocked', 'waiting-human', 'handoff', 'done'},
}
SUPERVISION_MAP = {
    'new': 'new',
    'ingested': 'ingested',
    'active': 'active',
    'blocked': 'blocked',
    'waiting-human': 'waiting-human',
    'handoff': 'handoff',
    'done': 'done',
    'archived': 'archived',
    'legacy': 'legacy',
}


def main():
    parser = argparse.ArgumentParser(description='Update task lifecycle with transition validation.')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--to', required=True)
    args = parser.parse_args()

    if args.to not in ALLOWED:
        raise SystemExit(f'invalid lifecycle target: {args.to}')

    path = root / '.agent' / 'state' / 'tasks' / f'{args.task_id}.json'
    if not path.exists():
        raise SystemExit(f'missing task: {args.task_id}')

    task = json.loads(path.read_text(encoding='utf-8'))
    current = task.get('lifecycle', 'legacy')
    if args.to not in TRANSITIONS.get(current, set()):
        raise SystemExit(f'illegal lifecycle transition: {current} -> {args.to}')

    task['lifecycle'] = args.to
    task['supervisionState'] = SUPERVISION_MAP[args.to]
    if args.to == 'archived':
        task['eligibleForScheduling'] = False
        task['isPrimaryTrack'] = False
    elif args.to in {'ingested', 'active', 'blocked', 'waiting-human', 'handoff'} and task.get('kind') == 'real':
        task['eligibleForScheduling'] = args.to in {'ingested', 'active', 'blocked', 'waiting-human', 'handoff'}
    task['updatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M Asia/Shanghai')
    path.write_text(json.dumps(task, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    supervision_path = root / '.agent' / 'state' / 'supervision' / f'{args.task_id}.json'
    if supervision_path.exists():
        supervision = json.loads(supervision_path.read_text(encoding='utf-8'))
    else:
        supervision = {'taskId': args.task_id}
    supervision['status'] = SUPERVISION_MAP[args.to]
    supervision['updatedAt'] = task['updatedAt']
    supervision['stale'] = args.to in {'blocked', 'waiting-human'}
    supervision_path.parent.mkdir(parents=True, exist_ok=True)
    supervision_path.write_text(json.dumps(supervision, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    out = root / 'tests' / 'TASK_LIFECYCLE_RESULT.md'
    lines = ['# TASK_LIFECYCLE_RESULT', '', '## summary']
    lines.append(f'- taskId: {args.task_id}')
    lines.append(f'- from: {current}')
    lines.append(f'- to: {args.to}')
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {path}')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
