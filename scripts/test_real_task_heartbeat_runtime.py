#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'REAL_TASK_HEARTBEAT_RUNTIME_RESULT.md'
issues = []

res = subprocess.run([
    'python3', str(root / 'scripts' / 'progress_task_runtime.py'),
    '--task-id', 'real-task-runtime-mainline',
    '--latest-result', 'Task 5.1 heartbeat 已接入正式 runtime。',
    '--next-step', '继续推进 supervisor logs。',
    '--blocker', '无',
    '--status', 'doing',
    '--lifecycle', 'active',
], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('progress_task_runtime failed for heartbeat runtime case')

summary_path = root / '.agent' / 'heartbeat' / 'heartbeat-summary.json'
latest_path = root / '.agent' / 'heartbeat' / 'latest-heartbeat.json'
if not summary_path.exists():
    issues.append('missing heartbeat-summary.json')
else:
    data = json.loads(summary_path.read_text(encoding='utf-8'))
    latest = data.get('latest', {})
    if latest.get('currentTask') != 'real-task-runtime-mainline':
        issues.append('heartbeat summary latest currentTask not switched to real runtime mainline')

if not latest_path.exists():
    issues.append('missing latest-heartbeat.json')
else:
    latest = json.loads(latest_path.read_text(encoding='utf-8'))
    if latest.get('currentTask') != 'real-task-runtime-mainline':
        issues.append('latest heartbeat currentTask not real-task-runtime-mainline')

lines = ['# REAL_TASK_HEARTBEAT_RUNTIME_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
