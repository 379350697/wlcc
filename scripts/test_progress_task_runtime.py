#!/usr/bin/env python3
import json
import subprocess
from uuid import uuid4
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'PROGRESS_TASK_RUNTIME_TEST_RESULT.md'
issues = []
task_id = f"real-progress-runtime-target-{uuid4().hex[:8]}"

res = subprocess.run([
    'python3', str(root / 'scripts' / 'ingest_real_task.py'),
    '--title', 'progress runtime target',
    '--goal', '验证结构化 progress runtime。',
    '--source', 'progress-test',
    '--priority', 'P1',
    '--owner-context', 'test',
    '--execution-mode', 'live',
    '--task-id', task_id,
], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('ingest_real_task for progress target failed')

bad = subprocess.run([
    'python3', str(root / 'scripts' / 'progress_task_runtime.py'),
    '--task-id', task_id,
    '--latest-result', 'Task 3.1 已进入统一推进入口验证。',
    '--next-step', '继续推进 Task 3.2 resume_real_task.py。',
    '--blocker', '无',
    '--status', 'doing',
    '--lifecycle', 'active',
], capture_output=True, text=True)
if bad.returncode == 0:
    issues.append('progress_task_runtime should reject evidence-free progress')

res = subprocess.run([
    'python3', str(root / 'scripts' / 'progress_task_runtime.py'),
    '--task-id', task_id,
    '--latest-result', 'Task 3.1 已进入统一推进入口验证，并记录 state-update。',
    '--next-step', '继续推进 Task 3.2 resume_real_task.py。',
    '--blocker', '无',
    '--status', 'doing',
    '--lifecycle', 'active',
    '--phase', 'verify',
    '--evidence-id', 'state-update',
    '--changed-file', 'scripts/progress_task_runtime.py',
], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('progress_task_runtime failed')

state = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
if not state.exists():
    issues.append('missing real-progress-runtime-target state')
else:
    data = json.loads(state.read_text(encoding='utf-8'))
    if data.get('latestResult') != 'Task 3.1 已进入统一推进入口验证，并记录 state-update。':
        issues.append('latestResult not updated')
    if data.get('nextStep') != '继续推进 Task 3.2 resume_real_task.py。':
        issues.append('nextStep not updated')
    if data.get('phase') != 'verify':
        issues.append('phase not updated')
    if data.get('evidenceIds') != ['state-update']:
        issues.append('evidenceIds not updated')
    if data.get('changedFiles') != ['scripts/progress_task_runtime.py']:
        issues.append('changedFiles not updated')

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
