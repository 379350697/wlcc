# Compatibility Read Result

## 场景
- 按新的分层结构读取项目上下文
- 在项目级、任务级、摘要级之间做兼容读取

## 读取对象
- `memory/long-term/RULES.md`
- `README.md`
- `STATUS.md`
- `DECISIONS.md`
- `TASKS.md`
- `INCIDENTS.md`
- `memory/session/SESSION_SUMMARY.md`
- `.agent/tasks/task-001.md`
- `.agent/resume/task-001-resume.md`
- `.agent/logs/CHANGELOG.md`

## 目标
验证当前最小兼容读取路径已经可以把长期规则、项目事实、任务状态、会话摘要按层读出来。
