#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'INVALID_AND_OVERRIDE_CASES_RESULT.md'
issues = []

# 1. invalid status should fail
invalid = subprocess.run([
    'python3', str(root / 'scripts' / 'write_state_store.py'),
    '--project-root', str(root),
    '--task-id', 'invalid-demo-task',
    '--project', 'local-agent-system',
    '--goal', 'invalid status case',
    '--status', 'weird',
    '--priority', 'P1',
    '--dependencies', '[]',
    '--override', 'none',
    '--latest-result', 'none',
    '--blocker', 'none',
    '--next-step', 'none',
    '--last-success', 'none',
    '--last-failure', 'none',
    '--updated-at', '2026-04-06 14:05 Asia/Shanghai',
], capture_output=True, text=True)
if invalid.returncode == 0:
    issues.append('invalid status unexpectedly accepted')

# 2. force-run should win
input_path = root / 'tests' / 'TMP_OVERRIDE_INPUT.json'
output_path = root / 'tests' / 'TMP_OVERRIDE_OUTPUT.json'
input_path.write_text(json.dumps({'tasks': [
    {'taskId': 'demo-a', 'status': 'doing', 'priority': 'P1', 'dependencies': [], 'override': 'none', 'updatedAt': '2026-04-06 14:01 Asia/Shanghai'},
    {'taskId': 'demo-force', 'status': 'todo', 'priority': 'P3', 'dependencies': [], 'override': 'force-run', 'updatedAt': '2026-04-06 14:02 Asia/Shanghai'}
]}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
res = subprocess.run(['python3', str(root / 'scripts' / 'decide_next_task_v2.py'), '--input', str(input_path), '--output', str(output_path)], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('force-run next-task decision failed')
else:
    data = json.loads(output_path.read_text(encoding='utf-8'))
    if data.get('nextTaskId') != 'demo-force':
        issues.append('force-run task did not win scheduling')

# 3. dependency unsatisfied should wait
input_path_2 = root / 'tests' / 'TMP_DEP_INPUT.json'
output_path_2 = root / 'tests' / 'TMP_DEP_OUTPUT.json'
input_path_2.write_text(json.dumps({'tasks': [
    {'taskId': 'demo-dependent', 'status': 'todo', 'priority': 'P0', 'dependencies': ['demo-prereq'], 'override': 'none', 'updatedAt': '2026-04-06 14:03 Asia/Shanghai'},
    {'taskId': 'demo-prereq', 'status': 'todo', 'priority': 'P2', 'dependencies': [], 'override': 'force-hold', 'updatedAt': '2026-04-06 14:04 Asia/Shanghai'}
]}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
res = subprocess.run(['python3', str(root / 'scripts' / 'decide_next_task_v2.py'), '--input', str(input_path_2), '--output', str(output_path_2)], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('dependency wait decision failed')
else:
    data = json.loads(output_path_2.read_text(encoding='utf-8'))
    if data.get('decisionType') != 'wait-dependency':
        issues.append('dependency unsatisfied did not produce wait-dependency')

lines = ['# INVALID_AND_OVERRIDE_CASES_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
