---
description: <One-line description of what this prompt does. State that it creates a bug-fix plan (not the fix itself) and emphasizes root-cause analysis and targeted, minimal resolution with parallel codebase research.>
---

# Bug Planning

<Opening framing paragraph (1–2 sentences). State that the prompt produces a new plan to resolve a `Bug` using the specified markdown `Plan Format`. Point the reader to the `Instructions`, `Process`, and `Relevant Files` sections. Make clear we are planning the fix, not performing it.>

## Variables

<Numbered or key:value list of inputs this prompt accepts from the invoker. Each slot should name the variable, the positional argument it maps to (`$1`, `$2`, ...), and a short description of the expected value. Typical slots: a task identifier and a structured payload describing the bug (plain text or a path to a .md/.txt file).>

task_id: $1
task_input: $2 <(plain text description OR path to a local .md/.txt file)>

## Instructions

<Bulleted list of hard rules the planning agent must follow. Preserve "IMPORTANT:" prefixes on rules that are easy to violate. Cover, at minimum: the planning-not-fixing boundary, the output file location and naming convention, the requirement to replace every `<placeholder>` in the `Plan Format`, the reasoning quality bar, how to handle ambiguity, phase ordering, citation discipline (`file:line`), context-window protection via subagents, scope discipline (surgical fix, minimal changes), any UI/E2E-specific branch, and the fallback when arguments are empty. Aim for 10–15 bullets, one imperative each.>

- IMPORTANT: <Planning-vs-fixing boundary — we're writing a plan; we are NOT resolving the bug.>
- <Output location + filename convention — create the plan in `specs/` as `task-{task_id}-sdlc_planner-{descriptive-name}.md`, where `{descriptive-name}` is a short kebab-case name derived from the bug.>
- <Directive — use the `Plan Format` below as the required shape.>
- IMPORTANT: <Replace every `<placeholder>` in the `Plan Format` with concrete content.>
- <Reasoning directive — think hard about root cause and fix steps.>
- <Skepticism directive — verify assumptions against actual code; don't accept claims at face value.>
- <No-open-questions rule — resolve all ambiguities before writing.>
- <Phase-ordering rule — each phase depends only on prior phases; Phase 1 has zero dependencies on new code.>
- IMPORTANT: <Scope-discipline directive — be surgical; solve only the bug at hand.>
- IMPORTANT: <Minimal-change directive — we want the minimal number of changes that will fix the bug.>
- <Research-first rule — investigate existing patterns, architecture, and conventions before planning.>
- <Citation rule — use specific `file:line` references throughout the plan.>
- <Context-window rule — delegate heavy searching to subagents.>
- IMPORTANT: <UI/E2E branch — when the bug affects UI or user interactions: add a task in `Step by Step Tasks` to create a separate E2E test file at `.claude/commands/e2e/test_<descriptive_name>.md` based on `.claude/commands/e2e/test_example.md`; add E2E test validation to the `Validation Commands` section; add an instruction in `Relevant Files` to read `.claude/commands/e2e/test_example.md`; list the new E2E test file in `New Files`. Clarify we are planning the E2E test, not writing it.>
- <Input-resolution fallback — what to do when `$ARGUMENTS` is empty and `task_input` is missing (use available context to infer; abort with an error if nothing can be determined).>

## Process

<Short lead-in sentence describing the three-phase process. Then three `###` subsections with numbered steps (bolded titles + sub-bullets).>

### Phase 1: <Name of the context-gathering phase>

<Numbered list of steps the planner takes to orient. Typical steps: resolve the input into a usable bug description, read every referenced file fully in the main context before spawning subagents, pull in project-wide contextual docs, and identify symptoms (expected vs actual behavior, reproduction steps).>

1. **<Step title — e.g., resolve input>**:
   - <Sub-action — if `task_input` is a file path (`.md`/`.txt`), read the file for bug details>
   - <Sub-action — if `task_input` is plain text, use it directly>
   - <Sub-action — incorporate any additional context from `$ARGUMENTS`>
   - <Sub-action — if no bug can be determined, abort with an error>

2. **<Step title — e.g., read all mentioned files FULLY>**:
   - <Category — bug description / task input>
   - <Category — project entry doc>
   - <Category — logs or stack traces referenced in the bug report>
   - <Category — `.claude/commands/ai-implementation-docs.md` for additional documentation hints>
   - <Anti-pattern reminder — do NOT spawn subagents before reading key files yourself>

3. **<Step title — e.g., read contextual docs>**:
   - <Sub-action — check `.claude/commands/ai-implementation-docs.md` for docs matching this bug area>
   - <Sub-action — include matched docs in the plan's `Relevant Files` section>

4. **<Step title — e.g., understand the symptoms>**:
   - <Sub-action — identify expected vs actual behavior>
   - <Sub-action — derive reproduction steps>

### Phase 2: <Name of the investigation / root-cause phase>

<Numbered list of steps that trace the bug to its source. Emphasize parallel subagent use, waiting for completion, re-reading findings into main context, and pinpointing the exact `file:line` where behavior diverges.>

1. **<Step title — e.g., spawn parallel subagents for research>**:
   - **codebase-locator** — <Investigation goal — find files related to the bug (error messages, stack traces, affected components)>
   - **codebase-analyzer** — <Investigation goal — understand involved code paths; trace the bug's likely execution flow with `file:line` references>
   - **codebase-pattern-finder** — <Investigation goal — find similar bug fixes or error-handling patterns to model after>
   - <Optional project-specific locator — e.g., find prior plans, tests that should have caught this, or related prior bugs>

2. **<Step title — e.g., wait for ALL subagents to complete>**

3. **<Step title — e.g., read all files identified>** into main context

4. **<Step title — e.g., determine root cause>** — <what "done" looks like: a single `file:line` naming the origin where behavior diverges>

### Phase 3: <Name of the plan-development / review phase>

<Numbered list of steps that produce and validate the plan artifact. Typical steps: develop the plan sequentially on the investigation findings, fill every placeholder, resolve ambiguities with documented rationale, write the file using the naming convention, and verify the plan is complete.>

1. **<Step title — e.g., develop the plan>** sequentially on the investigation findings

2. **<Step title — e.g., ensure all placeholders are filled>** with concrete content

3. **<Step title — e.g., resolve any ambiguities>** — <how to decide and where to document the rationale (typically the `Notes` section)>

4. **<Step title — e.g., create the plan file>** in `specs/` with the naming convention

5. **<Step title — e.g., verify the plan is complete>**:
   - <Completeness check — no `<placeholder>` tags remain>
   - <Accuracy check — `file:line` references resolve>
   - <Clarity check — no open questions remain>
   - <Executability check — validation commands are specific and runnable>

## Relevant Files

<Short lead-in sentence telling the planner where to focus. Then a bulleted list of project-wide anchors (entry doc, backend/core source, frontend source, ai-implementation-docs index) with one-line purposes. Close with a reminder to ignore files unrelated to the bug.>

Focus on the following files:
- `<path/to/entry-doc>` - <Purpose — project overview and instructions>
- `<path/to/backend-or-core-source>` - <Purpose — core source code>
- `<path/to/frontend-source>` - <Purpose — frontend source, if applicable>
- <Directive — read `.claude/commands/ai-implementation-docs.md` to check if the task requires additional documentation>

<Closing one-liner telling the planner to ignore files unrelated to the bug.>

## Bug

<Describe where the bug details come from. Typical: extract from the `task_input` variable (read file if path, use text directly otherwise). Then include a line that expands the positional arguments so free-form bug descriptions also flow through.>

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
task_id: `{task_id}`
task_input: `{task_input}`

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

- `<test command>` - <What passing proves>
- `<typecheck command>` - <What passing proves>
- `<build command>` - <What passing proves>
- `<lint command>` - <What passing proves>
- `<e2e command>` - Runner-owned; do NOT gate a phase on this

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
