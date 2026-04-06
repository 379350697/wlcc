#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ALLOWED_STATUS = {'todo', 'doing', 'blocked', 'done'}
ALLOWED_PRIORITY = {'P0', 'P1', 'P2', 'P3'}
ALLOWED_OVERRIDE = {'none', 'force-run', 'force-hold'}


def main():
    parser = argparse.ArgumentParser(description='Write canonical task state store.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--project', required=True)
    parser.add_argument('--goal', required=True)
    parser.add_argument('--status', required=True)
    parser.add_argument('--priority', default='P2')
    parser.add_argument('--dependencies', default='[]')
    parser.add_argument('--override', default='none')
    parser.add_argument('--latest-result', required=True)
    parser.add_argument('--blocker', required=True)
    parser.add_argument('--next-step', required=True)
    parser.add_argument('--last-success', required=True)
    parser.add_argument('--last-failure', required=True)
    parser.add_argument('--updated-at', required=True)
    parser.add_argument('--kind', default='sample')
    parser.add_argument('--source', default='legacy')
    parser.add_argument('--execution-mode', default='sample-only')
    parser.add_argument('--owner-context', default='unknown')
    parser.add_argument('--supervision-state', default='legacy')
    parser.add_argument('--eligible-for-scheduling', choices=['true', 'false'], default='false')
    parser.add_argument('--is-primary-track', choices=['true', 'false'], default='false')
    parser.add_argument('--lifecycle', default='legacy')
    parser.add_argument('--title', default='')
    args = parser.parse_args()

    if args.status not in ALLOWED_STATUS:
        raise SystemExit(f'invalid status: {args.status}')
    if args.priority not in ALLOWED_PRIORITY:
        raise SystemExit(f'invalid priority: {args.priority}')
    if args.override not in ALLOWED_OVERRIDE:
        raise SystemExit(f'invalid override: {args.override}')

    root = Path(args.project_root)
    state_dir = root / '.agent' / 'state' / 'tasks'
    state_dir.mkdir(parents=True, exist_ok=True)
    task_path = state_dir / f'{args.task_id}.json'

    task = {
        'taskId': args.task_id,
        'project': args.project,
        'goal': args.goal,
        'status': args.status,
        'priority': args.priority,
        'dependencies': json.loads(args.dependencies),
        'override': args.override,
        'latestResult': args.latest_result,
        'blocker': args.blocker,
        'nextStep': args.next_step,
        'lastSuccess': args.last_success,
        'lastFailure': args.last_failure,
        'updatedAt': args.updated_at,
        'kind': args.kind,
        'source': args.source,
        'executionMode': args.execution_mode,
        'ownerContext': args.owner_context,
        'supervisionState': args.supervision_state,
        'eligibleForScheduling': args.eligible_for_scheduling == 'true',
        'isPrimaryTrack': args.is_primary_track == 'true',
        'lifecycle': args.lifecycle,
        'title': args.title,
    }
    task_path.write_text(json.dumps(task, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    index_path = root / '.agent' / 'state' / 'index.json'
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding='utf-8'))
    else:
        index = {'tasks': [], 'updatedAt': args.updated_at}

    if args.task_id not in index['tasks']:
        index['tasks'].append(args.task_id)
    index['tasks'] = sorted(index['tasks'])
    index['updatedAt'] = args.updated_at
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(f'OK: wrote {task_path}')
    print(f'OK: wrote {index_path}')


if __name__ == '__main__':
    main()
