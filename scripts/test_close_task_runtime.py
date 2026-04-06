#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'CLOSE_TASK_RUNTIME_TEST_RESULT.md'
issues = []

# create dedicated close target
subprocess.run([
    'python3', str(root / 'scripts' / 'ingest_real_task.py'),
    '--title', 'close runtime final target',
    '--goal', '验证 close_task_runtime 收口链。',
    '--source', 'close-test',
    '--priority', 'P1',
    '--owner-context', 'test',
    '--execution-mode', 'live'
], capture_output=True, text=True)

task_id = 'real-close-runtime-final-target'
res = subprocess.run(['python3', str(root / 'scripts' / 'close_task_runtime.py'), '--task-id', task_id, '--final-result', '真实任务机制层 closure 已完成。'], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('close_task_runtime failed')

state = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
if not state.exists():
    issues.append('missing closed task state')
else:
    data = json.loads(state.read_text(encoding='utf-8'))
    if data.get('lifecycle') != 'archived':
        issues.append('task lifecycle not archived after close')
    if data.get('eligibleForScheduling') is not False:
        issues.append('eligibleForScheduling not disabled after archive')

closure = root / '.agent' / 'logs' / 'CLOSURE_NOTE.md'
if not closure.exists():
    issues.append('missing closure note')

result = root / 'tests' / 'CLOSE_TASK_RUNTIME_RESULT.md'
if not result.exists():
    issues.append('missing CLOSE_TASK_RUNTIME_RESULT.md')

lines = ['# CLOSE_TASK_RUNTIME_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
