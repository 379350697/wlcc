# OBSERVABILITY_DASHBOARD

## loop_history
- none

## check_history
- state_view_consistency: pass
- next_task_consistency: pass
- retrieval_priority: pass
- risk_policy_consistency: pass
- mainline: pass

## failure_clusters
- task-missing-field-demo: 1

## retry_reorder_rollback_history
- retryStateTasks: 1
- latestFailureDecision: rollback
- matchedEvents: 0
- rollbackEvents: 0

## runtime_scope
- defaultScope: real-task-first
- realFailureClusterCount: 0

## system_health_summary
- heartbeatHistoryCount: 59
- heartbeatRequiresHumanCount: 12
- eventCount: 81
- checkFailureCount: 5
- systemHealthcheck: - PASS
