#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'TASK_SUPERVISION_TRIGGER_SPEC_TEST_RESULT.md'
issues = []

spec = root / 'TASK_SUPERVISION_TRIGGER_SPEC.md'
if not spec.exists():
    issues.append('missing TASK_SUPERVISION_TRIGGER_SPEC.md')
else:
    text = spec.read_text(encoding='utf-8')
    for token in ['on_task_ingested', 'on_task_changed', 'on_interruption_detected', 'on_interval', 'on_completion', '动作链', '输出', '失败策略']:
        if token not in text:
            issues.append(f'missing spec token: {token}')

lines = ['# TASK_SUPERVISION_TRIGGER_SPEC_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
