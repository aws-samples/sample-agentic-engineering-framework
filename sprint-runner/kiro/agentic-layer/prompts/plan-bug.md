---
description: <One-line description of what this prompt does. State that it creates a bug-fix plan (not the fix itself) and emphasizes root-cause analysis and targeted, minimal resolution.>
---

# Bug Planning

<Opening framing paragraph (1–2 sentences). State that the prompt produces a new plan to resolve a `Bug` using the specified markdown `Plan Format`. Point the reader to the `Instructions`, `Process`, and `Relevant Files` sections. Make clear we are planning the fix, not performing it.>

## Variables

<Numbered or key:value list of inputs this prompt accepts from the invoker. Each slot should name the variable, the positional argument it maps to (`$1`, `$2`, ...), and a short description of the expected value. Typical slots: an issue identifier and a structured payload describing the bug.>

issue_id: $1
issue_json: $2

## Instructions

<Bulleted list of hard rules the planning agent must follow. Preserve "IMPORTANT:" prefixes on rules that are easy to violate. Cover, at minimum: the planning-not-fixing boundary, the output file location and naming convention, the requirement to replace every `<placeholder>` in the `Plan Format`, the reasoning quality bar, how to handle ambiguity, phase ordering, citation discipline (`file:line`), context-window protection via subagents, scope discipline (surgical fix, minimal changes), any UI/E2E-specific branch, and the fallback when arguments are empty. Aim for 10–15 bullets, one imperative each.>

- IMPORTANT: <State the planning-vs-fixing boundary.>
- <Describe where to write the plan and the filename convention, including how to derive the descriptive suffix.>
- <Point to the `Plan Format` as the required shape for the plan.>
- IMPORTANT: <Require every `<placeholder>` in the `Plan Format` to be replaced with real content.>
- <Reasoning-quality directive — e.g., think hard about root cause and fix steps.>
- <Verification directive — e.g., be skeptical, confirm claims against actual code.>
- <Directive forbidding open questions in the final plan.>
- <Phase-ordering directive — each phase depends only on prior phases; Phase 1 has no dependencies on new code.>
- <Citation directive — use `file:line` references throughout.>
- <Context-protection directive — delegate heavy searching to subagents.>
- IMPORTANT: <Scope-discipline directive — stay surgical, fix only the bug at hand.>
- IMPORTANT: <Minimal-change directive.>
- <Any style rules for the plan itself — e.g., no decorators, keep it simple.>
- <Dependency-management directive — how to add libraries and where to document them.>
- IMPORTANT: <UI/E2E branch: when the bug affects UI, add a task for a new E2E test file, wire E2E validation into the plan, and list the relevant reference files in `Relevant Files` / `New Files`. Clarify we are planning the E2E test, not writing it.>
- <Fallback behavior when arguments and structured inputs are both missing.>

## Process

<Describe the planning process as a series of phases, each introduced by a `###` sub-header. Preserve the three-phase shape: context gathering, investigation / root cause, and plan development / review. Under each phase, use a numbered list where each item has a **bolded title** and 1–4 sub-bullets of concrete actions.>

### Phase 1: <Name of the context-gathering phase>

<Numbered list of steps the planner takes to orient. Typical steps: resolve the input into a usable bug description, read every referenced file fully in the main context before spawning subagents, pull in project-wide contextual docs, and identify symptoms (expected vs actual behavior, reproduction steps).>

1. **<Step title — e.g., "Resolve input">**:
   - <Sub-action describing how to parse or branch on the inputs>
   - <Sub-action for the structured-input path>
   - <Sub-action for the abort-on-missing path>

2. **<Step title — e.g., "Read all mentioned files FULLY">**:
   - <Category of file to read, e.g., bug description>
   - <Category of file to read, e.g., logs / stack traces>
   - <Category of file to read, e.g., project README>
   - <Anti-pattern reminder — e.g., do NOT spawn subagents before reading key files yourself>

3. **<Step title — e.g., "Read contextual docs">**:
   - <Pointer to project-wide implementation-doc index>
   - <Directive to include any matched docs in the plan's Relevant Files>

4. **<Step title — e.g., "Understand the symptoms">**:
   - <Sub-action — identify expected vs actual behavior>
   - <Sub-action — derive reproduction steps>

### Phase 2: <Name of the investigation / root-cause phase>

<Numbered list of steps that trace the bug to its source. Emphasize parallel subagent use, waiting for completion, re-reading findings into main context, and pinpointing the exact `file:line` where behavior diverges.>

1. **<Step title — e.g., "Spawn parallel subagents">**:
   - <Investigation goal — find involved code paths>
   - <Investigation goal — locate the divergence point with `file:line`>
   - <Investigation goal — find related tests that should have caught this>
   - <Investigation goal — find similar prior bugs or patterns>

2. **<Step title — e.g., "Wait for ALL subagents to complete">**

3. **<Step title — e.g., "Read all files identified">**

4. **<Step title — e.g., "Determine root cause">** — <what "done" looks like for this step, e.g., a single `file:line` naming the origin>

### Phase 3: <Name of the plan-development / review phase>

<Numbered list of steps that produce and validate the plan artifact. Typical steps: develop the plan sequentially on the investigation findings, fill every placeholder, resolve ambiguities with documented rationale, write the file using the naming convention, and verify the plan is complete.>

1. **<Step title — e.g., "Develop the plan">**

2. **<Step title — e.g., "Ensure all placeholders are filled">**

3. **<Step title — e.g., "Resolve any ambiguities">** — <how to decide and where to document the rationale>

4. **<Step title — e.g., "Create the plan file">** — <reference back to the naming convention>

5. **<Step title — e.g., "Verify the plan">**:
   - <Completeness check — no `<placeholder>` tags remain>
   - <Accuracy check — `file:line` references resolve>
   - <Clarity check — no open questions remain>
   - <Executability check — validation commands are specific and runnable>

## Relevant Files

<Short lead-in sentence telling the planner where to focus. Then a bulleted list of top-level files and directories that provide project context, each with a one-line purpose. Close with a reminder to ignore files unrelated to the bug.>

Focus on the following files:
- `<path/or/glob>` - <One-line purpose, e.g., project overview>
- `<path/or/glob>` - <One-line purpose, e.g., build and run scripts>
- `<path/or/glob>` - <One-line purpose, e.g., workflow automation scripts>
- <Pointer to any implementation-doc index the planner should consult>

<One-line reminder to ignore files unrelated to the bug.>

## Bug

<Describe how the planner extracts the bug details from the inputs declared in `Variables`. Mention the structured-input path (parsing the JSON payload, using specific fields like title/body) and then surface `$ARGUMENTS` as a passthrough for free-form invocations.>

$ARGUMENTS

## Plan Format

The markdown block below is a **starter template**, not a rigid contract. Teams adopting this prompt are expected to reshape it to match their incident-response conventions, tooling, and review culture. The default below is opinionated on purpose — copy it, then adapt.

**What must stay (invariants).** Downstream prompts (`implement.md`, `patch.md`, `review.md`) read bug-fix plans for a small set of anchors. If you rename or remove these, update the downstream prompts in the same change:

- A title heading for the plan
- A `## Root Cause Analysis` section with `file:line` references tracing trigger to symptom — the reviewer and patch-loop use this to verify the fix addresses the cause, not the symptom
- A `## Steps to Reproduce` section — the test/e2e phase uses these to verify the bug is no longer reproducible
- One or more `## Phase N: <name>` sections, each with a `### Success Criteria:` checklist of runnable commands — the build/patch loop iterates by phase number; the first phase's success should confirm the bug no longer reproduces
- A `## Validation Commands` section listing executable commands — re-run by review and patch phases
- A `## Relevant Files` section — consumed by the builder and reviewer as the authoritative file manifest
- `file:line` citation discipline throughout

**What is safe to change.** Section naming (outside the invariants above), section ordering, the Testing Strategy / Regression Tests shape, acceptance criteria formatting, metadata fields, notes/references structure, code-block languages, and whether you use checkboxes or prose. If your team tracks postmortems separately, drop the Notes section. If you want a dedicated `## Blast Radius` section, add one. Keep the invariants wired; everything else is yours.

**Before shipping template changes, update in lockstep:** `prompts/implement.md` (consumes phase Success Criteria), `prompts/patch.md` (targets specific phases by number), `prompts/review.md` (compares implementation against the plan shape).

### Default template

Use this as-is until you have a reason to change it. Replace every `<placeholder>` with concrete content.

```markdown
# Bug Fix: [Bug Name]

## Metadata
issue_id: `{issue_id}`
run_id: `{run_id}`
issue_json: `{issue_json}`

## Overview
<1–3 sentences: the bug, its impact, and user-facing symptoms.>

## Current State Analysis
<Short paragraph describing observed symptoms, errors, and affected code paths. Ground every claim in the codebase.>

### Key Discoveries:
<3–6 findings, each with a `file:line` reference.>
- <Finding with `path/to/file.ext:line`>
- <Finding with `path/to/file.ext:line`>

## Root Cause Analysis
<Trace the code path from trigger to symptom with `file:line` references. This is the core of the plan.>

## Steps to Reproduce
<Ordered, unambiguous steps to trigger the bug.>

## Desired End State
<Correct behavior after the fix, plus how to verify.>

## What We're NOT Doing
<Out-of-scope items — no refactoring tangents, no "while we're here" changes.>

## Fix Approach
<High-level strategy and why it was chosen over alternatives.>

## Relevant Files
Use these files to fix the bug:
<Bullets of existing files relevant to the fix, each with a one-line reason.>

### New Files
<Bullets of new files to create, each with its purpose. Omit if none.>

---

## Phase 1: [Descriptive Name]

IMPORTANT: Execute every step in order, top to bottom.

### Overview
<1–2 sentences: what this phase accomplishes.>

### Changes Required:
<Numbered change groups. Each group: `**File**`, `**Changes**`, fenced code block. 1–3 groups per phase.>

#### 1. [Component/File Group]
**File**: `<path/to/file.ext>`
**Changes**: <One-line summary>

```<language>
<Specific code to add or modify>
```

### Success Criteria:
<2–5 runnable checks. Include test / typecheck / build commands as applicable.>

- [ ] Tests pass: `<test command>`
- [ ] Type checking passes: `<typecheck command>`
- [ ] Build succeeds: `<build command>`

**Implementation Note**: After completing this phase, run all automated verification checks before proceeding.

---

## Phase 2: [Descriptive Name]
<Same shape as Phase 1. First Success Criterion should confirm the bug is no longer reproducible via Steps to Reproduce.>

---

[Add more phases only if the fix genuinely requires them. Most bug fixes need 1–2 phases.]

---

## Testing Strategy

### Regression Tests:
<Tests that prove the bug is fixed and guard adjacent code.>
- <Named test file or case>

### E2E Tests (if UI bug):
<If UI: describe the E2E test artifact to create, the minimal steps it validates, and any screenshot expectations. Omit otherwise.>

## Acceptance Criteria
<Final user-visible conditions for the fix to be accepted.>

- [ ] Bug is no longer reproducible following Steps to Reproduce
- [ ] Root cause is addressed, not just symptoms
- [ ] No regressions introduced
- [ ] All validation commands pass with zero errors

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

<Runnable commands — tests, typechecks, builds, reproduction-before-and-after. If an E2E test was created, include a line to read the project's E2E runner doc and then read and execute the new E2E test file.>

- `<command>` - <What passing proves>
- `<command>` - <What passing proves>

## References
<Key code locations the fix hinges on.>
- Root cause location: `<file:line>`
- Related code: `<file:line>`
- Similar past fix: `<file:line>` (if applicable)

## Notes
<Additional context, workarounds, ambiguity rationale, or tech debt.>
```

## Report

- IMPORTANT: <State the exact return contract — typically, return only the path to the plan file created and nothing else.>
