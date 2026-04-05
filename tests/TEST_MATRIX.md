# Test Matrix

## 已完成
- 恢复演示（task-resume-demo）
- 回滚演示（task-rollback-demo）
- doing / blocked / done 状态流转
- TASKS 总览同步
- 串行锁修复验证

## 待补场景
1. 连续更新场景
2. 错误状态写入场景
3. 恢复后继续更新场景
4. 总览同步一致性场景
5. backup 缺失分支场景

## 目标
把最容易在后续演进中出 bug 的路径，先用受控样本打出来并记录结果。
