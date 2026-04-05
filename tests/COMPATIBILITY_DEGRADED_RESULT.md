# Compatibility Degraded Result

## 场景
- 会话摘要层缺失时的兼容读取降级

## 方法
- 临时移走 `memory/session/SESSION_SUMMARY.md`
- 运行 `read_project_context.py`
- 记录输出后恢复文件

## 预期
- session_summary 显示为 `MISSING`
- 其他层仍可正常读取
- 不影响项目事实层和任务状态层

## 判断
若输出中只有 session_summary 缺失，而其他层保持可读，则视为通过。
