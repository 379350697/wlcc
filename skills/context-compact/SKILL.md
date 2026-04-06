---
name: context-compact
description: Compress long project or execution conversations into a structured resume-quality summary that preserves facts, decisions, blockers, status, and next steps. Use when conversation history is long, when work is being resumed after interruption, when a handoff or context reset is needed, or when an agent must reduce chat volume without losing execution-critical state.
---

# Context Compact

Compress long conversations into a structured summary that supports continued execution, not just shorter reading.

## Workflow

### 1. Gather the minimum execution context
Use:
- the active conversation span
- relevant project fact files if available
- recent execution evidence
- current task state if available

Prefer execution evidence and project facts over conversational impressions.

### 2. Split content into evidence classes
Every compact summary must separate:
- `已证实`: facts supported by files, commands, or explicit user instruction
- `已决策`: choices already made
- `待验证`: unresolved claims, assumptions, or incomplete checks
- `当前任务状态`: where execution stands now
- `下一步`: the next concrete action

### 3. Preserve execution anchors
Always keep:
- referenced files
- blockers
- failed attempts if they matter
- next actionable step
- acceptance-relevant details

Do not reduce the summary to a timeline or chat recap.

### 4. Output in a fixed structure
Use this structure:

```md
## Compact Summary
### 已证实
- 

### 已决策
- 

### 待验证
- 

### 当前任务状态
- 

### 恢复锚点
- 最后成功动作：
- 最后失败动作：

### 下一步
- 
```

### 5. Optimize for resume quality
A good compact summary should allow another agent or a later session to continue with minimal rereading.

## Compression rules

### Keep
- concrete facts
- constraints
- blockers
- latest successful action
- latest failed action when relevant
- next step

### Drop
- politeness chatter
- repeated explanations
- stale branches already superseded
- low-value tool noise

### Mark uncertainty explicitly
If something is plausible but unverified, keep it under `待验证`.
Never move it into `已证实` just to make the summary cleaner.

## Safety rules

- Do not compress away blockers.
- Do not hide failed actions that explain current state.
- Do not merge assumptions into facts.
- Do not output free-form prose when structured state is needed.
