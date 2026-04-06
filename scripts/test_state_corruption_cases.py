#!/usr/bin/env python3
import json
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'STATE_CORRUPTION_CASES_RESULT.md'
issues = []

# broken next-task state should be detectable by downstream read/consistency chain
next_task = root / '.agent' / 'state' / 'next-task.json'
backup = root / '.agent' / 'state' / 'next-task.json.bak-corrupt'
if next_task.exists():
    shutil.copy2(next_task, backup)
    next_task.write_text('{broken json\n', encoding='utf-8')
    res = subprocess.run(['python3', str(root / 'scripts' / 'retrieve_context.py'), '--project-root', str(root), '--task-id', 'demo-long-chain-autonomy'], capture_output=True, text=True)
    if res.returncode == 0:
        issues.append('retrieve_context unexpectedly succeeded with broken next-task json')
    shutil.copy2(backup, next_task)
    backup.unlink(missing_ok=True)
else:
    issues.append('missing next-task.json for corruption case')

# broken heartbeat history should fail summary build
hist = root / '.agent' / 'heartbeat' / 'heartbeat-history.json'
backup2 = root / '.agent' / 'heartbeat' / 'heartbeat-history.json.bak-corrupt'
if hist.exists():
    shutil.copy2(hist, backup2)
    hist.write_text('{broken json\n', encoding='utf-8')
    res = subprocess.run(['python3', str(root / 'scripts' / 'build_heartbeat_summary.py')], capture_output=True, text=True)
    if res.returncode == 0:
        issues.append('build_heartbeat_summary unexpectedly succeeded with broken heartbeat history')
    shutil.copy2(backup2, hist)
    backup2.unlink(missing_ok=True)
else:
    issues.append('missing heartbeat-history.json for corruption case')

lines = ['# STATE_CORRUPTION_CASES_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
