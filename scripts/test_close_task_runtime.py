#!/usr/bin/env python3
import json
import subprocess
from uuid import uuid4
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'CLOSE_TASK_RUNTIME_TEST_RESULT.md'
issues = []
task_id = f"real-close-runtime-final-target-{uuid4().hex[:8]}"

# create dedicated close target
subprocess.run([
    'python3', str(root / 'scripts' / 'ingest_real_task.py'),
    '--title', 'close runtime final target',
    '--goal', '验证 close_task_runtime 收口链。',
    '--source', 'close-test',
    '--priority', 'P1',
    '--owner-context', 'test',
    '--execution-mode', 'live',
    '--task-id', task_id,
], capture_output=True, text=True)

fail = subprocess.run(['python3', str(root / 'scripts' / 'close_task_runtime.py'), '--task-id', task_id, '--final-result', '真实任务机制层 closure 已完成。'], capture_output=True, text=True)
if fail.returncode == 0:
    issues.append('close_task_runtime should reject incomplete task contract')

progress = subprocess.run([
    'python3', str(root / 'scripts' / 'progress_task_runtime.py'),
    '--task-id', task_id,
    '--latest-result', 'scripts/close_task_runtime.py close runtime target 已补齐 final-result / gap-check / status-update / state-update 并进入 verify。',
    '--next-step', '执行 close_task_runtime 收口。',
    '--blocker', '无',
    '--status', 'verify',
    '--phase', 'verify',
    '--evidence-id', 'state-update',
    '--evidence-id', 'final-result',
    '--evidence-id', 'gap-check',
    '--evidence-id', 'status-update',
    '--changed-file', 'scripts/close_task_runtime.py',
], capture_output=True, text=True)
if progress.returncode != 0:
    issues.append('progress_task_runtime for close target failed')

res = subprocess.run(['python3', str(root / 'scripts' / 'close_task_runtime.py'), '--task-id', task_id, '--final-result', '真实任务机制层 closure 已完成。'], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('close_task_runtime failed after valid progress')

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
