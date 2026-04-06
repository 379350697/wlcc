#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def now_text():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def main():
    parser = argparse.ArgumentParser(description='Write ownership + handoff state for multi-agent workflow.')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--owner', default='unassigned')
    parser.add_argument('--executor', default='unassigned')
    parser.add_argument('--reviewer', default='unassigned')
    parser.add_argument('--from-agent', required=True)
    parser.add_argument('--to-agent', required=True)
    parser.add_argument('--reason', required=True)
    parser.add_argument('--summary', required=True)
    parser.add_argument('--next-action', required=True)
    parser.add_argument('--requires-human', action='store_true')
    parser.add_argument('--notes', default='none')
    args = parser.parse_args()

    updated_at = now_text()

    ownership_dir = root / '.agent' / 'state' / 'ownership'
    handoff_dir = root / '.agent' / 'state' / 'handoffs'
    render_dir = root / '.agent' / 'handoffs'
    ownership_dir.mkdir(parents=True, exist_ok=True)
    handoff_dir.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)

    resume_state_path = root / '.agent' / 'state' / f'{args.task_id}-resume-state.json'
    next_task_path = root / '.agent' / 'state' / 'next-task.json'

    ownership = {
        'taskId': args.task_id,
        'owner': args.owner,
        'executor': args.executor,
        'reviewer': args.reviewer,
        'updatedAt': updated_at,
        'notes': args.notes,
    }
    handoff = {
        'taskId': args.task_id,
        'fromAgent': args.from_agent,
        'toAgent': args.to_agent,
        'reason': args.reason,
        'summary': args.summary,
        'nextAction': args.next_action,
        'requiresHuman': args.requires_human,
        'linkedResumeState': str(resume_state_path.relative_to(root)) if resume_state_path.exists() else 'missing',
        'linkedNextTask': str(next_task_path.relative_to(root)) if next_task_path.exists() else 'missing',
        'updatedAt': updated_at,
    }

    ownership_path = ownership_dir / f'{args.task_id}.json'
    handoff_path = handoff_dir / f'{args.task_id}.json'
    render_path = render_dir / f'{args.task_id}.md'

    ownership_path.write_text(json.dumps(ownership, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    handoff_path.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = ['# HANDOFF_OUTPUT', '']
    lines.append('## ownership')
    lines.append(f'- taskId: {ownership["taskId"]}')
    lines.append(f'- owner: {ownership["owner"]}')
    lines.append(f'- executor: {ownership["executor"]}')
    lines.append(f'- reviewer: {ownership["reviewer"]}')
    lines.append(f'- updatedAt: {ownership["updatedAt"]}')
    lines.append('')
    lines.append('## handoff')
    lines.append(f'- fromAgent: {handoff["fromAgent"]}')
    lines.append(f'- toAgent: {handoff["toAgent"]}')
    lines.append(f'- reason: {handoff["reason"]}')
    lines.append(f'- summary: {handoff["summary"]}')
    lines.append(f'- nextAction: {handoff["nextAction"]}')
    lines.append(f'- requiresHuman: {str(handoff["requiresHuman"]).lower()}')
    lines.append(f'- linkedResumeState: {handoff["linkedResumeState"]}')
    lines.append(f'- linkedNextTask: {handoff["linkedNextTask"]}')
    render_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    tests_path = root / 'tests' / 'HANDOFF_OUTPUT.md'
    tests_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {ownership_path}')
    print(f'OK: wrote {handoff_path}')
    print(f'OK: wrote {render_path}')
    print(f'OK: wrote {tests_path}')


if __name__ == '__main__':
    main()
