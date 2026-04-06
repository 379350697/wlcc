# RETRY_REORDER_TEST_RESULT

## retry-1
- action: retry-same-task
- backoffDelaySteps: 1
- manualPriorityLock: false
- reorderTarget: none
- result: PASS

## retry-2
- action: retry-same-task
- backoffDelaySteps: 2
- manualPriorityLock: false
- reorderTarget: none
- result: PASS

## reorder-promote-unblocked
- action: reorder-next-task
- backoffDelaySteps: 0
- manualPriorityLock: false
- reorderTarget: task-001
- result: PASS

## reorder-manual-lock
- action: reorder-next-task
- backoffDelaySteps: 0
- manualPriorityLock: true
- reorderTarget: none
- result: PASS

## Overall
- PASS
