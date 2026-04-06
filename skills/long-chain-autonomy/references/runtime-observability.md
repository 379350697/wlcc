# Runtime Observability

## Heartbeat
- `.agent/heartbeat/latest-heartbeat.json`
- `.agent/heartbeat/heartbeat-history.json`
- `.agent/heartbeat/heartbeat-summary.json`

## Observability outputs
- `.agent/audit/EVENT_OVERVIEW.md`
- `.agent/audit/AUDIT_SUMMARY.md`
- `.agent/audit/OBSERVABILITY_DASHBOARD.md`
- `.agent/audit/observability-dashboard.json`

## Runtime scripts
- `scripts/emit_heartbeat.py`
- `scripts/build_heartbeat_summary.py`
- `scripts/build_observability_dashboard.py`

## Rule
The wrapper skill must expose observability as product behavior, not as optional debug noise.
