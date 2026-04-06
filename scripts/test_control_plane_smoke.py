#!/usr/bin/env python3
"""Lightweight smoke test for the OpenClaw runtime control plane."""

from __future__ import annotations

import tempfile
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.actions.registry import get_action_meta
from runtime.context.package import collect_context_sources, package_context_payload
from runtime.evidence.ledger import append_evidence_record, load_evidence_entries
from runtime.events.bus import clear_runtime_event_bus, publish_runtime_event, subscribe_runtime_events
from runtime.failure.pipeline import route_failure
from runtime.supervision.core import save_json


def _seed_minimal_workspace(root: Path) -> None:
    save_json(
        root / '.agent' / 'state' / 'tasks' / 'smoke-task.json',
        {
            'taskId': 'smoke-task',
            'kind': 'real',
            'goal': 'smoke goal',
            'status': 'doing',
            'blocker': 'none',
            'nextStep': 'continue',
            'lastSuccess': 'did x',
            'lastFailure': 'none',
            'override': 'none',
        },
    )
    (root / 'README.md').write_text('smoke readme', encoding='utf-8')
    (root / 'TASKS.md').write_text('# TASKS\n- smoke task', encoding='utf-8')
    (root / '.agent' / 'tasks').mkdir(parents=True, exist_ok=True)
    (root / '.agent' / 'resume').mkdir(parents=True, exist_ok=True)
    (root / '.agent' / 'tasks' / 'smoke-task.md').write_text('# Task State\n- goal: smoke goal', encoding='utf-8')
    (root / '.agent' / 'resume' / 'smoke-task-resume.md').write_text(
        '# Resume State\n- 最后成功动作：did x',
        encoding='utf-8',
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        _seed_minimal_workspace(root)
        clear_runtime_event_bus()

        seen_events: list[str] = []
        subscribe_runtime_events(lambda event: seen_events.append(event.event_type))

        action_meta = get_action_meta('render_state_views')
        assert action_meta['read_only'] is True
        assert action_meta['concurrent_safe'] is True

        publish_runtime_event(
            'control_plane.smoke',
            'smoke-task',
            'probe',
            {'stage': 'event-bus'},
        )
        assert 'control_plane.smoke' in seen_events

        verdict = route_failure(
            'progress',
            {
                'passed': False,
                'reason': 'latest_result 太短（2 字符，最少 5）',
                'violations': [{'check': 'latest_result_length', 'passed': False}],
            },
        )
        assert verdict.failure_class == 'content_weak'
        assert verdict.decision == 'retry_same_step'

        raw_context = collect_context_sources(root, 'smoke-task')
        packaged = package_context_payload(raw_context, budget_chars=1000)
        assert packaged.payload['meta']['packageVersion'] == 1
        assert packaged.meta['contextBudgetChars'] == 1000

        append_evidence_record(
            root,
            'smoke-task',
            {
                'evidenceType': 'content',
                'source': 'scripts.test_control_plane_smoke',
                'summary': 'control plane smoke passed',
                'details': {'event': 'control_plane.smoke'},
            },
        )
        evidence = load_evidence_entries(root, 'smoke-task', {'content'})
        assert evidence
        assert evidence[0]['summary'] == 'control plane smoke passed'

    print('OK: control plane smoke passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
