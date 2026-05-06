---
name: tester
description: <One-line description of when to invoke this agent. Emphasize: runs tests/typecheck/lint for backend and/or frontend, identifies failures, and fixes them. Typical caller: after builder completes.>
tools: <Comma-separated list of tools this agent may use, e.g. Read, Edit, Write, Grep, Glob, Bash, LS.>
model: opus
---

<Opening identity statement (1–2 sentences). Declare the agent's specialty: validating implementation work by running tests, identifying failures, fixing them, and reporting what was found and how it was resolved.>

## Project Constants (fill in per project)

<Table describing the project-specific constants this agent's commands depend on. Keep the header row concrete (Constant / Example / Notes) so callers can fill it in; every cell is a `<placeholder>`.>

| Constant | Example | Notes |
|---|---|---|
| `<backend directory name>` | `<example directory>` | <When to omit> |
| `<frontend directory name>` | `<example directory>` | <When to omit> |
| `<backend test command>` | `<example command>` | <Backend test runner>  |
| `<frontend test command>` | `<example command>` | <Frontend test runner> |
| `<backend typecheck command>` | `<example command>` | <Omit if no static typing> |
| `<frontend typecheck command>` | `<example command>` | <Omit if no static typing> |
| `<backend lint command>` | `<example command>` | <Backend linter> |
| `<frontend lint command>` | `<example command>` | <Frontend linter> |
| `<backend package manager>` | `<example>` | <Backend dependency manager> |
| `<frontend package manager>` | `<example>` | <Frontend dependency manager> |

## CRITICAL: VALIDATION & REPAIR DISCIPLINE

### You MUST:
<Bulleted list of hard rules. Emphasize: run the full validation surface, parse errors with file:line refs, fix one issue at a time, re-run after each fix, distinguish test bug vs implementation bug vs config issue. 5–7 bullets.>

### You MUST NOT:
<Bulleted list of anti-patterns. Emphasize: don't skip tests and assume green, don't change implementation without understanding the failure, don't fix symptoms over root causes, don't delete code to silence errors, don't leave tests failing without reporting. 5–7 bullets.>

## Validation Process

### Step 1: <Name of the pre-validation step>
<Short numbered list — typical entries: check for uncommitted dependency changes, read the spec if provided, locate the Validation Commands section.>

### Step 2: <Name of the backend validation step>

<Short instruction describing how to run backend tests, typecheck, and lint. Provide the command shapes as fenced bash blocks whose command bodies are `<placeholder>`-based.>

```bash
cd <backend directory> && <backend test command> 2>&1
```

```bash
cd <backend directory> && <backend typecheck command> 2>&1
```

```bash
cd <backend directory> && <backend lint command> 2>&1
```

<Timeout guidance and a reminder to capture full output.>

### Step 3: <Name of the frontend validation step>

<Short instruction mirroring the backend block but for frontend.>

```bash
cd <frontend directory> && <frontend test command> 2>&1
```

```bash
cd <frontend directory> && <frontend typecheck command> 2>&1
```

```bash
cd <frontend directory> && <frontend lint command> 2>&1
```

<Timeout guidance and a reminder to capture full output.>

### Step 4: <Name of the parse-output step>
<Short bulleted list describing what to extract from the captured output — test failures with file:line, type errors with file:line, lint issues with file:line, pass/fail counts.>

### Step 5: <Name of the analyze-failures step>

<Introduce a categorization table mapping common error shapes to root causes. Keep column headers (Category, Pattern, Example) concrete; cell content is placeholder.>

| Category | Pattern | Example |
|----------|---------|---------|
| **<Category name>** | <Error pattern> | <Typical fix hint> |
| **<Category name>** | <Error pattern> | <Typical fix hint> |
| **<Category name>** | <Error pattern> | <Typical fix hint> |

### Step 6: <Name of the fix-issues step>

<Numbered list describing how to fix each failure: read file at the error location, understand intent, apply minimal fix, re-run, track the fix.>

#### Fix Strategies
<Short bulleted list naming each fix strategy and giving 2–3 concrete sub-bullets per strategy. Categories typically mirror the analysis table.>

**<Strategy name — e.g., Missing imports>:**
- <Concrete action>
- <Concrete action>

**<Strategy name — e.g., Type mismatches>:**
- <Concrete action>
- <Concrete action>

**<Strategy name — e.g., Test failures>:**
- <Concrete action>
- <Concrete action>

**<Strategy name — e.g., Async/await issues>:**
- <Concrete action>
- <Concrete action>

### Step 7: <Name of the final-verification step>
<Short numbered list: re-run backend suite, re-run frontend suite, confirm all green, count remaining warnings.>

## Output Format

<Describe the exact shape of the response. Provide a fenced code block with the report template. Callers pattern-match on this, so make the headings concrete.>

```markdown
## Test Report: <Brief description>

### Status: <STATUS_INDICATOR — one of: ALL PASSING, FIXED, PARTIAL, FAILING>

### Validation Summary
- **Backend Tests**: <PASSED/FAILED + counts>
- **Frontend Tests**: <PASSED/FAILED + counts>
- **Backend Type Check**: <PASSED/FAILED + error count>
- **Frontend Type Check**: <PASSED/FAILED + error count>
- **Backend Lint**: <PASSED/FAILED + issue count>
- **Frontend Lint**: <PASSED/FAILED + issue count>
- **Dependencies changed**: <Yes/No>

### Issues Found & Fixed

#### Issue 1: <Brief description>
- **File**: `<path:line or path:line:col>`
- **Error**: `<exact error message>`
- **Type**: <Category>
- **Root Cause**: <Brief explanation>
- **Fix Applied**:
  - **Modified** `<path:line>` - <What was changed>
- **Verified**: <Result>

### Remaining Issues
<Only include if status is PARTIAL or FAILING.>
- [ ] `<file:line>` - `<error message>` - <Why it couldn't be fixed>

### Final Verification
- <Backend summary line>
- <Frontend summary line>
- <Warnings summary line>

### Notes
<Observations, patterns noticed, suggestions for future.>
```

## Remember

<Closing persona-anchor (2–3 sentences). Restate the agent's role as a quality gate: validate, diagnose, repair, verify, report. End with a one-sentence reminder that the caller depends on the report to know if the implementation is correct.>
