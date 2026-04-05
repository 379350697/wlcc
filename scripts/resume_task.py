#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


def read_if_exists(path: Path):
    if path.exists():
        return path.read_text(encoding='utf-8').strip()
    return 'MISSING'


def extract_field(text: str, prefix: str):
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.replace(prefix, '').strip()
    return 'MISSING'


def tail_lines(text: str, count: int = 12):
    lines = text.splitlines()
    return '\n'.join(lines[-count:]) if lines else 'MISSING'


def main():
    parser = argparse.ArgumentParser(description='Resume a task from canonical state first, markdown views second.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id', required=True)
    args = parser.parse_args()

    root = Path(args.project_root)
    retriever = root / 'scripts' / 'retrieve_context.py'
    context_output = root / 'tests' / 'RETRIEVE_CONTEXT_OUTPUT.json'
    if retriever.exists():
        subprocess.run([
            'python3', str(retriever),
            '--project-root', str(root),
            '--task-id', args.task_id,
        ], check=False)

    task_view = read_if_exists(root / '.agent' / 'tasks' / f'{args.task_id}.md')
    resume_view = read_if_exists(root / '.agent' / 'resume' / f'{args.task_id}-resume.md')
    tasks_view = read_if_exists(root / 'TASKS.md')
    next_task_state = read_if_exists(root / '.agent' / 'state' / 'next-task.json')
    next_task_view = read_if_exists(root / '.agent' / 'NEXT_TASK.md')
    changelog = read_if_exists(root / '.agent' / 'logs' / 'CHANGELOG.md')
    event_log = read_if_exists(root / '.agent' / 'logs' / 'EVENT_LOG.md')
    retrieved_context = read_if_exists(context_output)

    task_state_json = read_if_exists(root / '.agent' / 'state' / 'tasks' / f'{args.task_id}.json')
    summary_source = 'state-json'
    if task_state_json != 'MISSING':
        parsed = json.loads(task_state_json)
        goal = parsed.get('goal', 'MISSING')
        status = parsed.get('status', 'MISSING')
        blocker = parsed.get('blocker', 'MISSING')
        next_step = parsed.get('nextStep', 'MISSING')
        last_success = parsed.get('lastSuccess', 'MISSING')
        last_failure = parsed.get('lastFailure', 'MISSING')
    else:
        summary_source = 'markdown-view-fallback'
        goal = extract_field(task_view, '- goal: ')
        status = extract_field(task_view, '- status: ')
        blocker = extract_field(task_view, '- blocker: ')
        next_step = extract_field(task_view, '- nextStep: ')
        last_success = extract_field(resume_view, '- 最后成功动作：')
        last_failure = extract_field(resume_view, '- 最后失败动作：')

    out = [
        '# RESUME_OUTPUT',
        '',
        '## structured_summary',
        f'- summary_source: {summary_source}',
        f'- goal: {goal}',
        f'- status: {status}',
        f'- blocker: {blocker}',
        f'- next_step: {next_step}',
        f'- last_success: {last_success}',
        f'- last_failure: {last_failure}',
        '',
        '## recent_events',
        '### changelog_tail',
        tail_lines(changelog),
        '',
        '### event_log_tail',
        tail_lines(event_log),
        '',
        '## retrieved_context',
        retrieved_context,
        '',
        '## task_state_json',
        task_state_json,
        '',
        '## task_view',
        task_view,
        '',
        '## resume_view',
        resume_view,
        '',
        '## tasks_view',
        tasks_view,
        '',
        '## next_task_state',
        next_task_state,
        '',
        '## next_task_view',
        next_task_view,
    ]
    result_path = root / 'tests' / f'{args.task_id}-resume-output.md'
    result_path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'OK: wrote {result_path}')


if __name__ == '__main__':
    main()
