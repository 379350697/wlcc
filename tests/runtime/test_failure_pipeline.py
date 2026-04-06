from runtime.failure.classifier import (
    classify_delivery_failure,
    classify_progress_failure,
    classify_risk_failure,
    classify_supervision_failure,
)
from runtime.failure.pipeline import build_failure_verdict, route_failure


def test_progress_failure_maps_to_content_weak():
    verdict = {
        'passed': False,
        'reason': 'latest_result 太短（2 字符，最少 5）',
        'violations': [{'check': 'latest_result_length', 'passed': False}],
    }
    assert classify_progress_failure(verdict) == 'content_weak'
    routed = route_failure('progress', verdict)
    assert routed.failure_class == 'content_weak'
    assert routed.decision == 'retry_same_step'
    assert routed.retryable is True


def test_delivery_failure_maps_to_evidence_insufficient():
    verdict = {
        'passed': False,
        'reason': 'insufficient evidence: 1/2',
        'required': 2,
        'collected': 1,
        'evidence': [{'type': 'content'}],
    }
    assert classify_delivery_failure(verdict) == 'evidence_insufficient'
    routed = route_failure('delivery', verdict)
    assert routed.failure_class == 'evidence_insufficient'
    assert routed.decision == 'degrade_continue'


def test_risk_failure_maps_to_manual_intervention_and_block():
    reject = {'decision': 'reject', 'reason': '破坏性状态删除默认拒绝。'}
    confirm = {'decision': 'require-confirmation', 'reason': '修改配置需要确认。'}
    assert classify_risk_failure(reject) == 'risk_blocked'
    assert classify_risk_failure(confirm) == 'manual_intervention_required'
    assert route_failure('risk', reject).decision == 'freeze_task'
    assert route_failure('risk', confirm).decision == 'escalate_human'


def test_supervision_failure_maps_to_heartbeat_stale():
    verdict = {'allowed': False, 'reason': 'stale-heartbeat', 'checks': ['stale-heartbeat']}
    assert classify_supervision_failure(verdict) == 'heartbeat_stale'
    routed = route_failure('supervision', verdict)
    assert routed.failure_class == 'heartbeat_stale'
    assert routed.decision == 'prepare_resume'
    assert routed.requires_human is True


def test_supervision_interruption_maps_to_resume_required():
    verdict = {'allowed': False, 'reason': 'interruption-detected', 'checks': ['interruption-detected']}
    routed = route_failure('supervision', verdict)
    assert routed.failure_class == 'resume_required'
    assert routed.decision == 'prepare_resume'
    assert routed.requires_human is True


def test_build_failure_verdict_has_compact_dict_shape():
    verdict = build_failure_verdict('content_weak', 'progress', 'weak result', {'passed': False})
    data = verdict.to_dict()
    assert data['failure_class'] == 'content_weak'
    assert data['next_action'] == 'retry_same_step'
    assert data['details']['passed'] is False
