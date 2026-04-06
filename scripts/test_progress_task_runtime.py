#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'PROGRESS_TASK_RUNTIME_TEST_RESULT.md'
issues = []
task_id = 'real-task-runtime-mainline' if (root / '.agent' / 'state' / 'tasks' / 'real-task-runtime-mainline.json').exists() else 'real-close-runtime-final-target'

res = subprocess.run([
    'python3', str(root / 'scripts' / 'progress_task_runtime.py'),
    '--task-id', task_id,
    '--latest-result', 'Task 3.1 已进入统一推进入口验证。',
    '--next-step', '继续推进 Task 3.2 resume_real_task.py。',
    '--blocker', '无',
    '--status', 'doing',
    '--lifecycle', 'active',
], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('progress_task_runtime failed')

state = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
if not state.exists():
    issues.append(f'missing {task_id} state')
else:
    data = json.loads(state.read_text(encoding='utf-8'))
    if data.get('latestResult') != 'Task 3.1 已进入统一推进入口验证。':
        issues.append('latestResult not updated')
    if data.get('nextStep') != '继续推进 Task 3.2 resume_real_task.py。':
        issues.append('nextStep not updated')

summary = root / 'tests' / 'PROGRESS_TASK_RUNTIME_RESULT.md'
if not summary.exists():
    issues.append('missing progress runtime summary')

lines = ['# PROGRESS_TASK_RUNTIME_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
