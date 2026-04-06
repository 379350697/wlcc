# COMPATIBILITY_AUDIT

## 2026-04-05
- 已实现 `scripts/read_project_context.py`。
- 已验证当前最小分层读取路径可读取：长期规则、项目事实、会话摘要、任务状态、任务日志。
- 当前结论：兼容读取已从文档说明进入最小脚本实现。

## 已验证层级
1. `memory/long-term/RULES.md`
2. `README.md / STATUS.md / DECISIONS.md / TASKS.md / INCIDENTS.md`
3. `memory/session/SESSION_SUMMARY.md`
4. `.agent/tasks/<task>.md`
5. `.agent/resume/<task>-resume.md`
6. `.agent/logs/CHANGELOG.md`
