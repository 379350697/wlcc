#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def read_text(path: Path):
    return path.read_text(encoding='utf-8').strip() if path.exists() else None


def main():
    parser = argparse.ArgumentParser(description='Retrieve context with explicit source priority.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id', required=True)
    args = parser.parse_args()

    root = Path(args.project_root)

    fact_sources = [
        root / 'README.md',
        root / 'STATUS.md',
        root / 'DECISIONS.md',
        root / 'TASKS.md',
        root / 'INCIDENTS.md',
    ]
    task_state_sources = [
        root / '.agent' / 'state' / 'tasks' / f'{args.task_id}.json',
        root / '.agent' / 'tasks' / f'{args.task_id}.md',
        root / '.agent' / 'resume' / f'{args.task_id}-resume.md',
        root / '.agent' / 'state' / 'next-task.json',
        root / '.agent' / 'NEXT_TASK.md',
    ]
    summary_sources = [
        root / 'memory' / 'session' / 'SESSION_SUMMARY.md',
        root / 'FINAL_DELIVERY_SUMMARY.md',
    ]

    used = []
    degraded = False
    result = {
        'facts': [],
        'task_state': [],
        'summary': [],
        'chat': [],
    }

    for path in fact_sources:
        content = read_text(path)
        if content:
            result['facts'].append({'source': str(path.relative_to(root)), 'content': content[:300]})
            used.append(str(path.relative_to(root)))

    canonical_found = False
    markdown_fallback_used = False
    for path in task_state_sources:
        content = read_text(path)
        if content:
            if path.suffix == '.json':
                parsed = json.loads(content)
                result['task_state'].append({'source': str(path.relative_to(root)), 'content': parsed})
                canonical_found = True
            else:
                result['task_state'].append({'source': str(path.relative_to(root)), 'content': content[:300]})
                markdown_fallback_used = True
            used.append(str(path.relative_to(root)))

    if not canonical_found and markdown_fallback_used:
        degraded = True

    for path in summary_sources:
        content = read_text(path)
        if content:
            result['summary'].append({'source': str(path.relative_to(root)), 'content': content[:300]})
            used.append(str(path.relative_to(root)))

    result['meta'] = {
        'priority': ['facts', 'task_state', 'summary', 'chat'],
        'usedSources': used,
        'degradedFallback': degraded,
    }

    out = root / 'tests' / 'RETRIEVE_CONTEXT_OUTPUT.json'
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
