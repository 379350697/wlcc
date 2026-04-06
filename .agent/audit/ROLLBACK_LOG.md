# ROLLBACK_LOG

## 2026-04-05
- 已完成 `task-rollback-demo` 最小回滚演示。
- 通过 backup 恢复被故意写坏的 task 状态文件。
- 当前结论：最小回滚路径成立，且未污染 `task-001 / task-002` 主任务状态。
