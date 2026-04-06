#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'INGEST_REAL_TASK_TEST_RESULT.md'
issues = []

res = subprocess.run([
    'python3', str(root / 'scripts' / 'ingest_real_task.py'),
    '--title', '真实任务接管机制层 P0 启动任务',
    '--goal', '验证真实任务可一跳接入 runtime，并自动生成 state/view/next-task/resume。',
    '--source', 'user-directive',
    '--priority', 'P0',
    '--owner-context', 'discord-direct',
    '--execution-mode', 'live'
], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('ingest_real_task.py failed')

state_path = root / '.agent' / 'state' / 'tasks' / 'real-真实任务接管机制层-p0-启动任务.json'
if not state_path.exists():
    issues.append('missing ingested canonical task')
else:
    data = json.loads(state_path.read_text(encoding='utf-8'))
    for key in ['kind', 'source', 'executionMode', 'ownerContext', 'supervisionState', 'eligibleForScheduling', 'isPrimaryTrack', 'lifecycle']:
        if key not in data:
            issues.append(f'missing field: {key}')
    if data.get('kind') != 'real':
        issues.append('kind should be real')

supervision_path = root / '.agent' / 'state' / 'supervision' / 'real-真实任务接管机制层-p0-启动任务.json'
if not supervision_path.exists():
    issues.append('missing supervision state')

resume_out = root / 'tests' / 'real-真实任务接管机制层-p0-启动任务-resume-output.md'
if not resume_out.exists():
    issues.append('missing resume output for ingested task')

lines = ['# INGEST_REAL_TASK_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
