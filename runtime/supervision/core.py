"""Online supervision core separated from sidecar reporting."""
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

from runtime.evidence.ledger import record_task_evidence
from runtime.events.bus import publish_runtime_event
from runtime.failure.pipeline import route_failure

from .heartbeat import emit_heartbeat_record

JUDGE_HEARTBEAT_THRESHOLD = 300


def now_text() -> str:
    return datetime.now().isoformat(timespec='seconds')


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def append_log(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(line + '\n')


def record_evidence(root: Path, task_id: str, evidence_type: str, summary: str, details: dict) -> None:
    record_task_evidence(
        root,
        task_id,
        evidence_type,
        'supervision.handle_supervision_trigger',
        summary,
        details,
    )


def task_paths(root: Path, task_id: str) -> dict:
    return {
        'task': root / '.agent' / 'state' / 'tasks' / f'{task_id}.json',
        'supervision': root / '.agent' / 'state' / 'supervision' / f'{task_id}.json',
        'handoff': root / '.agent' / 'state' / 'handoffs' / f'{task_id}.json',
    }


def get_latest_heartbeat_time(root: Path, task_id: str):
    hb_dir = root / '.agent' / 'heartbeat'
    if not hb_dir.exists():
        return None
    hb_files = sorted(hb_dir.glob('*.json'), key=lambda path: path.stat().st_mtime, reverse=True)
    if not hb_files:
        return None
    try:
        heartbeat = json.loads(hb_files[0].read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return None
    if isinstance(heartbeat, list):
        heartbeat = next(
            (item for item in reversed(heartbeat) if isinstance(item, dict) and item.get('currentTask') == task_id),
            None,
        )
    if not isinstance(heartbeat, dict):
        return None
    if heartbeat.get('currentTask') == task_id:
        return hb_files[0].stat().st_mtime
    return None


def judge_progress(task: dict, root: Path) -> dict:
    failed_checks = []
    latest = task.get('latestResult', '').strip()
    if not latest or len(latest) < 5:
        failed_checks.append('empty-latest-result')
    hb_time = get_latest_heartbeat_time(root, task['taskId'])
    if hb_time is not None:
        age = time.time() - hb_time
        if age > JUDGE_HEARTBEAT_THRESHOLD:
            failed_checks.append('stale-heartbeat')
    if failed_checks:
        return {'allowed': False, 'reason': failed_checks[0], 'checks': failed_checks}
    return {'allowed': True, 'reason': 'ok', 'checks': []}


def run_handoff(root: Path, task: dict):
    subprocess.run([
        'python3', str(root / 'scripts' / 'write_handoff_state.py'),
        '--task-id', task['taskId'],
        '--owner', task.get('ownerContext', 'unknown'),
        '--executor', 'coder',
        '--reviewer', 'reviewer',
        '--from-agent', 'coder',
        '--to-agent', 'reviewer',
        '--reason', 'supervision-handoff',
        '--summary', f"任务 {task['taskId']} 进入 handoff 监督阶段。",
        '--next-action', 'review-runtime-state',
        '--requires-human',
    ], check=True)


def handle_supervision_trigger(root: Path, task_id: str, trigger: str) -> dict:
    paths = task_paths(root, task_id)
    task = load_json(paths['task'], None)
    if not task:
        raise SystemExit(f'missing task: {task_id}')
    supervision = load_json(paths['supervision'], {'taskId': task_id})
    supervision['taskKind'] = task.get('kind', 'unknown')
    supervision['scope'] = 'real-task-first' if task.get('kind') == 'real' else 'sample-scope'
    supervisor_log = root / '.agent' / 'logs' / 'SUPERVISOR_ACTIONS_LOG.md'
    stalled_log = root / '.agent' / 'logs' / 'STALLED_TASK_LOG.md'
    missed_log = root / '.agent' / 'logs' / 'MISSED_HEARTBEAT_LOG.md'

    if trigger == 'on_task_ingested':
        supervision['status'] = 'active'
        supervision['lastHeartbeatAt'] = now_text()
        supervision['stale'] = False
        emit_heartbeat_record(root, {
            'stage': f"lifecycle-{task.get('lifecycle', 'unknown')}",
            'currentTask': task['taskId'],
            'nextStep': task.get('nextStep', 'continue-runtime'),
            'triggerReason': 'periodic-step',
            'riskOrBlocker': task.get('blocker', 'none'),
        }, throttle_seconds=0)
        record_evidence(
            root,
            task_id,
            'heartbeat-fresh',
            'heartbeat emitted on task ingest',
            {
                'trigger': trigger,
                'taskKind': supervision['taskKind'],
                'status': supervision['status'],
            },
        )
        publish_runtime_event(
            'supervision.task_ingested',
            task_id,
            'ingest',
            {'status': 'active', 'taskKind': supervision['taskKind']},
        )
        append_log(supervisor_log, f"- {now_text()} | task={task_id} | trigger=on_task_ingested | status=active")
    elif trigger == 'on_task_changed':
        verdict = judge_progress(task, root)
        supervision['lastVerdict'] = verdict
        if not verdict['allowed']:
            failure_verdict = route_failure('supervision', verdict)
            supervision['status'] = 'blocked-by-judge'
            supervision['blockReason'] = verdict['reason']
            supervision['lastFailureDecision'] = failure_verdict.to_dict()
            record_evidence(
                root,
                task_id,
                'supervision-verdict',
                'supervision verdict rejected task change',
                {
                    'trigger': trigger,
                    'decision': 'reject',
                    'reason': verdict['reason'],
                    'failureClass': failure_verdict.failure_class,
                },
            )
            supervision['updatedAt'] = now_text()
            save_json(paths['supervision'], supervision)
            publish_runtime_event(
                'supervision.task_changed',
                task_id,
                'change',
                {
                    'allowed': False,
                    'reason': verdict['reason'],
                    'checks': verdict['checks'],
                    'failureClass': failure_verdict.failure_class,
                    'decision': failure_verdict.decision,
                },
            )
            append_log(supervisor_log, f"- {now_text()} | task={task_id} | trigger=on_task_changed | verdict=REJECT | reason={verdict['reason']}")
            raise SystemExit(f"supervisor judge rejected: {verdict['reason']}")
        supervision['status'] = task.get('supervisionState', 'active')
        supervision['lastHeartbeatAt'] = now_text()
        emit_heartbeat_record(root, {
            'stage': f"lifecycle-{task.get('lifecycle', 'unknown')}",
            'currentTask': task['taskId'],
            'nextStep': task.get('nextStep', 'none'),
            'triggerReason': 'periodic-step',
            'riskOrBlocker': task.get('blocker', 'none'),
        }, throttle_seconds=0)
        record_evidence(
            root,
            task_id,
            'content',
            'supervision verdict accepted task change',
            {
                'trigger': trigger,
                'decision': 'allow',
                'reason': verdict['reason'],
                'status': supervision['status'],
            },
        )
        publish_runtime_event(
            'supervision.task_changed',
            task_id,
            'change',
            {
                'allowed': True,
                'status': supervision['status'],
                'reason': verdict['reason'],
                'failureClass': 'none',
                'decision': 'accept',
            },
        )
        append_log(supervisor_log, f"- {now_text()} | task={task_id} | trigger=on_task_changed | status={supervision['status']} | verdict=ALLOW")
    elif trigger == 'on_interruption_detected':
        supervision['lastResumeAt'] = now_text()
        supervision['status'] = 'resume-prepared'
        failure_verdict = route_failure('supervision', {'allowed': False, 'reason': 'interruption-detected', 'checks': ['interruption-detected']})
        supervision['lastFailureDecision'] = failure_verdict.to_dict()
        record_evidence(
            root,
            task_id,
            'resume-required',
            'supervision interruption detected',
            {
                'trigger': trigger,
                'status': supervision['status'],
                'failureClass': failure_verdict.failure_class,
            },
        )
        publish_runtime_event(
            'supervision.interruption_detected',
            task_id,
            'resume',
            {
                'status': supervision['status'],
                'failureClass': failure_verdict.failure_class,
                'decision': failure_verdict.decision,
            },
        )
        append_log(supervisor_log, f"- {now_text()} | task={task_id} | trigger=on_interruption_detected | action=resume")
    elif trigger == 'on_interval':
        supervision['status'] = supervision.get('status') or task.get('supervisionState', 'active')
        supervision['lastHeartbeatAt'] = now_text()
        supervision['stale'] = task.get('lifecycle') in {'blocked', 'waiting-human'}
        emit_heartbeat_record(root, {
            'stage': f"lifecycle-{task.get('lifecycle', 'unknown')}",
            'currentTask': task['taskId'],
            'nextStep': task.get('nextStep', 'none'),
            'triggerReason': 'periodic-step',
            'riskOrBlocker': task.get('blocker', 'none'),
            'requiresHuman': supervision['stale'],
        }, throttle_seconds=0)
        record_evidence(
            root,
            task_id,
            'heartbeat-stale' if supervision['stale'] else 'heartbeat-fresh',
            'supervision interval heartbeat',
            {
                'trigger': trigger,
                'stale': supervision['stale'],
                'status': supervision['status'],
                'lifecycle': task.get('lifecycle', 'unknown'),
            },
        )
        publish_runtime_event(
            'supervision.interval_tick',
            task_id,
            'interval',
            {
                'stale': supervision['stale'],
                'status': supervision['status'],
                'failureClass': 'heartbeat_stale' if supervision['stale'] else 'none',
                'decision': 'prepare_resume' if supervision['stale'] else 'accept',
            },
        )
        append_log(supervisor_log, f"- {now_text()} | task={task_id} | trigger=on_interval | stale={str(supervision['stale']).lower()}")
        if supervision['stale']:
            failure_verdict = route_failure('supervision', {'allowed': False, 'reason': 'stale-heartbeat', 'checks': ['stale-heartbeat']})
            supervision['lastFailureDecision'] = failure_verdict.to_dict()
            append_log(stalled_log, f"- {now_text()} | task={task_id} | lifecycle={task.get('lifecycle', 'unknown')} | stale=true")
            append_log(missed_log, f"- {now_text()} | task={task_id} | reason=blocked-or-waiting-human")
    elif trigger == 'on_completion':
        supervision['status'] = 'handoff-prepared'
        supervision['lastHandoffAt'] = now_text()
        record_evidence(
            root,
            task_id,
            'handoff-emitted',
            'supervision prepared completion handoff',
            {
                'trigger': trigger,
                'status': supervision['status'],
                'nextStep': 'close-task-runtime',
            },
        )
        run_handoff(root, task)
        emit_heartbeat_record(root, {
            'stage': f"lifecycle-{task.get('lifecycle', 'unknown')}",
            'currentTask': task['taskId'],
            'nextStep': 'close-task-runtime',
            'triggerReason': 'stage-complete-stop',
            'riskOrBlocker': 'completion-ready',
            'requiresHuman': True,
        }, throttle_seconds=0)
        publish_runtime_event(
            'supervision.completion_handoff',
            task_id,
            'handoff',
            {
                'status': supervision['status'],
                'nextStep': 'close-task-runtime',
                'failureClass': 'none',
                'decision': 'emit_handoff',
            },
        )
        append_log(supervisor_log, f"- {now_text()} | task={task_id} | trigger=on_completion | action=handoff")
    else:
        raise SystemExit(f'unsupported trigger: {trigger}')

    supervision['updatedAt'] = now_text()
    save_json(paths['supervision'], supervision)
    return supervision
