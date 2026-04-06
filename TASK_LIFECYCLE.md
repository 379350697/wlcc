# TASK_LIFECYCLE

## 目标
为真实任务接管机制层定义统一生命周期，让任务在任何会话、任何 agent、任何中断点下都能按状态迁移规则继续推进，而不是靠上下文记忆。

## 生命周期状态
- `new`
- `ingested`
- `active`
- `blocked`
- `waiting-human`
- `handoff`
- `done`
- `archived`
- `legacy`（兼容旧任务）

## 状态定义
### new
任务刚被识别，但尚未正式写入 canonical runtime。

### ingested
任务已进入 runtime，已生成 canonical task / views / next-task / supervision 初始状态。

### active
任务正在正式推进，默认允许调度与 heartbeat 监督。

### blocked
任务存在依赖或外部阻塞，不能继续推进。

### waiting-human
任务需要人工确认、人工输入或人工决策。

### handoff
任务已进入交接阶段，等待 reviewer / owner / 下一角色接手。

### done
任务已完成主要交付，等待 closure / archive。

### archived
任务已正式归档，不再进入主调度链。

### legacy
旧任务兼容态。允许存在，但不应作为真实任务机制层的正式目标状态。

## 进入条件 / 必做动作
### new -> ingested
进入条件：调用 `ingest_real_task.py`
必做动作：
- 写 canonical task
- 写 supervision state
- 渲染 task / resume / TASKS
- 刷 next-task
- 生成初始 resume output

### ingested -> active
进入条件：任务被正式接管并准备开始推进
必做动作：
- `supervisionState=active`
- `eligibleForScheduling=true`
- 允许进入正式 next-task

### active -> blocked
进入条件：依赖未满足 / 外部条件阻塞
必做动作：
- 写 blocker
- `supervisionState=blocked`
- heartbeat 可汇报阻塞

### active -> waiting-human
进入条件：需要人工确认 / 风险前置 / stop condition
必做动作：
- `supervisionState=waiting-human`
- heartbeat / handoff 可触发

### active -> handoff
进入条件：任务执行方准备交接
必做动作：
- 写 handoff state
- 生成 handoff output
- 更新 ownership / reviewer

### active -> done
进入条件：主要目标已完成并通过基本校验
必做动作：
- 更新结果
- closure 预备
- final handoff 可选

### done -> archived
进入条件：closure 完成
必做动作：
- 退出主调度链
- `eligibleForScheduling=false`
- `isPrimaryTrack=false`

## 非法迁移原则
- 不允许直接 `new -> done`
- 不允许直接 `archived -> active`
- 不允许跳过 ingest 进入 active
- 非法迁移应拒绝或显式告警

## 监督原则
- `active` 必须纳入 heartbeat / supervision
- `blocked` / `waiting-human` 必须能被 heartbeat 明确观察到
- `handoff` 必须有明确 handoff state
- `done` 必须准备 closure
