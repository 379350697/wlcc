---
name: handoff-report
description: Turn results, research, project state, or execution output into handoff formats tailored for different consumers. Use when the same work must be handed to CEO and coder differently, when research must become an executable task brief, when delivery status must be summarized by audience, or when a project needs both decision-ready and execution-ready reporting.
---

# Handoff Report

Transform the same underlying result into different delivery views without losing execution-critical information.

## Workflow

### 1. Identify the handoff audience
Choose the output mode before writing:
- CEO mode: decision-oriented
- Coder mode: execution-oriented

If both are needed, produce both from the same source facts.

### 2. Read the source material
Use only the material relevant to the handoff:
- task result
- project state
- research conclusion
- current blockers
- target files or modules

Do not amplify uncertainty beyond the evidence.

### 3. Extract invariant facts first
Before formatting by audience, identify:
- what was concluded
- what changed
- what remains risky
- what still needs confirmation
- what action is next

### 4. Format by audience

#### CEO mode
Use:

```md
## CEO Handoff
- 结论：
- 风险：
- 待确认项：
```

Focus on:
- whether the direction is sound
- what can be decided now
- what could go wrong
- what still requires confirmation

#### Coder mode
Use:

```md
## Coder Handoff
- 目标：
- 范围：
- 文件：
- 验收标准：
```

Focus on:
- implementation target
- scope boundary
- exact files or components
- concrete completion checks

## Complex-input pattern

When the input contains research, project state, implementation status, and pending decisions at the same time:
1. extract invariant facts first
2. separate confirmed conclusions from open risks
3. produce CEO mode from decision-relevant facts only
4. produce Coder mode from execution-relevant facts only
5. do not let strategic summary erase file/module/action detail

## Output rules

### CEO version
Prefer:
- strategic clarity
- risk framing
- explicit unknowns

Avoid:
- code-level noise
- verbose history
- implementation trivia unless it changes the decision

### Coder version
Prefer:
- concrete objectives
- execution scope
- files/modules
- testable acceptance criteria

Avoid:
- abstract encouragement
- vague summaries
- management-style language with no implementation value

## Example framing

### Source facts
- Research direction is accepted.
- Phase 1 skills are done.
- Real-sample validation found rule gaps.
- Next work is task-state base and resume-state support.

### CEO interpretation
- 结论：方向成立，可进入下一阶段。
- 风险：Skill 规则仍需补细，底层状态尚未实现。
- 待确认项：是否直接投入 Phase 2。

### Coder interpretation
- 目标：补齐 Skill 规则并实现任务状态底座。
- 范围：Skill files, task state files, resume files.
- 文件：`skills/*/SKILL.md`, `TASKS.md`, `.agent/tasks/*`, `.agent/resume/*`.
- 验收标准：Skill 规则补齐，任务状态可创建/更新/恢复。

## Safety rules

- Do not let audience tailoring distort the facts.
- Do not hide uncertainty in the CEO version.
- Do not omit file or scope details in the coder version if they are known.
- Do not generate a handoff that cannot be acted on immediately.
