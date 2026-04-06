# TOOL_HARNESS_TEST_RESULT

- registry-已注册-read_only: PASS (read_only=True)
- registry-已注册-concurrent_safe: PASS (concurrent_safe=True)
- registry-已注册-timeout: PASS (timeout=30)
- registry-未注册-fail-closed-read_only: PASS (default read_only=False)
- registry-未注册-fail-closed-concurrent_safe: PASS (default concurrent_safe=False)
- registry-未注册-fail-closed-can_modify_state: PASS (default can_modify_state=True)
- registry-is_registered-已注册: PASS
- registry-is_registered-未注册: PASS
- registry-concurrent-list-非空: PASS (count=20)
- registry-concurrent-list-包含render: PASS
- registry-py后缀处理: PASS (去除 .py 后正确匹配)
- registry-路径前缀处理: PASS (去除路径后正确匹配)
- partition-组数: PASS (expected 3 (concurrent+serial+serial), got 3)
- partition-第一组并发: PASS (type=concurrent)
- partition-第一组包含2个步骤: PASS (steps=2)
- partition-第二组串行: PASS (type=serial)
- tracked-step-序列化: PASS
- tracked-step-cmd: PASS
- log-目录存在: PASS

## Overall: PASS
