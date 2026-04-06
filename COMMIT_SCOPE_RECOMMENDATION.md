# COMMIT_SCOPE_RECOMMENDATION

## 建议提交
### 核心修改
- `STATUS.md`
- `SKILL_VALIDATION_ROUND1.md`
- `MEMORY_LAYERING_PLAN.md`
- `scripts/build_audit_summary.py`
- `scripts/build_release_manifest.py`
- `scripts/check_delivery_completeness.py`
- `scripts/check_next_stage_readiness.py`
- `scripts/run_degraded_read_test.py`
- `scripts/system_healthcheck.py`
- `.agent/tasks/task-001.md`
- `tests/RISK_GATE_RESULT.md`

### 核心新增
- `.agent/logs/EVENT_LOG.md`
- `.agent/logs/RELEASE_SCOPE.md`
- `FINAL_RELEASE_ACCEPTANCE.md`
- `scripts/log_event.py`
- `scripts/resume_task.py`
- `tests/README.md`

### 建议保留的删除
- `.agent/backups/*`
- `.agent/resume/task-002-resume.md`
- `.agent/resume/task-backup-miss-demo-resume.md`
- `.agent/resume/task-concurrent-demo-resume.md`
- `.agent/resume/task-resume-continue-demo-resume.md`
- `.agent/resume/task-resume-demo-resume.md`
- `.agent/resume/task-rollback-demo-resume.md`
- `.agent/tasks/task-002.md`
- `.agent/tasks/task-backup-miss-demo.md`
- `.agent/tasks/task-concurrent-demo.md`
- `.agent/tasks/task-resume-continue-demo.md`
- `.agent/tasks/task-resume-demo.md`
- `.agent/tasks/task-rollback-demo.md`
- 旧测试结果文件删除（`tests/` 下历史噪音）

## 不建议提交
### 临时整理文件
- `CHANGESET_PLAN.md`

## 备注
- 当前建议提交范围符合“更干净上线版”目标：保留核心脚本、核心日志、核心验收文件，删除 demo/backups/历史测试噪音。
