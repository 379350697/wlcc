#!/usr/bin/env python3
import json
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
issues = []

# 1. state / retrieval consistency
for script in ['check_state_view_consistency.py', 'check_retrieval_priority.py']:
    res = subprocess.run(['python3', str(root / 'scripts' / script)], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append(f'{script} failed')

# 2. degraded retrieval fallback simulation
state_json = root / '.agent' / 'state' / 'tasks' / 'local-task-001.json'
backup = root / '.agent' / 'state' / 'tasks' / 'local-task-001.json.bak-demo'
if state_json.exists():
    shutil.copy2(state_json, backup)
    state_json.unlink()
    res = subprocess.run(['python3', str(root / 'scripts' / 'retrieve_context.py'), '--project-root', str(root), '--task-id', 'local-task-001'], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append('retrieve_context degraded case failed to run')
    else:
        out = json.loads((root / 'tests' / 'RETRIEVE_CONTEXT_OUTPUT.json').read_text(encoding='utf-8'))
        sources = [item['source'] for item in out.get('task_state', [])]
        if '.agent/tasks/local-task-001.md' not in sources:
            issues.append('markdown fallback source missing when canonical state removed')
    shutil.copy2(backup, state_json)
    backup.unlink(missing_ok=True)
else:
    issues.append('missing local-task-001 canonical state for degraded case')

# 3. heartbeat edge triggers
for script in ['test_heartbeat_reporting.py', 'test_heartbeat_triggers.py']:
    res = subprocess.run(['python3', str(root / 'scripts' / script)], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append(f'{script} failed')

lines = ['# DEMO_EXTREME_CASES_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out = root / 'tests' / 'DEMO_EXTREME_CASES_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
