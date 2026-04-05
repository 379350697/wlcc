#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
from pathlib import Path


def render_task_md(task: dict) -> str:
    return f"""# Task State

- id: {task['taskId']}
- project: {task['project']}
- goal: {task['goal']}
- status: {task['status']}
- priority: {task['priority']}
- dependencies: {', '.join(task['dependencies']) if task['dependencies'] else '[]'}
- override: {task['override']}
- latestResult: {task['latestResult']}
- blocker: {task['blocker']}
- nextStep: {task['nextStep']}
- updatedAt: {task['updatedAt']}
"""


def render_resume_md(task: dict) -> str:
    return f"""# Resume State

- taskId: {task['taskId']}
- 最后目标：{task['goal']}
- 最后成功动作：{task['lastSuccess']}
- 最后失败动作：{task['lastFailure']}
- 当前阻塞：{task['blocker']}
- 建议下一步：{task['nextStep']}
- updatedAt: {task['updatedAt']}
"""


def render_tasks_summary(tasks: list) -> str:
    active = [t for t in tasks if t['status'] != 'done']
    done = [t for t in tasks if t['status'] == 'done']
    lines = ['# TASKS', '', '## Active']
    for task in active:
        lines.extend([
            f"### {task['taskId']}",
            f"- 目标：{task['goal']}",
            f"- 当前状态：{task['status']}",
            f"- 优先级：{task['priority']}",
            f"- 阻塞项：{task['blocker']}",
            f"- 下一步：{task['nextStep']}",
            f"- 最近结果：{task['latestResult']}",
            ''
        ])
    lines.append('## Done')
    for task in done:
        lines.extend([
            f"### {task['taskId']}",
            f"- 目标：{task['goal']}",
            f"- 当前状态：{task['status']}",
            f"- 优先级：{task['priority']}",
            f"- 阻塞项：{task['blocker']}",
            f"- 下一步：{task['nextStep']}",
            f"- 最近结果：{task['latestResult']}",
            ''
        ])
    return '\n'.join(lines).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(description='Render markdown views from canonical state store.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id')
    args = parser.parse_args()

    root = Path(args.project_root)
    state_dir = root / '.agent' / 'state' / 'tasks'
    task_files = sorted(state_dir.glob('*.json'))
    if not task_files:
        raise SystemExit(f'missing state dir content: {state_dir}')

    out_dir = root / '.agent' / 'tasks'
    resume_dir = root / '.agent' / 'resume'
    out_dir.mkdir(parents=True, exist_ok=True)
    resume_dir.mkdir(parents=True, exist_ok=True)
    all_tasks = []
    for source in task_files:
        task = json.loads(source.read_text(encoding='utf-8'))
        all_tasks.append(task)
        if args.task_id and task['taskId'] != args.task_id:
            continue
        out_path = out_dir / f"{task['taskId']}.md"
        out_path.write_text(render_task_md(task), encoding='utf-8')
        print(f'OK: wrote {out_path}')
        resume_path = resume_dir / f"{task['taskId']}-resume.md"
        resume_path.write_text(render_resume_md(task), encoding='utf-8')
        print(f'OK: wrote {resume_path}')

    tasks_md = root / 'TASKS.md'
    tasks_md.write_text(render_tasks_summary(all_tasks), encoding='utf-8')
    print(f'OK: wrote {tasks_md}')


if __name__ == '__main__':
    main()
