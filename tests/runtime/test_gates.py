from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from runtime.gates.delivery import evaluate_delivery_gate
from runtime.gates.progress import evaluate_progress_gate
from runtime.gates.risk import evaluate_risk
from runtime.evidence.ledger import append_evidence_record


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_delivery_gate_accepts_emitted_at(tmp_path: Path):
    task_id = 'task-1'
    _write_json(
        tmp_path / '.agent' / 'state' / 'tasks' / f'{task_id}.json',
        {
            'taskId': task_id,
            'goal': 'g',
            'status': 'doing',
            'priority': 'P2',
            'blocker': '无',
            'nextStep': 'next',
            'latestResult': 'done',
            'lastSuccess': 'x',
            'lastFailure': 'y',
            'updatedAt': '2026-04-06T00:00:00',
        },
    )
    hb_path = tmp_path / '.agent' / 'heartbeat' / 'latest-heartbeat.json'
    _write_json(
        hb_path,
        {
            'currentTask': task_id,
            'emittedAt': datetime.now(timezone.utc).isoformat(),
        },
    )

    result = evaluate_delivery_gate(task_id, 'ok', tmp_path, 'sample')
    assert result['passed'] is True
    assert any(item['type'] == 'heartbeat-fresh' for item in result['evidence'])


def test_delivery_gate_accepts_timestamp_fallback(tmp_path: Path):
    task_id = 'task-2'
    _write_json(
        tmp_path / '.agent' / 'state' / 'tasks' / f'{task_id}.json',
        {
            'taskId': task_id,
            'goal': 'g',
            'status': 'doing',
            'priority': 'P2',
            'blocker': '无',
            'nextStep': 'next',
            'latestResult': 'done',
            'lastSuccess': 'x',
            'lastFailure': 'y',
            'updatedAt': '2026-04-06T00:00:00',
        },
    )
    hb_path = tmp_path / '.agent' / 'heartbeat' / 'latest-heartbeat.json'
    _write_json(
        hb_path,
        {
            'currentTask': task_id,
            'timestamp': (datetime.now(timezone.utc) - timedelta(seconds=5)).isoformat(),
        },
    )

    result = evaluate_delivery_gate(task_id, 'ok', tmp_path, 'sample')
    assert result['passed'] is True
    assert any(item['type'] == 'heartbeat-fresh' for item in result['evidence'])


def test_progress_gate_rejects_circular_and_short_text():
    result = evaluate_progress_gate('ok', 'ok')
    assert result['passed'] is False
    assert result['violations']
    assert result['failureClass'] == 'content_weak'
    assert result['degradationAction'] == 'retry_same_step'


def test_risk_policy_evaluates():
    result = evaluate_risk('write-state', 'project', {'userApproved': False, 'requiresConfirmation': False})
    assert 'riskLevel' in result
    assert 'decision' in result
    assert 'failureClass' in result


def test_delivery_gate_exposes_structured_failure_fields(tmp_path: Path):
    task_id = 'task-3'
    _write_json(
        tmp_path / '.agent' / 'state' / 'tasks' / f'{task_id}.json',
        {
            'taskId': task_id,
            'goal': 'g',
            'status': 'doing',
            'priority': 'P2',
            'blocker': '无',
            'nextStep': 'next',
            'latestResult': 'done',
            'lastSuccess': 'x',
            'lastFailure': 'y',
            'updatedAt': '2026-04-06T00:00:00',
        },
    )

    result = evaluate_delivery_gate(task_id, 'README.md', tmp_path, 'sample')
    assert result['passed'] is True
    assert result['failureClass'] == 'none'
    assert result['degradationAction'] == 'accept'


def test_delivery_gate_ignores_stale_ledger_without_fresh_evidence(tmp_path: Path):
    task_id = 'task-ledger-delivery'
    _write_json(
        tmp_path / '.agent' / 'state' / 'tasks' / f'{task_id}.json',
        {
            'taskId': task_id,
            'goal': 'g',
            'status': 'doing',
            'priority': 'P2',
            'blocker': '无',
            'nextStep': 'next',
            'latestResult': '',
            'lastSuccess': 'x',
            'lastFailure': 'y',
            'updatedAt': '2026-04-06T00:00:00',
        },
    )
    append_evidence_record(
        tmp_path,
        task_id,
        {
            'evidenceType': 'content',
            'source': 'supervision.handle_supervision_trigger',
            'summary': 'progress is substantive',
            'details': {'status': 'active'},
        },
    )
    append_evidence_record(
        tmp_path,
        task_id,
        {
            'evidenceType': 'heartbeat-fresh',
            'source': 'supervision.handle_supervision_trigger',
            'summary': 'heartbeat emitted',
            'details': {'stale': False},
        },
    )

    result = evaluate_delivery_gate(task_id, '', tmp_path, 'real')
    assert result['passed'] is False
    assert result['collected'] == 0
    assert result['evidence'] == []


def test_delivery_gate_preserves_heartbeat_detail_fields(tmp_path: Path):
    task_id = 'task-4'
    _write_json(
        tmp_path / '.agent' / 'state' / 'tasks' / f'{task_id}.json',
        {
            'taskId': task_id,
            'goal': 'g',
            'status': 'doing',
            'priority': 'P2',
            'blocker': '无',
            'nextStep': 'next',
            'latestResult': 'done',
            'lastSuccess': 'x',
            'lastFailure': 'y',
            'updatedAt': '2026-04-06T00:00:00',
        },
    )
    (tmp_path / '.agent' / 'heartbeat').mkdir(parents=True, exist_ok=True)
    _write_json(
        tmp_path / '.agent' / 'heartbeat' / 'latest-heartbeat.json',
        {
            'currentTask': task_id,
            'emittedAt': datetime.now(timezone.utc).isoformat(),
        },
    )

    result = evaluate_delivery_gate(task_id, '', tmp_path, 'sample')
    assert result['passed'] is True
    assert result['evidence']
    assert any(item['type'] == 'heartbeat-fresh' and 'age_seconds' in item['details'] for item in result['evidence'])


def test_delivery_gate_counts_current_evidence_even_if_ledger_has_same_record(tmp_path: Path):
    task_id = 'task-dup-current'
    _write_json(
        tmp_path / '.agent' / 'state' / 'tasks' / f'{task_id}.json',
        {
            'taskId': task_id,
            'goal': 'g',
            'status': 'doing',
            'priority': 'P2',
            'blocker': '无',
            'nextStep': 'next',
            'latestResult': 'implemented substantial change',
            'lastSuccess': 'x',
            'lastFailure': 'y',
            'updatedAt': '2026-04-06T00:00:00',
        },
    )
    append_evidence_record(
        tmp_path,
        task_id,
        {
            'evidenceType': 'content',
            'source': 'delivery.evaluate_delivery_gate',
            'summary': 'latest_result is substantive',
            'details': {'detail': 'latest_result is substantive'},
        },
    )

    result = evaluate_delivery_gate(task_id, 'implemented substantial change', tmp_path, 'sample')
    assert result['passed'] is True
    assert result['collected'] == 1
    assert result['evidence'][0]['type'] == 'content'


def test_delivery_gate_preserves_file_change_detail_fields(tmp_path: Path):
    task_id = 'task-5'
    _write_json(
        tmp_path / '.agent' / 'state' / 'tasks' / f'{task_id}.json',
        {
            'taskId': task_id,
            'goal': 'g',
            'status': 'doing',
            'priority': 'P2',
            'blocker': '无',
            'nextStep': 'next',
            'latestResult': '',
            'lastSuccess': 'x',
            'lastFailure': 'y',
            'updatedAt': '2026-04-06T00:00:00',
        },
    )
    (tmp_path / 'tests').mkdir(parents=True, exist_ok=True)
    changed = tmp_path / 'tests' / 'changed.txt'
    changed.write_text('changed', encoding='utf-8')
    future = time.time() + 5
    os.utime(changed, (future, future))

    result = evaluate_delivery_gate(task_id, '', tmp_path, 'sample')
    assert result['passed'] is True
    assert result['evidence']
    assert any(item['type'] == 'file-changes' and item['details'].get('count', 0) >= 1 for item in result['evidence'])
