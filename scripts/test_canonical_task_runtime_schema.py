#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'CANONICAL_TASK_RUNTIME_SCHEMA_TEST_RESULT.md'
issues = []

# write one real task and one demo task
for task_id, kind, exec_mode, eligible, primary, priority in [
    ('real-schema-check', 'real', 'live', 'true', 'true', 'P1'),
    ('demo-schema-check', 'demo', 'sample-only', 'false', 'false', 'P0'),
]:
    res = subprocess.run([
        'python3', str(root / 'scripts' / 'write_state_store.py'),
        '--project-root', str(root),
        '--task-id', task_id,
        '--project', root.name,
        '--goal', task_id,
        '--status', 'todo',
        '--priority', priority,
        '--dependencies', '[]',
        '--override', 'none',
        '--latest-result', 'init',
        '--blocker', '无',
        '--next-step', 'check',
        '--last-success', '无',
        '--last-failure', '无',
        '--updated-at', '2026-04-06 15:45 Asia/Shanghai',
        '--kind', kind,
        '--source', 'schema-test',
        '--execution-mode', exec_mode,
        '--owner-context', 'test',
        '--supervision-state', 'ingested',
        '--eligible-for-scheduling', eligible,
        '--is-primary-track', primary,
        '--lifecycle', 'ingested',
        '--title', task_id,
    ], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append(f'write_state_store failed for {task_id}')

state_path = root / '.agent' / 'state' / 'tasks' / 'real-schema-check.json'
if state_path.exists():
    data = json.loads(state_path.read_text(encoding='utf-8'))
    for key in ['kind','source','executionMode','ownerContext','supervisionState','eligibleForScheduling','isPrimaryTrack','lifecycle','title']:
        if key not in data:
            issues.append(f'missing field {key}')
else:
    issues.append('missing real-schema-check state')

input_path = root / 'tests' / 'TMP_SCHEMA_NEXT_INPUT.json'
output_path = root / 'tests' / 'TMP_SCHEMA_NEXT_OUTPUT.json'
input_path.write_text(json.dumps({'tasks': [
    json.loads((root / '.agent' / 'state' / 'tasks' / 'real-schema-check.json').read_text(encoding='utf-8')),
    json.loads((root / '.agent' / 'state' / 'tasks' / 'demo-schema-check.json').read_text(encoding='utf-8')),
]}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
res = subprocess.run(['python3', str(root / 'scripts' / 'decide_next_task_v2.py'), '--input', str(input_path), '--output', str(output_path)], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('decide_next_task_v2 failed for schema test')
else:
    decision = json.loads(output_path.read_text(encoding='utf-8'))
    if decision.get('nextTaskId') != 'real-schema-check':
        issues.append('scheduler did not prefer real primary task')

lines = ['# CANONICAL_TASK_RUNTIME_SCHEMA_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
