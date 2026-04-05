#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parent.parent
release_items = [
    'ARCHITECTURE_PLAN.md',
    'MIGRATION_PLAN.md',
    'ROLLBACK_PLAN.md',
    'README.md',
    'README_DEPLOY.md',
    'TASKS.md',
    'STATUS.md',
    'DECISIONS.md',
    'INCIDENTS.md',
    'TEST_RESULTS.md',
    'FINAL_DELIVERY_SUMMARY.md',
    'REPO_PUBLISH_CHECKLIST.md',
    'skills',
    'dist',
    'scripts',
    '.agent/audit',
    '.agent/logs',
    '.agent/tasks',
    '.agent/resume',
    'memory',
    'tests',
]

lines = ['# RELEASE_MANIFEST', '']
for item in release_items:
    path = root / item
    lines.append(f'- {item}: {"PASS" if path.exists() else "MISSING"}')

out = root / 'RELEASE_MANIFEST.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
