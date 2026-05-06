# <Sprint or Change Name> — E2E Validation

<Opening framing paragraph for the E2E doc. This file is a TEMPLATE that teams copy to
`.claude/commands/e2e/test_<descriptive_name>.md` and adapt per sprint. Every paragraph
and step below is a shape description — replace each angle-bracket slot with the
concrete content for your sprint.>

## Overview

<One to three sentences: what this test covers and at what layer (HTTP API,
CLI, UI, etc.). State the scope boundary — what this E2E proves, and what
it intentionally leaves to unit tests.>

## Prerequisites

<Bulleted list of binaries, runtimes, and services that must be present on
the machine before the test can run. Each entry is a placeholder — replace
with the specific dependencies your test requires.>

- `<package manager>`
- `<language runtime at the required version>`
- `<container tool, if the test uses local services>`
- `<cli tool for any external-service probing>`

## Environment Variables

<If the test depends on env vars (local credentials, endpoint URLs,
feature flags), list them in a fenced bash block. Keep values generic —
never real secrets. Delete this whole section if the test needs no env vars.>

```bash
export <VAR_1>=<value>
export <VAR_2>=<value>
```

---

## Steps

### 0. <Clean-State / Teardown-Any-Previous-Run step title>

**Input**:
```bash
<command to reset local state (optional — omit the fenced block entirely if there are no local services to tear down)>
```

**Expected output**: <what a clean teardown looks like>.
**Pass criterion**: <the specific observable that proves teardown succeeded>.

---

### 1. <Step title — e.g., install dependencies>

**Input**:
```bash
<exact command>
```

**Expected output**: <what successful output looks like — the key lines the
runner or a human will see>.
**Pass criterion**: <binary yes/no — exit code, specific substring, file
existence, HTTP status, etc.>.

---

### 2. <Step title — e.g., start local services>

**Input**:
```bash
<exact command>
```

**Expected output**: <what successful output looks like>.
**Pass criterion**: <binary yes/no>.

**Why**: <One-line rationale, only if the step is non-obvious (env glue,
permission repair, data seed). Delete this sub-bullet otherwise.>

---

### N. <Continue as needed — one step per observable>

<Each step follows the same shape: Input (bash block), Expected output,
Pass criterion. Add optional **Why** lines only when the step's existence
needs justification. Keep each step atomic — one command, one observable
outcome, one binary gate.>

---

### N+1. <Cleanup / Teardown step title>

**Input**:
```bash
<command to stop services, delete volumes, restore clean state>
```

**Expected output**: <what successful teardown looks like>.
**Pass criterion**: <exit code or state observation>.

---

## Final Pass/Fail Criterion

<Preamble sentence — the E2E passes if and only if ALL of the following are true. This list is the canonical gate the runner or reviewer checks; keep one bullet per Pass criterion above.>

1. <Specific, measurable criterion from step N>
2. <Specific, measurable criterion from step N>
3. <Additional criterion — one bullet per Pass criterion in the numbered steps above>

<Closing one-liner — any failure in the numbered list above means this E2E is NOT complete.>

---

## Quick Reference — Full Test Run

<Optional: a single fenced bash block that chains every step's Input
together so a human can copy-paste and run the whole suite. Keep it
identical to the steps above — if you add a step, add it here too.>

```bash
<command from step 0>
<command from step 1>
<command from step 2>
<...one line per step...>
<command from step N+1>
echo "<success sentinel>"
```
