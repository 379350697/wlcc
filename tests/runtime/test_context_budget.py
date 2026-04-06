import json
from pathlib import Path

from runtime.context.budget import DEFAULT_CONTEXT_BUDGET_CHARS, clip_text, estimate_serialized_chars
from runtime.context.package import collect_context_sources, package_context_payload
from runtime.supervision.core import save_json


def seed_context(root: Path, task_id: str = 'demo-task'):
    save_json(root / '.agent' / 'state' / 'tasks' / f'{task_id}.json', {
        'taskId': task_id,
        'kind': 'real',
        'goal': 'demo goal',
        'status': 'doing',
        'blocker': '无',
        'nextStep': 'continue',
        'lastSuccess': 'did x',
        'lastFailure': 'none',
        'override': 'none',
    })
    (root / 'README.md').write_text('readme fact', encoding='utf-8')
    (root / 'STATUS.md').write_text('status fact', encoding='utf-8')
    (root / 'TASKS.md').write_text('tasks fact', encoding='utf-8')
    (root / '.agent' / 'tasks').mkdir(parents=True, exist_ok=True)
    (root / '.agent' / 'resume').mkdir(parents=True, exist_ok=True)
    (root / '.agent' / 'tasks' / f'{task_id}.md').write_text('# Task State\n- goal: demo goal', encoding='utf-8')
    (root / '.agent' / 'resume' / f'{task_id}-resume.md').write_text('# Resume State\n- 最后成功动作：did x', encoding='utf-8')
    (root / 'memory').mkdir(parents=True, exist_ok=True)
    (root / 'memory' / 'session').mkdir(parents=True, exist_ok=True)
    (root / 'memory' / 'session' / 'SESSION_SUMMARY.md').write_text('S' * 1200, encoding='utf-8')
    (root / 'FINAL_DELIVERY_SUMMARY.md').write_text('F' * 1200, encoding='utf-8')
    save_json(root / '.agent' / 'state' / 'next-task.json', {'nextTaskId': task_id, 'currentTask': task_id})
    (root / '.agent' / 'NEXT_TASK.md').write_text('next task', encoding='utf-8')


def test_clip_text_is_deterministic():
    clipped, changed = clip_text('abcdefghijklmnopqrstuvwxyz', 20)
    assert clipped.endswith('[truncated]')
    assert changed is True


def test_package_context_preserves_canonical_task_state(tmp_path: Path):
    seed_context(tmp_path)
    raw = collect_context_sources(tmp_path, 'demo-task')
    package = package_context_payload(raw)

    assert package.payload['meta']['packageVersion'] == 1
    assert package.payload['meta']['contextBudgetChars'] == DEFAULT_CONTEXT_BUDGET_CHARS
    assert any(isinstance(item['content'], dict) for item in package.payload['task_state'])
    assert package.payload['task_state'][0]['content']['taskId'] == 'demo-task'
    assert package.payload['summary']
    assert estimate_serialized_chars(package.payload) == package.meta['packagedChars']


def test_package_context_trims_summary_before_canonical_state(tmp_path: Path):
    seed_context(tmp_path)
    raw = collect_context_sources(tmp_path, 'demo-task')
    raw['summary'].append({'source': 'extra-summary.md', 'content': 'x' * 5000})
    package = package_context_payload(raw, budget_chars=1200)

    assert package.payload['task_state'][0]['content']['taskId'] == 'demo-task'
    assert package.meta['contextTrimmed'] is True
    assert package.payload['meta']['contextBudgetExceeded'] is True
    assert all(len(item['content']) < 1200 for item in package.payload['summary'] if isinstance(item['content'], str))


def test_collect_context_sources_falls_back_when_task_state_json_is_invalid(tmp_path: Path):
    task_id = 'demo-task'
    (tmp_path / '.agent' / 'state' / 'tasks').mkdir(parents=True, exist_ok=True)
    (tmp_path / '.agent' / 'tasks').mkdir(parents=True, exist_ok=True)
    (tmp_path / '.agent' / 'state' / 'tasks' / f'{task_id}.json').write_text('{bad json', encoding='utf-8')
    (tmp_path / '.agent' / 'tasks' / f'{task_id}.md').write_text('# Task State\n- goal: markdown fallback', encoding='utf-8')

    payload = collect_context_sources(tmp_path, task_id)

    assert payload['meta']['degradedFallback'] is True
    assert payload['task_state']
    assert payload['task_state'][0]['source'].endswith(f'{task_id}.md')
    assert payload['task_state'][0]['content'].startswith('# Task State')
