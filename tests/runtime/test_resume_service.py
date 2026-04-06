import json
from pathlib import Path

from runtime.resume.service import (
    build_resume_state_payload,
    collect_context_payload,
    resume_real_task_flow,
    resume_task_payload,
)
from runtime.supervision.core import save_json


def seed_task(root: Path, task_id: str = 'demo-task'):
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
    save_json(root / '.agent' / 'state' / 'next-task.json', {'nextTaskId': task_id, 'currentTask': task_id})
    save_json(root / '.agent' / 'loop' / 'last-run.json', {'steps': [{'taskId': task_id, 'step': 1}]})
    (root / 'README.md').write_text('demo readme', encoding='utf-8')
    (root / 'TASKS.md').write_text('# TASKS', encoding='utf-8')
    (root / '.agent' / 'tasks').mkdir(parents=True, exist_ok=True)
    (root / '.agent' / 'resume').mkdir(parents=True, exist_ok=True)
    (root / '.agent' / 'logs').mkdir(parents=True, exist_ok=True)
    (root / '.agent' / 'tasks' / f'{task_id}.md').write_text('# Task State\n- goal: demo goal', encoding='utf-8')
    (root / '.agent' / 'resume' / f'{task_id}-resume.md').write_text('# Resume State\n- 最后成功动作：did x', encoding='utf-8')
    (root / '.agent' / 'logs' / 'CHANGELOG.md').write_text('a\nb', encoding='utf-8')
    (root / '.agent' / 'logs' / 'EVENT_LOG.md').write_text('e1\ne2', encoding='utf-8')


def test_collect_context_payload_prioritizes_task_state(tmp_path: Path):
    seed_task(tmp_path)
    payload = collect_context_payload(tmp_path, 'demo-task')
    assert payload['meta']['taskKind'] == 'real'
    assert any(item['source'].endswith('demo-task.json') for item in payload['task_state'])


def test_build_resume_state_payload_selects_next_task(tmp_path: Path):
    seed_task(tmp_path)
    payload = build_resume_state_payload(tmp_path, ['demo-task'])
    assert payload['selectedTaskId'] == 'demo-task'


def test_resume_task_payload_uses_state_json(tmp_path: Path):
    seed_task(tmp_path)
    payload = resume_task_payload(tmp_path, 'demo-task')
    assert payload['structured_summary']['summary_source'] == 'state-json'
    assert payload['structured_summary']['goal'] == 'demo goal'
    assert payload['retrieved_context']['meta']['packageVersion'] == 1
    assert payload['runtime_meta']['contextBudgetChars'] > 0
    assert payload['runtime_meta']['contextTrimmed'] in (True, False)


def test_collect_context_payload_falls_back_when_task_state_json_is_invalid(tmp_path: Path):
    task_id = 'demo-task'
    (tmp_path / '.agent' / 'state' / 'tasks').mkdir(parents=True, exist_ok=True)
    (tmp_path / '.agent' / 'tasks').mkdir(parents=True, exist_ok=True)
    (tmp_path / '.agent' / 'state' / 'tasks' / f'{task_id}.json').write_text('{bad json', encoding='utf-8')
    (tmp_path / '.agent' / 'tasks' / f'{task_id}.md').write_text('# Task State\n- goal: markdown fallback', encoding='utf-8')

    payload = collect_context_payload(tmp_path, task_id)
    assert payload['meta']['degradedFallback'] is True
    assert payload['task_state'][0]['source'].endswith(f'{task_id}.md')
    assert payload['task_state'][0]['content'].startswith('# Task State')


def test_resume_real_task_flow_accepts_bare_real_task_id(tmp_path: Path):
    seed_task(tmp_path, 'real-demo-task')
    result = resume_real_task_flow(tmp_path, 'demo-task')

    assert result['task']['taskId'] == 'real-demo-task'
    assert result['task']['lifecycle'] == 'active'
    assert result['supervision']['lastResumeAt']
