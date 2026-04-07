import json
from pathlib import Path

from runtime.events.bus import clear_runtime_event_bus, get_runtime_events
from runtime.evidence.ledger import load_evidence_entries
from runtime.supervision.core import handle_supervision_trigger, judge_progress, save_json


def make_task(root: Path, task_id: str = 'stall-task', **overrides) -> dict:
    task_path = root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
    task_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'taskId': task_id,
        'kind': 'real',
        'lifecycle': 'active',
        'latestResult': 'still working on a concrete step',
        'nextStep': 'continue with current leaf task',
        'blocker': 'none',
        'supervisionState': 'active',
        'phase': 'implement',
        'turnCount': 1,
        'testsRun': [],
    }
    payload.update(overrides)
    save_json(task_path, payload)
    return json.loads(task_path.read_text(encoding='utf-8'))


def setup_function():
    clear_runtime_event_bus()


def teardown_function():
    clear_runtime_event_bus()


def test_judge_progress_rejects_weak_progress_when_turn_advances_without_delta(tmp_path: Path):
    task = make_task(tmp_path, turnCount=2)

    verdict = judge_progress(
        task,
        tmp_path,
        {
            'lastEvidenceCount': 0,
            'lastTestsCount': 0,
            'lastPhase': 'implement',
            'lastTurnCount': 1,
        },
    )

    assert verdict['allowed'] is False
    assert verdict['reason'] == 'weak-progress'


def test_interval_escalates_after_repeated_no_progress(tmp_path: Path):
    task = make_task(tmp_path, turnCount=1)
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
            'weakProgressCount': 1,
        },
    )

    supervision = handle_supervision_trigger(tmp_path, task['taskId'], 'on_interval')

    assert supervision['status'] == 'resume-prepared'
    assert supervision['blockReason'] == 'weak-progress'
    assert supervision['lastFailureDecision']['failure_class'] == 'weak_progress'
    assert get_runtime_events()[-1].payload['failureClass'] == 'weak_progress'
    evidence = load_evidence_entries(tmp_path, task['taskId'], {'weak-progress'})
    assert evidence
    assert evidence[0]['type'] == 'weak-progress'


def test_interval_resets_weak_progress_counter_when_evidence_changes(tmp_path: Path):
    task = make_task(tmp_path, turnCount=1)
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
            'weakProgressCount': 1,
        },
    )
    evidence_path = tmp_path / '.agent' / 'state' / 'evidence' / f"{task['taskId']}.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        json.dumps(
            {
                'taskId': task['taskId'],
                'version': 1,
                'updatedAt': '2026-04-07T10:00:00',
                'entries': [
                    {
                        'evidenceType': 'content',
                        'source': 'test',
                        'summary': 'new evidence',
                        'details': {},
                        'recordedAt': '2026-04-07T10:00:00',
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )

    supervision = handle_supervision_trigger(tmp_path, task['taskId'], 'on_interval')

    assert supervision['status'] == 'active'
    assert supervision['weakProgressCount'] == 0
