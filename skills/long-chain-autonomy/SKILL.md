---
name: long-chain-autonomy
description: Unified runtime entry for long-chain autonomous project execution with canonical state, next-task, retrieval-first resume, risk/failure governance, heartbeat/observability, and handoff-aware continuation. Use when a project should run as one packaged system instead of separate skills, when task extraction/state summary/compact/handoff must share one runtime, when work needs resumable execution with risk controls, or when deploying the full product mode of this repository.
---

# Long Chain Autonomy

Use this skill as the **single product entry** for the repository.

It wraps three layers together:
- product entry workflow
- runtime / infrastructure layer
- reusable atomic skill modules

## Workflow

### 1. Choose the operating mode
Use one of these modes:
- **task mode**: create or update executable task state
- **state mode**: summarize current project/runtime state
- **resume mode**: recover continuation state after interruption
- **handoff mode**: prepare decision-ready or execution-ready handoff
- **runtime mode**: run checks, read next-task, inspect risk/heartbeat/observability

### 2. Prefer runtime state before chat reconstruction
When the repository contains runtime state, prefer this order:
1. `.agent/state/tasks/*.json`
2. `.agent/state/*resume-state.json`
3. `.agent/state/handoffs/*.json`
4. `.agent/state/next-task.json`
5. rendered views in `.agent/tasks/`, `.agent/resume/`, `.agent/NEXT_TASK.md`
6. project fact files and summaries

Do not start from long chat history when canonical state exists.

### 3. Route to the right atomic capability
- For task extraction/update, follow `../task-extract/SKILL.md`
- For current project state summary, follow `../project-state/SKILL.md`
- For compact/resume summary, follow `../context-compact/SKILL.md`
- For audience-specific delivery, follow `../handoff-report/SKILL.md`

Use these as atomic modules under one runtime, not as separate products.

### 4. Use runtime references when execution needs infrastructure context
Read these references when relevant:
- `references/runtime-state.md`
- `references/runtime-risk-and-failure.md`
- `references/runtime-observability.md`
- `references/runtime-handoff.md`
- `references/runtime-deploy.md`

### 5. Keep product semantics unified
For all modes, preserve the same semantics for:
- canonical state
- next-task
- retrieval priority
- risk policy / escalation
- failure control
- heartbeat / observability
- resume / handoff inheritance

Do not fork behavior just because the surface is a skill.

## Packaging model

This skill is the **outer wrapper**.
The repository still depends on the runtime layer under:
- `scripts/`
- `.agent/state/`
- `.agent/loop/`
- `.agent/heartbeat/`
- `.agent/audit/`

Do not treat this skill as a text-only replacement for the runtime.

## Deployment rule

Deploy this repository in the following shape:
- `skills/long-chain-autonomy/` as the main entry skill
- existing atomic skills retained for reuse and internal routing
- runtime scripts and `.agent` structures retained as the execution substrate

## Safety rules

- Do not bypass canonical state when it exists.
- Do not let the unified skill erase risk/failure/heartbeat semantics.
- Do not collapse runtime checks into vague prose.
- Do not expose the wrapper as if it replaces the infrastructure layer.
