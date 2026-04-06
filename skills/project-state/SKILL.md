---
name: project-state
description: Read core project files and produce a current-state summary grounded in project facts rather than chat history. Use when starting work on an existing project, when recovering context after a long pause, when a user asks for current phase/risk/blockers/next steps, or when STATUS.md needs a disciplined summary from README.md, STATUS.md, DECISIONS.md, TASKS.md, and INCIDENTS.md.
---

# Project State

Read project fact files and summarize the real current state with explicit handling for missing files and stale information.

## Workflow

### 1. Read project fact sources in order
Read these files if they exist:
1. `README.md`
2. `STATUS.md`
3. `DECISIONS.md`
4. `TASKS.md`
5. `INCIDENTS.md`

Treat missing files as missing evidence, not as empty truth.

### 2. Extract only state-relevant information
Build the summary around:
- current phase
- recent meaningful change
- active risks
- active blockers
- next step

Ignore decorative or outdated narrative unless it changes execution.

### 3. Resolve source priority correctly
When sources disagree, prefer:
1. the most specific project fact file
2. the most recent explicit status file
3. task state tied to active work
4. chat history

If timing is unclear, mark it explicitly as `时间不明` and avoid pretending recency.

### 4. Output in a fixed structure
Use this structure:

```md
## Project State
- 当前阶段：
- 最近变化：
- 风险点：
- 阻塞项：
- 下一步：
```

For missing inputs, state `缺失/未发现`.

## File interpretation rules

### README.md
Use for:
- project purpose
- scope
- main architecture or constraints

### STATUS.md
Use for:
- latest known progress
- current stage
- current blockers

### DECISIONS.md
Use for:
- fixed choices
- constraints created by past decisions
- options that are no longer open

### TASKS.md
Use for:
- active deliverables
- task states
- owner-facing next steps

### INCIDENTS.md
Use for:
- failure patterns
- unresolved operational risks
- recovery notes that affect current work

## Degrade gracefully

If some files are missing:
- still produce a useful summary
- list what evidence is absent
- avoid pretending completeness

If a core file is missing and the user wants the project normalized, recommend initializing a minimal template instead of fabricating content.

### Minimal templates to suggest

#### STATUS.md
```md
# STATUS.md

## 当前阶段

## 最近变化

## 当前阻塞

## 下一步
```

#### DECISIONS.md
```md
# DECISIONS.md

## 已确定决策
- 
```

#### INCIDENTS.md
```md
# INCIDENTS.md

## 当前已知问题
- 
```

## Safety rules

- Do not let old status override newer explicit state.
- Do not treat a historical decision as a current blocker unless it still applies.
- Do not infer project health from silence.
- Do not summarize chat first when project files exist.
