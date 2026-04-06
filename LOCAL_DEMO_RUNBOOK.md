# LOCAL_DEMO_RUNBOOK

## 如何运行完整 demo

### 1. 主链检查
```bash
python3 scripts/check_phase2_mainline.py
```

### 2. 核心 demo 链路
已实际跑过：
- demo task state
- next-task
- resume
- heartbeat
- handoff
- observability

### 3. 完整 demo 包
```bash
python3 scripts/test_demo_completeness_pack.py
```

### 4. 关键输出
- `.agent/state/tasks/demo-long-chain-autonomy.json`
- `.agent/NEXT_TASK.md`
- `tests/demo-long-chain-autonomy-resume-output.md`
- `tests/HANDOFF_OUTPUT.md`
- `tests/HEARTBEAT_SUMMARY_RESULT.md`
- `.agent/audit/OBSERVABILITY_DASHBOARD.md`
- `tests/DEMO_COMPLETENESS_PACK_RESULT.md`

## 适用场景
- 本地验收
- 对外演示前自查
- 回归测试入口
