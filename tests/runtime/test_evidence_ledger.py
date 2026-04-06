from __future__ import annotations

import json
from pathlib import Path

from runtime.common.models import EvidenceRecord
from runtime.evidence.ledger import (
    append_evidence_record,
    evidence_ledger_path,
    load_evidence_entries,
    load_evidence_ledger,
    record_task_evidence,
)


def test_evidence_ledger_persists_compact_entries(tmp_path: Path):
    task_id = 'task-ledger'
    ledger = record_task_evidence(
        tmp_path,
        task_id,
        'content',
        'unit-test',
        'x' * 1000,
        {
            'payload': 'y' * 1000,
            'nested': {'message': 'z' * 1000},
            'items': list(range(20)),
        },
    )

    path = evidence_ledger_path(tmp_path, task_id)
    assert path == tmp_path / '.agent' / 'state' / 'evidence' / f'{task_id}.json'
    assert path.exists()

    payload = json.loads(path.read_text(encoding='utf-8'))
    assert payload['taskId'] == task_id
    assert payload['version'] == 1
    assert len(payload['entries']) == 1
    assert len(payload['entries'][0]['summary']) <= 240
    assert payload['entries'][0]['details']['payload'].endswith('...')
    assert payload['entries'][0]['details']['items'][-1] == '... [truncated]'

    loaded = load_evidence_ledger(tmp_path, task_id)
    assert loaded is not None
    assert loaded.taskId == task_id
    assert len(loaded.entries) == 1
    assert loaded.entries[0].summary == payload['entries'][0]['summary']
    assert ledger.updatedAt == loaded.updatedAt


def test_evidence_ledger_deduplicates_and_filters(tmp_path: Path):
    task_id = 'task-ledger-filter'
    record = EvidenceRecord(
        evidenceType='heartbeat-fresh',
        source='supervision.handle_supervision_trigger',
        summary='heartbeat emitted',
        details={'status': 'active'},
    )

    append_evidence_record(tmp_path, task_id, record)
    append_evidence_record(tmp_path, task_id, record)
    append_evidence_record(
        tmp_path,
        task_id,
        {
            'evidenceType': 'handoff-emitted',
            'source': 'supervision.handle_supervision_trigger',
            'summary': 'handoff prepared',
            'details': {'nextStep': 'close-task-runtime'},
        },
    )

    entries = load_evidence_entries(tmp_path, task_id, {'heartbeat-fresh'})
    assert len(entries) == 1
    assert entries[0]['type'] == 'heartbeat-fresh'

    ledger = load_evidence_ledger(tmp_path, task_id)
    assert ledger is not None
    assert len(ledger.entries) == 2
