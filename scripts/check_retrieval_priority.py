#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path


root = Path(__file__).resolve().parent.parent
path = root / 'tests' / 'RETRIEVE_CONTEXT_NORMAL_OUTPUT.json'
issues = []

retriever = root / 'scripts' / 'retrieve_context.py'
if retriever.exists():
    run = subprocess.run([
        'python3', str(retriever),
        '--project-root', str(root),
        '--task-id', 'task-001',
    ], capture_output=True, text=True)
    if run.returncode != 0:
        issues.append('retrieve_context.py failed for fresh normal output')
    else:
        fresh = root / 'tests' / 'RETRIEVE_CONTEXT_OUTPUT.json'
        if fresh.exists():
            path.write_text(fresh.read_text(encoding='utf-8'), encoding='utf-8')
        else:
            issues.append('missing fresh RETRIEVE_CONTEXT_OUTPUT.json')
else:
    issues.append('missing retrieve_context.py')

if not path.exists():
    issues.append('missing RETRIEVE_CONTEXT_NORMAL_OUTPUT.json')
else:
    data = json.loads(path.read_text(encoding='utf-8'))
    sources = [item['source'] for item in data.get('task_state', [])]
    if '.agent/state/tasks/task-001.json' not in sources:
        issues.append('missing canonical task state source')
    if '.agent/tasks/task-001.md' not in sources:
        issues.append('missing markdown task state source')
    if '.agent/state/next-task.json' not in sources:
        issues.append('missing canonical next-task source')
    if '.agent/NEXT_TASK.md' not in sources:
        issues.append('missing markdown next-task source')

    used = data.get('meta', {}).get('usedSources', [])
    try:
        json_task_idx = used.index('.agent/state/tasks/task-001.json')
        md_task_idx = used.index('.agent/tasks/task-001.md')
        if json_task_idx > md_task_idx:
            issues.append('canonical task state not ordered before markdown')
    except ValueError:
        pass

    try:
        json_next_idx = used.index('.agent/state/next-task.json')
        md_next_idx = used.index('.agent/NEXT_TASK.md')
        if json_next_idx > md_next_idx:
            issues.append('canonical next-task not ordered before markdown')
    except ValueError:
        pass

    if data.get('meta', {}).get('degradedFallback') is True:
        issues.append('normal retrieval unexpectedly degraded')

lines = ['# RETRIEVAL_PRIORITY_CHECK', '']
lines.append('## summary')
if path.exists():
    data = json.loads(path.read_text(encoding='utf-8'))
    used = data.get('meta', {}).get('usedSources', [])
    lines.append(f"- canonical_task_before_markdown: {'yes' if '.agent/state/tasks/task-001.json' in used and '.agent/tasks/task-001.md' in used and used.index('.agent/state/tasks/task-001.json') < used.index('.agent/tasks/task-001.md') else 'no'}")
    lines.append(f"- canonical_next_before_markdown: {'yes' if '.agent/state/next-task.json' in used and '.agent/NEXT_TASK.md' in used and used.index('.agent/state/next-task.json') < used.index('.agent/NEXT_TASK.md') else 'no'}")
    lines.append(f"- degraded_fallback: {str(data.get('meta', {}).get('degradedFallback', 'unknown')).lower()}")
lines.append('')
lines.append('## issues')
if issues:
    lines.extend(f'- {issue}' for issue in issues)
    code = 1
else:
    lines.append('- none')
    code = 0

out = root / 'tests' / 'RETRIEVAL_PRIORITY_CHECK_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
