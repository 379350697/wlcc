#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'TASK_LIFECYCLE_RUNTIME_INTEGRATION_RESULT.md'
issues = []

# ingest should auto-promote to active after initial runtime setup
res = subprocess.run([
    'python3', str(root / 'scripts' / 'ingest_real_task.py'),
    '--title', 'lifecycle runtime integration',
    '--goal', '验证 ingest 与 lifecycle 迁移逻辑已接通。',
    '--source', 'integration-test',
    '--priority', 'P0',
    '--owner-context', 'runtime-test',
    '--execution-mode', 'live'
], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('ingest_real_task failed in runtime integration test')

task_id = 'real-lifecycle-runtime-integration'
state_path = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
supervision_path = root / '.agent' / 'state' / 'supervision' / f'{task_id}.json'
if not state_path.exists():
    issues.append('missing runtime integration task state')
else:
    task = json.loads(state_path.read_text(encoding='utf-8'))
    if task.get('lifecycle') != 'active':
        issues.append('ingest did not advance lifecycle to active')
    if task.get('supervisionState') != 'active':
        issues.append('ingest did not advance supervisionState to active')

if not supervision_path.exists():
    issues.append('missing runtime integration supervision state')
else:
    supervision = json.loads(supervision_path.read_text(encoding='utf-8'))
    if supervision.get('status') != 'active':
        issues.append('supervision status not active after ingest runtime integration')

# active -> blocked -> active roundtrip
res = subprocess.run(['python3', str(root / 'scripts' / 'update_task_lifecycle.py'), '--task-id', task_id, '--to', 'blocked'], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('active -> blocked failed')
res = subprocess.run(['python3', str(root / 'scripts' / 'update_task_lifecycle.py'), '--task-id', task_id, '--to', 'active'], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('blocked -> active failed')

lines = ['# TASK_LIFECYCLE_RUNTIME_INTEGRATION_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
