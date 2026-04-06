#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'EMPTY_DIRTY_OBSERVABILITY_CASES_RESULT.md'
issues = []

# empty event log should still allow overview build
log = root / '.agent' / 'logs' / 'EVENT_LOG.md'
backup = root / '.agent' / 'logs' / 'EVENT_LOG.md.bak-empty'
if log.exists():
    shutil.copy2(log, backup)
    log.write_text('# EVENT_LOG\n\n', encoding='utf-8')
    res = subprocess.run(['python3', str(root / 'scripts' / 'build_observability_dashboard.py')], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append('observability build failed on empty event log')
    shutil.copy2(backup, log)
    backup.unlink(missing_ok=True)
else:
    issues.append('missing event log for empty case')

lines = ['# EMPTY_DIRTY_OBSERVABILITY_CASES_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
