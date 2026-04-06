#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'RESUME_REAL_TASK_TEST_RESULT.md'
issues = []
task_id = 'real-task-runtime-mainline' if (root / '.agent' / 'state' / 'tasks' / 'real-task-runtime-mainline.json').exists() else 'real-close-runtime-final-target'

# move task to blocked first, then ensure resume_real_task restores active flow
subprocess.run(['python3', str(root / 'scripts' / 'update_task_lifecycle.py'), '--task-id', task_id, '--to', 'blocked'], capture_output=True, text=True)
res = subprocess.run(['python3', str(root / 'scripts' / 'resume_real_task.py'), '--task-id', task_id], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('resume_real_task failed')

state_path = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
if state_path.exists():
    task = json.loads(state_path.read_text(encoding='utf-8'))
    if task.get('lifecycle') != 'active':
        issues.append('resume_real_task did not restore lifecycle to active')
else:
    issues.append(f'missing {task_id} state')

supervision_path = root / '.agent' / 'state' / 'supervision' / f'{task_id}.json'
if supervision_path.exists():
    supervision = json.loads(supervision_path.read_text(encoding='utf-8'))
    if not supervision.get('lastResumeAt'):
        issues.append('resume_real_task did not update lastResumeAt')
else:
    issues.append('missing supervision state')

resume_output = root / 'tests' / 'RESUME_REAL_TASK_RESULT.md'
if not resume_output.exists():
    issues.append('missing RESUME_REAL_TASK_RESULT.md')

lines = ['# RESUME_REAL_TASK_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
