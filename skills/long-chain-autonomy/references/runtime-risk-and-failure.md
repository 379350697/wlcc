# Runtime Risk and Failure

## Risk layer
- `risk_policy.json`
- `scripts/evaluate_risk_policy.py`
- `scripts/check_risk_level.py`
- `scripts/evaluate_risk_escalation.py`

## Failure layer
- `scripts/evaluate_failure_control.py`
- `scripts/evaluate_retry_reorder.py`
- retry / reorder / rollback / dead-loop-stop

## Shared semantics
- all entry modes must preserve the same risk gates
- all high-risk actions must respect confirmation policy
- failure decisions must remain structured, not ad-hoc
