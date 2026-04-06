#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def load_task_state(task_id: str):
    task_path = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
    if not task_path.exists():
        return {}
    return json.loads(task_path.read_text(encoding='utf-8'))


def compute_backoff_delay(retries: int, mode: str):
    if mode == 'none':
        return 0
    if mode == 'linear':
        return retries
    if mode == 'bounded':
        return min(2 ** max(retries - 1, 0), 8)
    return 0


def find_unblocked_candidate(current_task_id: str):
    state_dir = root / '.agent' / 'state' / 'tasks'
    if not state_dir.exists():
        return 'none'

    candidates = []
    for path in sorted(state_dir.glob('*.json')):
        task = json.loads(path.read_text(encoding='utf-8'))
        if task.get('taskId') == current_task_id:
            continue
        if task.get('override') == 'force-hold':
            continue
        if task.get('status') not in {'todo', 'doing'}:
            continue
        candidates.append(task)

    if not candidates:
        return 'none'

    priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    candidates.sort(key=lambda t: (priority_order.get(t.get('priority', 'P2'), 9), 0 if t.get('status') == 'doing' else 1, t.get('updatedAt', '9999-99-99 99:99 Asia/Shanghai')))
    return candidates[0].get('taskId', 'none')


def main():
    parser = argparse.ArgumentParser(description='Evaluate retry / reorder / rollback signal for task loop.')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--stop-type', required=True)
    parser.add_argument('--reason', required=True)
    parser.add_argument('--manual-priority-lock', choices=['true', 'false'], default='false')
    args = parser.parse_args()

    policy = json.loads((root / '.agent' / 'loop' / 'retry-policy.json').read_text(encoding='utf-8'))
    state_path = root / '.agent' / 'loop' / 'retry-state.json'
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding='utf-8'))
    else:
        state = {}

    item = state.get(args.task_id, {'retries': 0})
    action = 'no-retry'
    requires_rollback = False
    rollback_target = 'none'
    reorder_target = 'none'
    manual_priority_lock = args.manual_priority_lock == 'true'

    if args.stop_type in policy.get('retryOn', []) and item['retries'] < policy.get('maxRetries', 0):
        item['retries'] += 1
        action = 'retry-same-task'
    elif args.stop_type == 'anomaly-stop' and item['retries'] >= policy.get('maxRetries', 0):
        action = 'reorder-next-task'
        if policy.get('preferUnblocked', False) and not manual_priority_lock:
            reorder_target = find_unblocked_candidate(args.task_id)
    elif args.stop_type == 'risk-stop':
        action = 'wait-human'
    elif args.stop_type == 'stage-complete-stop':
        action = 'advance-after-human'

    if 'rollback' in args.reason.lower():
        requires_rollback = True
        rollback_target = args.task_id

    task_state = load_task_state(args.task_id)
    backoff_delay = compute_backoff_delay(item.get('retries', 0), policy.get('backoffMode', 'none')) if action == 'retry-same-task' else 0

    item['lastStopType'] = args.stop_type
    item['lastReason'] = args.reason
    item['action'] = action
    item['requiresRollback'] = requires_rollback
    item['rollbackTarget'] = rollback_target
    item['backoffMode'] = policy.get('backoffMode', 'none')
    item['backoffDelaySteps'] = backoff_delay
    item['manualPriorityLock'] = manual_priority_lock
    item['reorderTarget'] = reorder_target
    item['preferUnblocked'] = policy.get('preferUnblocked', False)
    item['taskPriority'] = task_state.get('priority', 'unknown')
    item['taskStatus'] = task_state.get('status', 'unknown')
    state[args.task_id] = item
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = ['# RETRY_REORDER_RESULT', '', '## summary']
    lines.append(f'- taskId: {args.task_id}')
    lines.append(f'- stopType: {args.stop_type}')
    lines.append(f'- action: {action}')
    lines.append(f'- retries: {item["retries"]}')
    lines.append(f'- backoffMode: {item["backoffMode"]}')
    lines.append(f'- backoffDelaySteps: {item["backoffDelaySteps"]}')
    lines.append(f'- manualPriorityLock: {str(manual_priority_lock).lower()}')
    lines.append(f'- reorderTarget: {reorder_target}')
    lines.append(f'- preferUnblocked: {str(item["preferUnblocked"]).lower()}')
    lines.append(f'- requiresRollback: {str(requires_rollback).lower()}')
    lines.append(f'- rollbackTarget: {rollback_target}')
    out = root / 'tests' / 'RETRY_REORDER_RESULT.md'
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {state_path}')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
