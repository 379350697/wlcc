# Recovery & Rollback Controlled Test Plan

## 目标
在不污染现有主状态的前提下，使用受控样本验证：
1. 任务中断后能否仅基于状态文件恢复
2. 状态文件被错误写入后能否从备份回滚

## 受控样本
- `task-resume-demo`
- `task-rollback-demo`

## 恢复演示
输入文件：
- `TASKS.md`
- `.agent/tasks/task-resume-demo.md`
- `.agent/resume/task-resume-demo-resume.md`
- `.agent/logs/CHANGELOG.md`

验证目标：
- 恢复出目标
- 恢复出当前状态
- 恢复出当前阻塞
- 恢复出下一步

## 回滚演示
输入文件：
- `.agent/tasks/task-rollback-demo.md`
- `.agent/resume/task-rollback-demo-resume.md`
- `.agent/backups/*`

验证步骤：
1. 生成正常状态
2. 故意写入错误状态
3. 使用 backup 回滚
4. 核对回滚后内容
5. 记录日志

## 约束
- 不破坏现有 `task-001 / task-002`
- 错误写入仅作用于 demo 任务
- 所有测试结果要落文档
