#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'TASK_LIFECYCLE_TEST_RESULT.md'
issues = []

# create lifecycle test task in ingested state
subprocess.run([
    'python3', str(root / 'scripts' / 'write_state_store.py'),
    '--project-root', str(root),
    '--task-id', 'real-lifecycle-check',
    '--project', root.name,
    '--goal', 'lifecycle check',
    '--status', 'doing',
    '--priority', 'P0',
    '--dependencies', '[]',
    '--override', 'none',
    '--latest-result', 'created',
    '--blocker', '无',
    '--next-step', 'move active',
    '--last-success', 'created',
    '--last-failure', '无',
    '--updated-at', '2026-04-06 15:50 Asia/Shanghai',
    '--kind', 'real',
    '--source', 'lifecycle-test',
    '--execution-mode', 'live',
    '--owner-context', 'test',
    '--supervision-state', 'ingested',
    '--eligible-for-scheduling', 'true',
    '--is-primary-track', 'true',
    '--lifecycle', 'ingested',
    '--title', 'real-lifecycle-check',
], capture_output=True, text=True)

res = subprocess.run(['python3', str(root / 'scripts' / 'update_task_lifecycle.py'), '--task-id', 'real-lifecycle-check', '--to', 'active'], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('ingested -> active failed')
else:
    data = json.loads((root / '.agent' / 'state' / 'tasks' / 'real-lifecycle-check.json').read_text(encoding='utf-8'))
    if data.get('lifecycle') != 'active':
        issues.append('lifecycle not updated to active')
    if data.get('supervisionState') != 'active':
        issues.append('supervisionState not updated to active')

res = subprocess.run(['python3', str(root / 'scripts' / 'update_task_lifecycle.py'), '--task-id', 'real-lifecycle-check', '--to', 'archived'], capture_output=True, text=True)
if res.returncode == 0:
    issues.append('illegal active -> archived unexpectedly allowed')

lines = ['# TASK_LIFECYCLE_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
