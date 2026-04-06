# REAL_TASK_HEARTBEAT_POLICY

## 目标
让 heartbeat 正式进入真实任务 runtime，而不是只作为 demo 或单次结果文件。

## 默认规则
### on progress
任务推进后可触发 heartbeat。

### on interval
定期触发 heartbeat，用于判断 stale / waiting-human / blocked。

### on completion
完成时必须触发 completion heartbeat。

## 约束
- 只要 `kind=real` 且 `eligibleForScheduling=true`，heartbeat 就属于正式 runtime 行为
- blocked / waiting-human 状态应可被 heartbeat 明确观察到
- heartbeat summary 必须能够反映真实任务主线
