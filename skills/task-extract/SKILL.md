---
name: task-extract
description: Extract structured executable tasks from user chat, requirement discussions, implementation notes, or project conversations and merge them into a stable task record. Use when a request is scattered across chat history, when a project needs TASKS.md updates, when work must be turned into goal/current status/blocker/next step/acceptance criteria, or when an agent needs a durable task handoff instead of rereading long conversation history.
---

# Task Extract

Extract explicit work items from chat and convert them into a stable task record.

## Workflow

### 1. Read the minimum required context
Collect only the context needed to define the task correctly:
- the user's current request
- the most recent confirmed implementation status
- existing `TASKS.md` if present
- existing `STATUS.md` if present

Prefer project files over chat restatements when they conflict.

### 2. Separate facts from assumptions
Classify each candidate task field as one of:
- confirmed from project files or explicit user instructions
- confirmed from recent execution evidence
- unclear and requiring a `待确认` marker

Never invent blockers, progress, or acceptance criteria.

### 3. Choose extraction mode

#### Single-task mode
Use when the request clearly refers to one active deliverable.

Output:

```md
## Task
- 目标：
- 当前状态：
- 阻塞项：
- 下一步：
- 验收标准：
```

#### Multi-task mode
Use when the conversation clearly contains multiple distinct deliverables, phases, or owners.

Output:

```md
# TASKS

## Task 1
- 目标：
- 当前状态：
- 阻塞项：
- 下一步：
- 验收标准：

## Task 2
- 目标：
- 当前状态：
- 阻塞项：
- 下一步：
- 验收标准：
```

If a field is unknown, write `待确认` or `未发现` instead of guessing.

### 4. Merge instead of overwrite
When `TASKS.md` already exists:
- update the matching active task if the intent is clearly the same
- append a new task if the request is materially new
- preserve unrelated tasks
- do not silently delete historical context that is still active

### 5. Keep execution-oriented wording
Write tasks so a coder can act on them immediately.

Prefer:
- concrete goal
- current real status
- explicit blocker
- next executable action
- verifiable acceptance check

Avoid:
- vague summaries
- emotional language
- repeating raw chat history

## Recommended TASKS.md template

Use this template when creating a new `TASKS.md` from scratch:

```md
# TASKS

## Active

### Task 1
- 目标：
- 当前状态：
- 阻塞项：
- 下一步：
- 验收标准：

## Done

### Task X
- 目标：
- 完成结果：
- 验收情况：
```

Rules:
- keep active and done separated
- do not move a task to done without evidence
- keep unrelated active tasks intact

## Merge rules

### Update an existing task when
- the goal matches the current request
- the project/files referenced are the same
- the new message is clearly a continuation

### Create a new task when
- the goal changes materially
- the user introduces a distinct deliverable
- the old task is done and a new one starts

### Mark `待确认` when
- ownership is unclear
- acceptance criteria are implied but not stated
- there is conflicting status across files and chat

## Output quality bar

A good extraction must make it possible to answer, without rereading the whole chat:
- what is being done
- what is already known
- what is blocked
- what should happen next
- how completion will be judged

## Safety rules

- Do not mark a task done without explicit evidence.
- Do not rewrite the full file when a local merge is enough.
- Do not convert speculation into task facts.
- Do not erase blockers just because the latest message is optimistic.
