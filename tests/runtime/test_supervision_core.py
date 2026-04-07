import json
from pathlib import Path

from runtime.events.bus import clear_runtime_event_bus, get_runtime_events, subscribe_runtime_events
from runtime.evidence.ledger import load_evidence_entries
from runtime.supervision.core import handle_supervision_trigger, judge_progress, save_json


def make_task(root: Path, task_id: str = 'demo-task', **overrides):
    task_path = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
    task_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'taskId': task_id,
        'kind': 'real',
        'lifecycle': 'active',
        'latestResult': 'implemented substantial change',
        'nextStep': 'continue',
        'blocker': 'none',
        'supervisionState': 'active',
        'phase': 'implement',
        'turnCount': 0,
        'testsRun': [],
    }
    payload.update(overrides)
    save_json(task_path, payload)
    return json.loads(task_path.read_text(encoding='utf-8'))


def setup_function():
    clear_runtime_event_bus()


def teardown_function():
    clear_runtime_event_bus()


def test_judge_rejects_empty_latest_result(tmp_path: Path):
    task = {'taskId': 'demo', 'latestResult': '', 'blocker': 'none', 'nextStep': 'continue'}
    verdict = judge_progress(task, tmp_path)
    assert verdict['allowed'] is False
    assert verdict['reason'] == 'empty-latest-result'


def test_handle_supervision_on_interval_writes_state_and_evidence(tmp_path: Path):
    task = make_task(tmp_path)
    supervision = handle_supervision_trigger(tmp_path, task['taskId'], 'on_interval')
    supervision_path = tmp_path / '.agent' / 'state' / 'supervision' / f"{task['taskId']}.json"
    assert supervision_path.exists()
    assert supervision['status'] == 'active' or 'status' in supervision
    evidence = load_evidence_entries(tmp_path, task['taskId'], {'heartbeat-fresh'})
    assert evidence
    assert evidence[0]['type'] == 'heartbeat-fresh'


def test_handle_supervision_on_interval_records_stale_evidence(tmp_path: Path):
    task = make_task(tmp_path, lifecycle='blocked')
    supervision = handle_supervision_trigger(tmp_path, task['taskId'], 'on_interval')
    assert supervision['stale'] is True
    evidence = load_evidence_entries(tmp_path, task['taskId'], {'heartbeat-stale'})
    assert evidence
    assert evidence[0]['type'] == 'heartbeat-stale'


def test_supervision_emits_events_for_ingest_and_completion(tmp_path: Path, monkeypatch):
    task = make_task(tmp_path)
    seen = []
    subscribe_runtime_events(lambda event: seen.append(event.event_type))

    monkeypatch.setattr('runtime.supervision.core.run_handoff', lambda root, task: None)

    handle_supervision_trigger(tmp_path, task['taskId'], 'on_task_ingested')
    handle_supervision_trigger(tmp_path, task['taskId'], 'on_completion')

    assert 'supervision.task_ingested' in seen
    assert 'supervision.completion_handoff' in seen
    assert any(event.event_type == 'supervision.completion_handoff' for event in get_runtime_events())
    evidence = load_evidence_entries(tmp_path, task['taskId'], {'heartbeat-fresh', 'handoff-emitted'})
    assert {item['type'] for item in evidence} == {'heartbeat-fresh', 'handoff-emitted'}


def test_supervision_marks_weak_progress_and_emits_failure_class(tmp_path: Path):
    task = make_task(tmp_path, turnCount=2, phase='implement')
    supervision_path = tmp_path / '.agent' / 'state' / 'supervision' / f"{task['taskId']}.json"
    save_json(
        supervision_path,
        {
            'taskId': task['taskId'],
            'status': 'active',
            'lastEvidenceCount': 0,
            'lastTestsCount': 0,
            'lastPhase': 'implement',
            'lastTurnCount': 1,
            'weakProgressCount': 0,
        },
    )

    try:
        handle_supervision_trigger(tmp_path, task['taskId'], 'on_task_changed')
    except SystemExit:
        pass

    supervision = json.loads(supervision_path.read_text(encoding='utf-8'))
    assert supervision['status'] == 'resume-prepared'
    assert supervision['blockReason'] == 'weak-progress'
    event = get_runtime_events()[-1]
    assert event.event_type == 'supervision.task_changed'
    assert event.payload['failureClass'] == 'weak_progress'
