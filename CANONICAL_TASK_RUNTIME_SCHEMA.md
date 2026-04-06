# CANONICAL_TASK_RUNTIME_SCHEMA

## 目标
把真实任务接管机制层需要的 canonical task 元字段正式化，并让调度与监督链可依赖这些字段，而不再只靠约定。

## 核心字段
### 既有字段
- `taskId`
- `project`
- `goal`
- `status`
- `priority`
- `dependencies`
- `override`
- `latestResult`
- `blocker`
- `nextStep`
- `lastSuccess`
- `lastFailure`
- `updatedAt`

### 新增 runtime 元字段
- `kind`: `real | demo | fixture | sample`
- `source`: 任务来源，如 `user-directive | demo-run | migration-sample`
- `executionMode`: `live | background | sample-only`
- `ownerContext`: 任务所属上下文，如 `discord-direct`
- `supervisionState`: `new | ingested | active | stale | waiting-human | handoff | done`
- `eligibleForScheduling`: `true | false`
- `isPrimaryTrack`: `true | false`
- `lifecycle`: `new | ingested | active | blocked | waiting-human | handoff | done | archived`
- `title`: 简短标题

## 调度规则
- 默认只调度 `eligibleForScheduling=true`
- 默认优先调度 `kind=real`
- `isPrimaryTrack=true` 的 real task 优先于 demo / fixture / sample
- `executionMode=sample-only` 默认不进入正式执行链

## 最低兼容规则
- 缺少新字段时，按兼容默认值处理，不直接炸旧任务：
  - `kind=sample`
  - `source=legacy`
  - `executionMode=sample-only`
  - `ownerContext=unknown`
  - `supervisionState=legacy`
  - `eligibleForScheduling=false`
  - `isPrimaryTrack=false`
  - `lifecycle=legacy`
