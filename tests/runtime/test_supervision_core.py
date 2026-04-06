import json
from pathlib import Path

from runtime.supervision.core import handle_supervision_trigger, judge_progress, save_json


def make_task(root: Path, task_id: str = 'demo-task'):
    task_path = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
    task_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(task_path, {
        'taskId': task_id,
        'kind': 'real',
        'lifecycle': 'active',
        'latestResult': 'implemented substantial change',
        'nextStep': 'continue',
        'blocker': 'none',
        'supervisionState': 'active',
    })
    return json.loads(task_path.read_text(encoding='utf-8'))


def test_judge_rejects_empty_latest_result(tmp_path: Path):
    task = {'taskId': 'demo', 'latestResult': '', 'blocker': 'none', 'nextStep': 'continue'}
    verdict = judge_progress(task, tmp_path)
    assert verdict['allowed'] is False
    assert verdict['reason'] == 'empty-latest-result'


def test_handle_supervision_on_interval_writes_state(tmp_path: Path):
    task = make_task(tmp_path)
    supervision = handle_supervision_trigger(tmp_path, task['taskId'], 'on_interval')
    supervision_path = tmp_path / '.agent' / 'state' / 'supervision' / f"{task['taskId']}.json"
    assert supervision_path.exists()
    assert supervision['status'] == 'active' or 'status' in supervision
