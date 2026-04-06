# HEARTBEAT_SCHEMA

## 目标
让长链执行不是黑箱，也不是每一步都打扰，而是在关键节点输出压缩后的可决策状态。

## 最低字段
- `stage`
- `completedItems`
- `currentTask`
- `riskOrBlocker`
- `nextStep`
- `requiresHuman`
- `triggerReason`
- `emittedAt`
- `humanSummary`
- `throttled`

## 触发条件
- 每完成 N 个任务
- 每次 stop condition
- 每次阶段完成
- 每次 degraded / fallback

## 输出位置
- `.agent/heartbeat/latest-heartbeat.json`
- `.agent/heartbeat/heartbeat-history.json`
- `.agent/heartbeat/heartbeat-summary.json`
- `tests/HEARTBEAT_RESULT.md`
- `tests/HEARTBEAT_SUMMARY_RESULT.md`

## 聚合要求
- latest heartbeat 可直接查看当前状态
- daily summary 用于按天回顾
- stage summary 用于阶段聚合
- anomaly heartbeats 单独聚合
- 相同 heartbeat 需支持去噪 / 节流
