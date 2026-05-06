---
description: <One-line description of what this prompt does. State that it validates the implementation against its spec — runs tests, checks types, and verifies behavior.>
---

# Test & Validate

<Opening framing paragraph (1–2 sentences). State the goal: validate the implementation against its spec, run existing tests, write new ones as needed, and verify behavior. Point the reader to the `Purpose`, `Instructions`, `Test Sequence`, and `Report Format` sections below.>

## Variables

<List each variable this prompt accepts, mapped to its positional argument. Typical: a single path to the spec file that drives validation.>

spec_file: $1

## Purpose

<Short paragraph describing the role of the suite: ensure the implementation satisfies the spec's requirements before marking a phase or sprint complete. Bulleted list enumerating what the suite provides.>

- <Check — verifies all tests pass with zero regressions>
- <Check — checks types and catches errors before runtime>
- <Check — validates behavior matches spec requirements>
- <Check — confirms edge cases and failure modes are handled>
- <Check — ensures build succeeds across all components>

## Instructions

<Numbered list of the validation steps. Typical steps: read the spec to understand what was built, run existing project tests (detecting stack automatically), run each phase's validation command from the spec, check for type/syntax/import errors, test edge cases described in the spec, and report structured results.>

1. <Step — read the spec to understand what was built.>
2. <Step — run existing project tests (detect stack automatically).>
3. <Step — run each phase's validation command from the spec.>
4. <Step — check for type errors, syntax errors, import failures.>
5. <Step — test edge cases described in the spec.>
6. <Step — report structured results in the `Report Format` below.>

## Variables

<Second variables block capturing environment-style slots used during execution. Include timeout and project-root defaults.>

TEST_COMMAND_TIMEOUT: <timeout value, e.g., "5 minutes">
PROJECT_ROOT: <absolute path to the project root>
spec_file: $1

## Test Sequence

<Preamble — execute tests in the ordered sequence below. The categories are illustrative; adapt to your project's stack.>

1. <Step — backend validation: run tests, typecheck, lint, build; parse errors and results.>
2. <Step — frontend validation: run tests, typecheck, lint, build; parse errors and results.>
3. <Step — spec validation: run each phase's validation command from the spec.>
4. <Step — edge cases: test boundaries and failure modes from the spec.>

### <Backend Test Commands>

<Fenced block listing the canonical command shape for backend checks. Adapt to your project. Each line is a command template; everything in angle brackets is a placeholder.>

```
cd <PROJECT_ROOT>/<backend directory> && <test command>
cd <PROJECT_ROOT>/<backend directory> && <typecheck command>
cd <PROJECT_ROOT>/<backend directory> && <lint command>
cd <PROJECT_ROOT>/<backend directory> && <build command>
```

<Closing one-liner — parse output for error lines and test results.>

### <Frontend Test Commands>

<Fenced block listing the canonical command shape for frontend checks. Adapt to your project. Each line is a command template; everything in angle brackets is a placeholder.>

```
cd <PROJECT_ROOT>/<frontend directory> && <test command>
cd <PROJECT_ROOT>/<frontend directory> && <typecheck command>
cd <PROJECT_ROOT>/<frontend directory> && <lint command>
cd <PROJECT_ROOT>/<frontend directory> && <build command>
```

<Closing one-liner — parse output for error lines (typical compiler error format: `file.ext:line:col: error: message`) and test results.>

## Report Format

<Preamble — results are reported as structured markdown AND a machine-readable JSON object. The markdown is for humans; the JSON is consumed by `tools/sprint_runner.py` and must match the schema exactly.>

### Markdown Report

<Preamble — fill each section with concrete pass/fail counts and per-test details. Keep the shape below; adapt labels to your stack.>

```markdown
## Test Results

### Summary
- Backend Tests: X passed, X failed <pass/fail indicator>
- Frontend Tests: X passed, X failed <pass/fail indicator>
- Backend Type Check: <pass/fail indicator>
- Frontend Type Check: <pass/fail indicator>
- Backend Lint: <pass/fail indicator>
- Frontend Lint: <pass/fail indicator>

### Backend Validation
- tests: <pass/fail> (X passed, X failed)
- typecheck: <pass/fail> (X errors)
- lint: <pass/fail> (X issues)

### Frontend Validation
- tests: <pass/fail> (X passed, X failed)
- typecheck: <pass/fail> (X errors)
- lint: <pass/fail> (X issues)

### Spec Validation
- Phase 1 (<name>): <pass/fail> <details>
- Phase 2 (<name>): <pass/fail> <details>

### Edge Cases
- <case>: <pass/fail> <details>

### Failures (if any)
<For each failure:>
- **Test:** <name>
- **File:** <path>:<line>
- **Expected:** <what should happen>
- **Actual:** <what happened>
- **Suggestion:** <where to look for the fix>
```

### JSON Output

<Preamble — the JSON object below is the required schema. `build_succeeded`, `tests_passed`, `tests_executed`, `errors_count`, `warnings_count`, `errors[]`, and `summary` are required top-level fields. This schema is consumed by `tools/sprint_runner.py` and must not be changed without updating the parser.>

```json
{
  "build_succeeded": <boolean>,
  "tests_passed": <boolean>,
  "tests_executed": <integer>,
  "errors_count": <integer>,
  "warnings_count": <integer>,
  "errors": [
    {
      "file": "<path/to/file.ext>",
      "line": <integer>,
      "message": "<error message>"
    }
  ],
  "summary": "<one-line summary of validation results>"
}
```

### Example Output

<Preamble — illustrative example showing a realistic structured response. Use placeholder paths only; do not leak real project details.>

```json
{
  "build_succeeded": true,
  "tests_passed": false,
  "tests_executed": <integer>,
  "errors_count": <integer>,
  "warnings_count": <integer>,
  "errors": [
    {
      "file": "<path/to/file.ext>",
      "line": <integer>,
      "message": "<error message>"
    }
  ],
  "summary": "<one-line summary>"
}
```

## Rules

<Bulleted list of hard rules the validator must follow. Cover: thoroughness, failure-detail discipline, report-but-don't-fix (fixes belong to patch agents), full-suite execution (not just new code), and parallelization where safe.>

- <Rule — be thorough; missed bugs become production issues.>
- <Rule — report failures with enough detail to fix them.>
- <Rule — do NOT fix bugs yourself; only report them.>
- <Rule — run ALL tests, not just the ones for new code.>
- <Rule — run backend and frontend validations in parallel when possible.>
