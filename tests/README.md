# tests

当前仓库的测试分三层：

1. `tests/runtime/`
- 这是主信心来源。
- 直接验证 `runtime/` 内核，不依赖太多脚本包装。

2. `scripts/test_*.py`
- 这是兼容性 smoke test。
- 用来确认旧 CLI 入口在 runtime 化之后仍然可用。

3. `tests/*.md` 与 `tests/*.json`
- 这些是结果产物和摘要，不是主要断言层。
- 它们更多用于审计、回看、演示和交付记录。

推荐的执行顺序：

1. 先跑 runtime 回归
```bash
python3 -m pytest tests/runtime -q
```

2. 再跑标准运行版验收
```bash
python3 scripts/verify_standard_runtime_bundle.py
```

关于 sidecar 边界：

- `next-task.json` 属于同步主链产物，必须存在。
- `NEXT_TASK.md`、`.agent/tasks/*.md`、`.agent/resume/*.md`、heartbeat summary、observability dashboard 属于 sidecar 产物。
- 主链成功不应依赖 sidecar 先生成；sidecar 可以稍后补齐。
