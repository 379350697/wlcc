#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path

PRIORITY_ORDER = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
STATUS_ORDER = {'doing': 0, 'todo': 1, 'blocked': 2, 'done': 3}


def parse_time(text: str):
    text = text.replace(' Asia/Shanghai', '')
    return datetime.strptime(text, '%Y-%m-%d %H:%M')


def normalize_task(task, done_ids):
    priority = task.get('priority', 'P2')
    dependencies = task.get('dependencies', [])
    override = task.get('override', 'none')
    kind = task.get('kind', 'sample')
    execution_mode = task.get('executionMode', 'sample-only')
    eligible = task.get('eligibleForScheduling', False)
    primary = task.get('isPrimaryTrack', False)
    dependency_satisfied = all(dep in done_ids for dep in dependencies)
    runnable = task['status'] in {'doing', 'todo'} and dependency_satisfied and override != 'force-hold' and eligible
    forced = override == 'force-run'
    return {
        **task,
        'priority': priority,
        'dependencies': dependencies,
        'override': override,
        'kind': kind,
        'executionMode': execution_mode,
        'eligibleForScheduling': eligible,
        'isPrimaryTrack': primary,
        'dependencySatisfied': dependency_satisfied,
        'isRunnable': runnable,
        'isForced': forced,
    }


def choose(tasks):
    done_ids = {t['taskId'] for t in tasks if t['status'] == 'done'}
    normalized = [normalize_task(t, done_ids) for t in tasks]

    force_run = [t for t in normalized if t['override'] == 'force-run']
    if force_run:
        selected = sorted(force_run, key=lambda t: (PRIORITY_ORDER[t['priority']], parse_time(t['updatedAt'])), reverse=False)[0]
        return {
            'decisionType': 'force-override',
            'nextTaskId': selected['taskId'],
            'selectedPriority': selected['priority'],
            'dependencyStatus': 'satisfied' if selected['dependencySatisfied'] else 'unsatisfied',
            'overrideStatus': 'force-run',
            'reason': '存在 force-run 覆盖任务。',
            'nextAction': '直接执行覆盖任务。',
            'currentTask': selected['taskId'],
            'currentStatus': selected['status'],
        }

    active = [
        t for t in normalized
        if t['status'] != 'done'
        and t['override'] != 'force-hold'
        and t.get('eligibleForScheduling', False)
        and t.get('executionMode', 'sample-only') != 'sample-only'
    ]
    if not active:
        return {
            'decisionType': 'done-no-next', 'nextTaskId': 'none', 'selectedPriority': 'none',
            'dependencyStatus': 'none', 'overrideStatus': 'none', 'reason': '无可选任务。',
            'nextAction': '当前阶段完成。', 'currentTask': 'none', 'currentStatus': 'done'
        }

    sorted_active = sorted(active, key=lambda t: (0 if t.get('kind') == 'real' else 1, 0 if t.get('isPrimaryTrack') else 1, PRIORITY_ORDER[t['priority']], STATUS_ORDER[t['status']], -parse_time(t['updatedAt']).timestamp()))
    top = sorted_active[0]

    if not top['dependencySatisfied']:
        return {
            'decisionType': 'wait-dependency',
            'nextTaskId': top['taskId'],
            'selectedPriority': top['priority'],
            'dependencyStatus': 'unsatisfied',
            'overrideStatus': top['override'],
            'reason': '最高优先任务依赖未满足。',
            'nextAction': '先满足依赖任务。',
            'currentTask': top['taskId'],
            'currentStatus': top['status'],
        }

    if top['status'] == 'doing':
        decision = 'continue-current'
        action = '继续执行当前优先任务。'
    elif top['status'] == 'todo':
        decision = 'switch-next'
        action = '切换到下一优先任务。'
    else:
        decision = 'blocked'
        action = '等待阻塞解除。'

    return {
        'decisionType': decision,
        'nextTaskId': top['taskId'],
        'selectedPriority': top['priority'],
        'dependencyStatus': 'satisfied',
        'overrideStatus': top['override'],
        'reason': '按 priority/status/updatedAt 选出最高优先任务。',
        'nextAction': action,
        'currentTask': top['taskId'],
        'currentStatus': top['status'],
    }


def main():
    parser = argparse.ArgumentParser(description='Decide next task with priority/dependency/override support.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    tasks = json.loads(Path(args.input).read_text(encoding='utf-8'))['tasks']
    result = choose(tasks)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('OK')


if __name__ == '__main__':
    main()
