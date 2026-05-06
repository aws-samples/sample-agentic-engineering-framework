---
description: <One-line description of what this prompt does. State that it creates a focused, minimal patch plan to resolve a specific review issue — not the patch itself.>
---

# Patch Plan

<Opening framing paragraph (1–2 sentences). State that this prompt produces a focused patch plan to resolve a specific issue based on a `review_change_request`. Follow the `Instructions` to create a concise plan that addresses the issue with minimal, targeted changes. Point the reader to the `Variables`, `Instructions`, `Relevant Files`, and `Plan Format` sections below.>

## Variables

<List each variable this prompt accepts, mapped to its positional argument. Include required and optional slots; mark optional slots with a default or skip rule.>

task_id: $1
review_change_request: $2
spec_path: $3 <if provided, otherwise leave it blank>
agent_name: $4 <if provided, otherwise use a sensible default>
issue_screenshots: $5 <OPTIONAL — comma-separated list of screenshot paths if provided>

## Instructions

<Bulleted list of hard rules the patch-planner must follow. Preserve "IMPORTANT:" prefixes on the non-negotiables. Cover: the patch-planning-vs-patching boundary, the minimal-scope rule, reading the original spec for context, using `review_change_request` as the basis, examining issue screenshots if present, where the patch plan file lives and how it's named, how to base Validation on the original spec (with a fallback to the project's test sequence), the diff-awareness rule (run `git diff --stat` and use it to inform the plan), the reasoning quality bar, and the output contract. 10–14 bullets.>

- IMPORTANT: <State the patch-planning-vs-patching boundary — we write the plan; a separate agent applies it.>
- <Directive — read the original spec at `spec_path` (if provided) for context and requirements.>
- IMPORTANT: <Directive — use the `review_change_request` as the basis for the patch plan.>
- <Directive — examine `issue_screenshots` if provided to understand the visual context.>
- <Filename/location rule — create the patch plan in `specs/patch/` as `patch-task-{task_id}-{descriptive-name}.md`, where `{descriptive-name}` is a short kebab-case name derived from the issue.>
- IMPORTANT: <Scope-discipline directive — keep the patch minimal; address only the `review_change_request` and nothing more.>
- <Directive — run `git diff --stat` first; use the results to understand existing changes and inform the exact patch steps.>
- <Reasoning directive — think hard about the most efficient solution with minimal code changes.>
- <Validation directive — base `Plan Format: Validation` on the spec's validation steps when available; if any tests fail, the patch must fix them.>
- <Validation fallback directive — when no spec is provided, consult the project's test sequence (e.g., `.claude/commands/test.md: ## Test Sequence`) and derive validation commands from there.>
- <Placeholder-replacement rule — replace every `<placeholder>` in the `Plan Format` with concrete content.>
- IMPORTANT: <Output contract — return only the path to the patch plan file created and nothing else.>

## Relevant Files

<Short lead-in sentence telling the planner where to focus. Then a bulleted list of project-wide anchors (entry doc, backend/core source, frontend source, ai-implementation-docs index) with one-line purposes. Close with a reminder to ignore files unrelated to the patch.>

Focus on the following files:
- `<path/to/entry-doc>` - <Purpose>
- `<path/to/backend-or-core-source>` - <Purpose>
- `<path/to/frontend-source>` - <Purpose>

- <Directive — read `.claude/commands/ai-implementation-docs.md` to check if your task requires additional documentation.>
- <Directive — if your task matches any of the conditions listed, reference those documentation files to understand the context when creating the patch plan.>

<Closing one-liner telling the planner to ignore files unrelated to the patch.>

## Plan Format

<Preamble sentence stating this is the required shape for the patch plan. Remind the author that every `<placeholder>` must be replaced with concrete content.>

```md
# Patch: <concise patch title>

## Metadata
task_id: `<task_id>`
review_change_request: `<review_change_request>`

## Issue Summary
**Original Spec:** <spec_path>
**Issue:** <brief description of the review issue based on the `review_change_request`>
**Solution:** <brief description of the solution approach based on the `review_change_request`>

## Files to Modify
Use these files to implement the patch:

<List only the files that need changes — be specific and minimal.>

## Implementation Steps
IMPORTANT: Execute every step in order, top to bottom.

<2–5 focused steps to implement the patch. Each step is a concrete action. Include filenames and line-number references if existing code is being modified.>

### Step 1: <specific action>
- <implementation detail>
- <implementation detail>

### Step 2: <specific action>
- <implementation detail>
- <implementation detail>

<Continue as needed, but keep it minimal.>

## Validation
Execute every command to validate the patch is complete with zero regressions.

<1–5 specific commands or checks to verify the patch works correctly.>

## Patch Scope
**Lines of code to change:** <estimate>
**Risk level:** <low|medium|high>
**Testing required:** <brief description>
```

## Report

- IMPORTANT: <State the exact return contract — typically, return only the path to the patch plan file created and nothing else.>
