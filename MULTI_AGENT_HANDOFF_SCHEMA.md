# MULTI_AGENT_HANDOFF_SCHEMA

## 目标
把 owner / executor / reviewer、多 agent 共享状态、handoff 协议统一成可写入、可恢复、可验证的结构化层。

## 1. Ownership State
文件：`.agent/state/ownership/<task-id>.json`

字段：
- `taskId`
- `owner`
- `executor`
- `reviewer`
- `updatedAt`
- `notes`

规则：
- owner 负责任务归属
- executor 负责当前执行
- reviewer 负责验收 / 审核
- 未设置时默认 `unassigned`

## 2. Handoff State
文件：`.agent/state/handoffs/<task-id>.json`

字段：
- `taskId`
- `fromAgent`
- `toAgent`
- `reason`
- `summary`
- `nextAction`
- `requiresHuman`
- `linkedResumeState`
- `linkedNextTask`
- `updatedAt`

规则：
- handoff 必须带 summary
- handoff 必须能链接到当前 resume state
- handoff 必须能链接到当前 next-task

## 3. Multi-agent Inheritance Rules
- 多 agent 共享 canonical state
- 不同 agent 只通过 state store / handoff state 继承上下文
- stop / heartbeat / risk 语义对所有 agent 一致
- handoff 后恢复优先读取 handoff state，再读取 resume state / next-task

## 4. Render Targets
- `.agent/handoffs/<task-id>.md`
- `tests/HANDOFF_OUTPUT.md`
- `tests/MULTI_AGENT_STATE_RESULT.md`
