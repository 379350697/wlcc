#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
state = root / '.agent' / 'loop' / 'retry-state.json'
if state.exists():
    state.unlink()

cases = [
    ('retry-1', ['--task-id','task-phase2-demo','--stop-type','anomaly-stop','--reason','check failure'], {'action': 'retry-same-task', 'backoffDelaySteps': 1}),
    ('retry-2', ['--task-id','task-phase2-demo','--stop-type','anomaly-stop','--reason','check failure'], {'action': 'retry-same-task', 'backoffDelaySteps': 2}),
    ('reorder-promote-unblocked', ['--task-id','task-phase2-demo','--stop-type','anomaly-stop','--reason','check failure'], {'action': 'reorder-next-task', 'reorderTarget': 'task-001'}),
    ('reorder-manual-lock', ['--task-id','task-phase2-demo','--stop-type','anomaly-stop','--reason','check failure','--manual-priority-lock','true'], {'action': 'reorder-next-task', 'manualPriorityLock': True, 'reorderTarget': 'none'}),
]
failed = []
lines = ['# RETRY_REORDER_TEST_RESULT', '']
for name, args, expected in cases:
    res = subprocess.run(['python3', str(root/'scripts'/'evaluate_retry_reorder.py'), *args], capture_output=True, text=True)
    data = json.loads(state.read_text(encoding='utf-8')) if state.exists() else {}
    item = data.get('task-phase2-demo', {})
    ok = res.returncode == 0
    for key, value in expected.items():
        if item.get(key) != value:
            ok = False
            break
    lines.append(f'## {name}')
    lines.append(f"- action: {item.get('action', 'MISSING')}")
    lines.append(f"- backoffDelaySteps: {item.get('backoffDelaySteps', 'MISSING')}")
    lines.append(f"- manualPriorityLock: {str(item.get('manualPriorityLock', 'MISSING')).lower()}")
    lines.append(f"- reorderTarget: {item.get('reorderTarget', 'MISSING')}")
    lines.append(f"- result: {'PASS' if ok else 'FAIL'}")
    lines.append('')
    if not ok:
        failed.append(name)
lines.append('## Overall')
lines.append(f"- {'PASS' if not failed else 'FAIL: ' + ', '.join(failed)}")
out = root / 'tests' / 'RETRY_REORDER_TEST_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(0 if not failed else 1)
