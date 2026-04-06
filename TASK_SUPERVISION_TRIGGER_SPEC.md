# TASK_SUPERVISION_TRIGGER_SPEC

## 目标
把真实任务监督器中的 trigger 从“脚本支持”升级成“正式规范”，明确输入、动作链、输出和失败策略。

## 统一输入
所有 trigger 最低输入：
- `taskId`
- `trigger`

任务数据来源：
1. `.agent/state/tasks/<task-id>.json`
2. `.agent/state/supervision/<task-id>.json`
3. handoff / heartbeat / resume 等运行态文件

---

## Trigger 1：on_task_ingested
### 进入条件
真实任务刚完成 ingest。
### 动作链
1. supervision 进入 active
2. 记录 `lastHeartbeatAt`
3. 触发初始 heartbeat
4. 构建 heartbeat summary
### 输出
- supervision state 更新
- heartbeat 结果更新
### 失败策略
- heartbeat 失败则 trigger 失败
- supervision state 不应假装成功

---

## Trigger 2：on_task_changed
### 进入条件
真实任务状态、blocker、nextStep 等发生变化。
### 动作链
1. supervision 状态与 task 同步
2. 触发 heartbeat
### 输出
- supervision state 更新
- heartbeat 结果更新
### 失败策略
- 若 task state 缺失，直接失败

---

## Trigger 3：on_interruption_detected
### 进入条件
任务发生会话切换、中断、恢复需求。
### 动作链
1. 记录 `lastResumeAt`
2. 调用 `resume_task.py`
3. 准备 resume output
### 输出
- supervision state 更新
- resume output 更新
### 失败策略
- resume 失败则 trigger 失败

---

## Trigger 4：on_interval
### 进入条件
定期间隔触发。
### 动作链
1. 更新 `lastHeartbeatAt`
2. 判断是否 stale
3. 触发 interval heartbeat
### 输出
- supervision state 更新
- heartbeat / summary 更新
### 失败策略
- stale 判断失败时应显式失败，不默默忽略

---

## Trigger 5：on_completion
### 进入条件
任务已进入完成收口阶段。
### 动作链
1. 记录 `lastHandoffAt`
2. 生成 handoff state
3. 触发 completion heartbeat
### 输出
- handoff state
- heartbeat / summary
- supervision state 更新
### 失败策略
- handoff 失败则 trigger 失败

---

## 统一失败原则
- trigger 失败不能假装完成
- 失败必须留下可见结果或退出码
- 后续 orchestrator 只能消费成功 trigger 的结果
