#!/usr/bin/env python3
import json
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'OWNERSHIP_AND_DIRTY_EVENT_CASES_RESULT.md'
issues = []

# ownership missing reviewer field should be detectable as malformed stored state
ownership = root / '.agent' / 'state' / 'ownership' / 'demo-long-chain-autonomy.json'
backup = root / '.agent' / 'state' / 'ownership' / 'demo-long-chain-autonomy.json.bak-own'
if ownership.exists():
    shutil.copy2(ownership, backup)
    data = json.loads(ownership.read_text(encoding='utf-8'))
    data.pop('reviewer', None)
    ownership.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    re = json.loads(ownership.read_text(encoding='utf-8'))
    if 'reviewer' in re:
        issues.append('ownership missing reviewer mutation not applied')
    shutil.copy2(backup, ownership)
    backup.unlink(missing_ok=True)
else:
    issues.append('missing ownership state for malformed case')

# dirty event log line should not break observability dashboard build
log = root / '.agent' / 'logs' / 'EVENT_LOG.md'
backup2 = root / '.agent' / 'logs' / 'EVENT_LOG.md.bak-dirty'
if log.exists():
    shutil.copy2(log, backup2)
    with log.open('a', encoding='utf-8') as f:
        f.write('\nTHIS IS A DIRTY LINE WITHOUT STRUCTURE\n')
    res = subprocess.run(['python3', str(root / 'scripts' / 'build_observability_dashboard.py')], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append('observability build failed on dirty event log line')
    shutil.copy2(backup2, log)
    backup2.unlink(missing_ok=True)
else:
    issues.append('missing event log for dirty line case')

lines = ['# OWNERSHIP_AND_DIRTY_EVENT_CASES_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
