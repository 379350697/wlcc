# wlcc

一个面向 OpenClaw 的可部署项目原型仓库，用于快速恢复并继续工作。

## 包含内容
- 实施文档：架构、迁移、回滚
- Skills：4 个可复用 Skill 定义与打包产物
- 项目事实文件：README / STATUS / DECISIONS / TASKS / INCIDENTS
- 状态底座：Task State / Resume State / CHANGELOG / 审计文件
- 脚本：安全写入、状态更新、分层读取、风险检查、审计汇总、健康检查、交付检查
- 测试与验证材料

## 快速开始
1. 确保系统有 `bash` 和 `python3`
2. 执行：
   ```bash
   bash scripts/bootstrap_project.sh
   python3 scripts/system_healthcheck.py
   python3 scripts/check_delivery_completeness.py
   ```
3. 继续工作前优先查看：
   - `FINAL_DELIVERY_SUMMARY.md`
   - `TEST_RESULTS.md`
   - `TASKS.md`
   - `.agent/audit/AUDIT_SUMMARY.md`

## 当前状态
当前仓库已经具备：
- 最小 Skill 闭环
- 最小状态底座
- 恢复/回滚最小证明
- 多场景测试
- 记忆分层与兼容读取最小实现
- 权限/留痕最小实现

## 注意
研究用的大型上游样本仓库未默认纳入该发布版，以保持仓库轻量、可部署、可复用。
