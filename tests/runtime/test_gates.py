from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from runtime.gates.delivery import evaluate_delivery_gate
from runtime.gates.progress import evaluate_progress_gate
from runtime.gates.risk import evaluate_risk


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

    result = evaluate_delivery_gate(task_id, 'README.md', tmp_path, 'sample')
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

    result = evaluate_delivery_gate(task_id, 'README.md', tmp_path, 'sample')
    assert result['passed'] is True
    assert any(item['type'] == 'heartbeat-fresh' for item in result['evidence'])


def test_progress_gate_rejects_circular_and_short_text():
    result = evaluate_progress_gate('ok', 'ok')
    assert result['passed'] is False
    assert result['violations']


def test_risk_policy_evaluates():
    result = evaluate_risk('write-state', 'project', {'userApproved': False, 'requiresConfirmation': False})
    assert 'riskLevel' in result
    assert 'decision' in result
