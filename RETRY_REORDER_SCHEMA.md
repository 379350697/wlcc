# RETRY_REORDER_SCHEMA

## 目标
补齐 bounded autonomy 完整体中缺失的失败重试 / 任务重排 / 回退骨架。

## 结构
### retry-policy
- `maxRetries`
- `retryOn`
- `backoffMode`

### reorder-policy
- `promoteBlockedTask`
- `deprioritizeRepeatedFailure`
- `preferUnblocked`
- `manualPriorityLock`

### retry-runtime
- `backoffMode`
- `backoffDelaySteps`
- `reorderTarget`

### rollback-signal
- `requiresRollback`
- `rollbackTarget`
- `rollbackReason`

## 输出位置
- `.agent/loop/retry-policy.json`
- `.agent/loop/retry-state.json`
- `tests/RETRY_REORDER_RESULT.md`
