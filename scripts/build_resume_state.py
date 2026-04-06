#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def choose_resume_target(task_ids, next_task_state, last_run):
    candidates = []
    next_task_id = next_task_state.get('nextTaskId')
    current_task = next_task_state.get('currentTask')

    for task_id in task_ids:
        task_path = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
        if not task_path.exists():
            continue
        task = json.loads(task_path.read_text(encoding='utf-8'))
        score = 0
        reasons = []
        if task_id == next_task_id:
            score += 100
            reasons.append('matches-next-task')
        if task_id == current_task:
            score += 90
            reasons.append('matches-current-task')
        if task.get('status') == 'doing':
            score += 50
            reasons.append('status-doing')
        elif task.get('status') == 'todo':
            score += 20
            reasons.append('status-todo')
        elif task.get('status') == 'blocked':
            score += 5
            reasons.append('status-blocked')
        if task.get('override') == 'force-run':
            score += 40
            reasons.append('override-force-run')
        if task.get('override') == 'force-hold':
            score -= 100
            reasons.append('override-force-hold')
        candidates.append({'taskId': task_id, 'score': score, 'reasons': reasons, 'task': task})

    candidates.sort(key=lambda item: item['score'], reverse=True)
    selected = candidates[0] if candidates else None

    last_step = last_run.get('steps', [])[-1] if last_run.get('steps') else {}
    loop_resume = {
        'lastTaskId': last_step.get('taskId', 'none'),
        'lastStep': last_step.get('step', 0),
        'decisionType': last_step.get('decisionType', 'none'),
        'stopType': last_step.get('stopType', 'none'),
        'stopReason': last_step.get('stopReason', 'none'),
        'riskEscalation': last_step.get('riskEscalation', 'none'),
        'failureControl': last_step.get('failureControl', 'none'),
    }

    return {
        'selectedTaskId': selected['taskId'] if selected else 'none',
        'selectionReasons': selected['reasons'] if selected else ['no-candidate'],
        'candidateCount': len(candidates),
        'conflictPolicy': {
            'priority': ['next-task', 'current-task', 'doing', 'override', 'todo', 'blocked'],
            'selectedBy': 'score-based-priority',
        },
        'loopResume': loop_resume,
        'candidates': [
            {
                'taskId': item['taskId'],
                'score': item['score'],
                'reasons': item['reasons'],
            }
            for item in candidates
        ],
    }


def main():
    parser = argparse.ArgumentParser(description='Build multi-session resume state with conflict resolution.')
    parser.add_argument('--task-ids', nargs='+', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    next_task_state = read_json(root / '.agent' / 'state' / 'next-task.json', {})
    last_run = read_json(root / '.agent' / 'loop' / 'last-run.json', {})
    result = choose_resume_target(args.task_ids, next_task_state, last_run)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'OK: wrote {output}')


if __name__ == '__main__':
    main()
