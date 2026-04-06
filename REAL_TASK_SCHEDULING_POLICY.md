# REAL_TASK_SCHEDULING_POLICY

## 目标
让 next-task 正式默认只调度真实任务，而不是被 demo / fixture / sample 污染。

## 默认规则
- 只调度 `eligibleForScheduling=true`
- 只调度 `executionMode != sample-only`
- 优先 `kind=real`
- 优先 `isPrimaryTrack=true`

## 兼容规则
旧任务如果缺少这些字段，默认按样本对待：
- `kind=sample`
- `executionMode=sample-only`
- `eligibleForScheduling=false`
- `isPrimaryTrack=false`

## 结果
- demo / fixture 默认不进入正式执行链
- 真正的用户任务可以在任何会话中稳定成为 next-task
