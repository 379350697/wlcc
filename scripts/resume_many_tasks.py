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


def log_event(root: Path, time_text: str, target: str, result: str, note: str):
    log_script = root / 'scripts' / 'log_event.py'
    if not log_script.exists():
        return
    subprocess.run([
        'python3', str(log_script),
        '--project-root', str(root),
        '--time', time_text,
        '--type', 'bulk-resume',
        '--target', target,
        '--result', result,
        '--note', note,
    ], check=False)


def main():
    parser = argparse.ArgumentParser(description='Resume multiple tasks from canonical state first, markdown views second.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-ids', nargs='+', required=True)
    parser.add_argument('--time', default='2026-04-05 21:06 Asia/Shanghai')
    args = parser.parse_args()

    root = Path(args.project_root)
    next_task_state = read_if_exists(root / '.agent' / 'state' / 'next-task.json')
    next_task_view = read_if_exists(root / '.agent' / 'NEXT_TASK.md')
    out = ['# BULK_RESUME_OUTPUT', '']
    retriever = root / 'scripts' / 'retrieve_context.py'
    context_output = root / 'tests' / 'RETRIEVE_CONTEXT_OUTPUT.json'

    bulk_resume_state_output = root / '.agent' / 'state' / 'bulk-resume-state.json'
    build_resume_state = root / 'scripts' / 'build_resume_state.py'
    if build_resume_state.exists():
        subprocess.run([
            'python3', str(build_resume_state),
            '--task-ids', *args.task_ids,
            '--output', str(bulk_resume_state_output),
        ], check=False)
    bulk_resume_state = read_if_exists(bulk_resume_state_output)
    for task_id in args.task_ids:
        if retriever.exists():
            subprocess.run([
                'python3', str(retriever),
                '--project-root', str(root),
                '--task-id', task_id,
            ], check=False)
        retrieved_context = read_if_exists(context_output)
        task_state_json = read_if_exists(root / '.agent' / 'state' / 'tasks' / f'{task_id}.json')
        task_view = read_if_exists(root / '.agent' / 'tasks' / f'{task_id}.md')
        resume_view = read_if_exists(root / '.agent' / 'resume' / f'{task_id}-resume.md')
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

        out.append(f'## {task_id}')
        out.append('### structured_summary')
        out.append(f'- summary_source: {summary_source}')
        out.append(f'- goal: {goal}')
        out.append(f'- status: {status}')
        out.append(f'- blocker: {blocker}')
        out.append(f'- next_step: {next_step}')
        out.append(f'- last_success: {last_success}')
        out.append(f'- last_failure: {last_failure}')
        out.append('')
        out.append('### retrieved_context')
        out.append(retrieved_context)
        out.append('')
        out.append('### task_state_json')
        out.append(task_state_json)
        out.append('')
        out.append('### task_view')
        out.append(task_view)
        out.append('')
        out.append('### resume_view')
        out.append(resume_view)
        out.append('')
        log_event(root, args.time, task_id, 'success', 'bulk resume output generated')
    out.append('## bulk_resume_state')
    out.append(bulk_resume_state)
    out.append('')
    out.append('## next_task_state')
    out.append(next_task_state)
    out.append('')
    out.append('## next_task_view')
    out.append(next_task_view)
    path = root / 'tests' / 'BULK_RESUME_OUTPUT.md'
    path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'OK: wrote {path}')


if __name__ == '__main__':
    main()
