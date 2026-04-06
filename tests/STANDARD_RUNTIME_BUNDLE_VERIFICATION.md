# STANDARD_RUNTIME_BUNDLE_VERIFICATION

## checks
- runtime-pytest: PASS
  - stdout: ...........................                                              [100%]
27 passed in 0.36s
- tool-harness: PASS
  - stdout: === test_tool_harness.py ===

--- Registry Tests ---
  [PASS] registry-已注册-read_only — read_only=True
  [PASS] registry-已注册-concurrent_safe — concurrent_safe=True
  [PASS] registry-已注册-timeout — timeout=30
  [PASS] registry-未注册-fail-closed-read_only — default read_only=False
  [PASS] registry-未注册-fail-closed-concurrent_safe — default concurrent_safe=False
  [PASS] registry-未注册-fail-closed-can_modi
- progress-task-runtime: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/tests/PROGRESS_TASK_RUNTIME_TEST_RESULT.md
- ingest-real-task: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/tests/INGEST_REAL_TASK_TEST_RESULT.md
- close-task-runtime: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/tests/CLOSE_TASK_RUNTIME_TEST_RESULT.md
- resume-real-task: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/tests/RESUME_REAL_TASK_TEST_RESULT.md
- task-supervision: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/tests/TASK_SUPERVISION_TEST_RESULT.md
- heartbeat-summary: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/tests/HEARTBEAT_SUMMARY_TEST_RESULT.md
- observability-dashboard: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/tests/OBSERVABILITY_DASHBOARD_TEST_RESULT.md
- render-state-views: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/.agent/tasks/demo-schema-check.md
OK: wrote /mnt/d/codex/wlcc/.agent/resume/demo-schema-check-resume.md
OK: wrote /mnt/d/codex/wlcc/.agent/tasks/real-close-runtime-debug-target.md
OK: wrote /mnt/d/codex/wlcc/.agent/resume/real-close-runtime-debug-target-resume.md
OK: wrote /mnt/d/codex/wlcc/.agent/tasks/real-close-runtime-final-target.md
OK: wrote /mnt/d/codex/wlcc/.age
- state-view-consistency: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/tests/STATE_VIEW_CONSISTENCY_RESULT.md
- retrieval-priority: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/tests/RETRIEVAL_PRIORITY_CHECK_RESULT.md
- system-healthcheck: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/.agent/logs/EVENT_LOG.md
PASS
- phase2-mainline: PASS
  - stdout: OK: wrote /mnt/d/codex/wlcc/tests/PHASE2_MAINLINE_CHECK_RESULT.md

## overall
- status: PASS
