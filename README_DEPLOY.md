# README_DEPLOY

## 用途
这是一个可复用的 OpenClaw 项目原型仓库，目标是在新的 OpenClaw 环境中快速部署并继续迭代。

## 包含内容
- 实施文档
- Skill 定义与打包产物
- 项目事实文件
- 状态底座与审计脚本
- 测试与验证结果
- 最小记忆分层样例

## 建议部署步骤
1. 将仓库 clone 到新的工作目录
2. 确保 Python 3 可用
3. 运行 `scripts/bootstrap_project.sh`
4. 运行 `python3 scripts/system_healthcheck.py`
5. 运行 `python3 scripts/check_delivery_completeness.py`
6. 如需继续任务，先看：
   - `FINAL_DELIVERY_SUMMARY.md`
   - `TEST_RESULTS.md`
   - `TASKS.md`
   - `.agent/audit/AUDIT_SUMMARY.md`

## 最小继续工作入口
- 项目事实：`README.md / STATUS.md / DECISIONS.md / TASKS.md / INCIDENTS.md`
- 任务状态：`.agent/tasks/` 与 `.agent/resume/`
- 审计摘要：`.agent/audit/AUDIT_SUMMARY.md`
- 风险策略：`.agent/audit/ACCESS_POLICY.md`

## 注意
- `memory/long-term/` 与 `memory/session/` 中的是当前项目快照样例，可按新环境需要更新。
- backup、日志、测试结果建议保留，便于后续恢复与审计。
