#!/usr/bin/env python3
import json
from pathlib import Path


root = Path(__file__).resolve().parent.parent
state_dir = root / '.agent' / 'state' / 'tasks'
issues = []
all_tasks = []

for path in sorted(state_dir.glob('*.json')):
    task = json.loads(path.read_text(encoding='utf-8'))
    all_tasks.append(task)
    task_id = task['taskId']
    task_md = root / '.agent' / 'tasks' / f'{task_id}.md'
    resume_md = root / '.agent' / 'resume' / f'{task_id}-resume.md'

    if not task_md.exists():
        issues.append(f'{task_id}: missing task markdown view')
    else:
        text = task_md.read_text(encoding='utf-8')
        if f"- goal: {task['goal']}" not in text:
            issues.append(f'{task_id}: task goal mismatch')
        if f"- status: {task['status']}" not in text:
            issues.append(f'{task_id}: task status mismatch')
        if f"- priority: {task['priority']}" not in text:
            issues.append(f'{task_id}: task priority mismatch')

    if not resume_md.exists():
        issues.append(f'{task_id}: missing resume markdown view')
    else:
        text = resume_md.read_text(encoding='utf-8')
        if f"- 最后目标：{task['goal']}" not in text:
            issues.append(f'{task_id}: resume goal mismatch')
        if f"- 最后成功动作：{task['lastSuccess']}" not in text:
            issues.append(f'{task_id}: resume lastSuccess mismatch')
        if f"- 最后失败动作：{task['lastFailure']}" not in text:
            issues.append(f'{task_id}: resume lastFailure mismatch')


tasks_view = root / 'TASKS.md'
if not tasks_view.exists():
    issues.append('TASKS.md: missing tasks summary view')
else:
    tasks_text = tasks_view.read_text(encoding='utf-8')
    for task in all_tasks:
        if f"### {task['taskId']}" not in tasks_text:
            issues.append(f"{task['taskId']}: TASKS view missing section")
        if f"- 目标：{task['goal']}" not in tasks_text:
            issues.append(f"{task['taskId']}: TASKS goal mismatch")
        if f"- 当前状态：{task['status']}" not in tasks_text:
            issues.append(f"{task['taskId']}: TASKS status mismatch")
        if f"- 优先级：{task['priority']}" not in tasks_text:
            issues.append(f"{task['taskId']}: TASKS priority mismatch")
        if f"- 阻塞项：{task['blocker']}" not in tasks_text:
            issues.append(f"{task['taskId']}: TASKS blocker mismatch")
        if f"- 下一步：{task['nextStep']}" not in tasks_text:
            issues.append(f"{task['taskId']}: TASKS nextStep mismatch")
        if f"- 最近结果：{task['latestResult']}" not in tasks_text:
            issues.append(f"{task['taskId']}: TASKS latestResult mismatch")

lines = ['# STATE_VIEW_CONSISTENCY', '']
if not issues:
    lines.append('## summary')
    lines.append(f'- task_count: {len(all_tasks)}')
    lines.append(f"- tasks_view_checked: {'yes' if tasks_view.exists() else 'no'}")
    lines.append('')
lines.append('## issues')
if issues:
    lines.extend(f'- {issue}' for issue in issues)
    code = 1
else:
    lines.append('- none')
    code = 0

out = root / 'tests' / 'STATE_VIEW_CONSISTENCY_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
