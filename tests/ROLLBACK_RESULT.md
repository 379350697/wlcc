# Rollback Demo Result

## 样本
- `task-rollback-demo`

## 演示步骤
1. 对正常任务状态与 Resume State 生成 backup
2. 故意将 task 状态写成错误值 `corrupted`
3. 使用 backup 恢复 task 与 resume 文件
4. 核对恢复后内容

## 预期恢复后状态
- Task State 回到正常 `doing`
- Resume State 回到正常描述
- 不污染 `task-001 / task-002`

## 判断
**通过（最小回滚证明成立）**

说明：
- 演示仅作用于 demo 任务
- 现有主任务状态未被破坏
- backup 可用于恢复错误写入后的任务状态文件
