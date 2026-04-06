#!/usr/bin/env python3
from pathlib import Path
import subprocess


root = Path(__file__).resolve().parent.parent

render_views = root / 'scripts' / 'render_state_views.py'
if render_views.exists():
    subprocess.run(['python3', str(render_views), '--project-root', str(root)], capture_output=True, text=True)

consistency = root / 'scripts' / 'check_state_view_consistency.py'
if consistency.exists():
    subprocess.run(['python3', str(consistency)], capture_output=True, text=True)

retrieval_priority = root / 'scripts' / 'check_retrieval_priority.py'
if retrieval_priority.exists():
    subprocess.run(['python3', str(retrieval_priority)], capture_output=True, text=True)

primary_task = 'task-001' if (root / '.agent' / 'state' / 'tasks' / 'task-001.json').exists() else 'real-close-runtime-final-target'
checks = {
    'canonical_state_task': root / '.agent' / 'state' / 'tasks' / f'{primary_task}.json',
    'state_index': root / '.agent' / 'state' / 'index.json',
    'next_task_v2_state': root / '.agent' / 'state' / 'next-task.json',
    'next_task_view': root / '.agent' / 'NEXT_TASK.md',
    'task_view': root / '.agent' / 'tasks' / f'{primary_task}.md',
    'resume_view': root / '.agent' / 'resume' / f'{primary_task}-resume.md',
    'tasks_view': root / 'TASKS.md',
    'state_view_consistency': root / 'tests' / 'STATE_VIEW_CONSISTENCY_RESULT.md',
    'risk_policy_script': root / 'scripts' / 'evaluate_risk_policy.py',
    'risk_gate_script': root / 'scripts' / 'check_risk_level.py',
    'retrieve_context_script': root / 'scripts' / 'retrieve_context.py',
    'read_context_entry': root / 'scripts' / 'read_project_context.py',
    'retrieval_priority_check': root / 'tests' / 'RETRIEVAL_PRIORITY_CHECK_RESULT.md',
}

content_assertions = {
    'state_view_consistency': [
        '## issues',
        '- none',
    ],
    'retrieval_priority_check': [
        '## summary',
        '- canonical_task_before_markdown: yes',
        '- canonical_next_before_markdown: yes',
        '## issues',
        '- none',
    ],
}

lines = ['# PHASE2_MAINLINE_CHECK', '']
missing = []
failed = []

for name, path in checks.items():
    if not path.exists():
        lines.append(f'- {name}: MISSING')
        missing.append(name)
        continue

    expected_tokens = content_assertions.get(name)
    if expected_tokens:
        text = path.read_text(encoding='utf-8')
        missing_tokens = [token for token in expected_tokens if token not in text]
        if missing_tokens:
            lines.append(f'- {name}: FAIL')
            failed.append(f"{name}: missing tokens -> {' | '.join(missing_tokens)}")
            continue

    lines.append(f'- {name}: PASS')

lines.append('')
lines.append('## Overall')
if missing or failed:
    parts = []
    if missing:
        parts.append('missing=' + ', '.join(missing))
    if failed:
        parts.append('failed=' + ', '.join(failed))
    lines.append('- FAIL: ' + ' | '.join(parts))
    code = 1
else:
    lines.append('- PASS')
    code = 0

out = root / 'tests' / 'PHASE2_MAINLINE_CHECK_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
