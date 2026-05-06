---
description: <One-line description of what this prompt does. State that it runs the full application validation test suite and returns results in a standardized JSON format for automated processing.>
---

# Application Validation Test Suite

<Opening framing paragraph (1–2 sentences). State the goal: run validation checks across all application components and return results in a standardized JSON format for automated processing. Point the reader to the `Variables`, `Instructions`, `Test Execution Sequence`, and `Report` sections.>

## Purpose

<Short paragraph describing the role of the suite: identify and fix issues before they reach users or downstream agents. Use a bulleted list to enumerate the kinds of checks it provides.>

- <Kind of check — syntax errors, type mismatches, import failures>
- <Kind of check — broken tests and test regressions>
- <Kind of check — build failures, dependency problems, migration errors>
- <Kind of check — overall application health>

## Variables

<List each variable this prompt accepts. Include environment-style slots (timeouts, project root) with sensible defaults.>

TEST_COMMAND_TIMEOUT: <timeout value, e.g., "5 minutes">
PROJECT_ROOT: <absolute path to the project root>

## Instructions

<Bulleted list of hard rules the test runner must follow. Preserve "IMPORTANT:" prefixes on the non-negotiables. Cover: the fixed test sequence, per-test status/error capture, the output-purity rule (JSON only, parseable by `JSON.parse()`), the error-field convention (omit on pass, include on fail), no-early-exit, error-handling semantics (non-zero exits, stderr, timeouts), inter-test dependency handling, path resolution, and the subagent delegation guidance for diagnose-and-fix.>

- <Directive — execute tests in the sequence provided below.>
- <Directive — capture pass/fail status and error messages for each test.>
- IMPORTANT: <Return results exclusively as JSON matching the `Output Structure` schema.>
  - IMPORTANT: <Do NOT include extra text, explanations, or markdown — only the JSON object.>
  - <The output will be parsed with `JSON.parse()` by automated tooling.>
- <Directive — omit the error field when a test passes.>
- <Directive — include the error message when a test fails.>
- <Directive — execute all tests; do NOT stop early on the first failure.>
- <Error-handling sub-bullets:>
  - <Capture non-zero exit codes as failures.>
  - <Capture stderr output in the error field.>
  - <Respect `TEST_COMMAND_TIMEOUT` for long-running tests.>
  - IMPORTANT: <If a timeout occurs, return partial results with the timeout error in the affected test's error field.>
- <Inter-test dependency sub-bullets:>
  - <Order tests so dependencies run before dependents.>
  - <If a dependency fails, downstream tests may be skipped (note this in their error field).>
- <Path resolution sub-bullets:>
  - <Resolve all paths relative to `PROJECT_ROOT`.>
  - <Run `pwd` or `cd` before each test to guarantee the correct working directory.>
- <Sub-agent delegation sub-bullet:>
  - <When a test fails and you need to diagnose and fix it, delegate to a dedicated test-fixer sub-agent to protect the main context window.>

## Test Execution Sequence

<Preamble sentence — the categories below are illustrative. Adapt to your project's stack and validation needs. Keep the per-test fields (`test_name`, `test_purpose`, preparation command, command) consistent so the reporter can emit uniform JSON.>

### <Category — e.g., Backend Tests>

1. **<Test title — e.g., Unit Tests>**
   - Preparation Command: `<command to install deps or prepare fixtures, if any>`
   - Command: `<command to run the tests>`
   - test_name: "<snake_case test name>"
   - test_purpose: "<One-line purpose — what this test protects against.>"

2. **<Test title — e.g., Type Check>**
   - Preparation Command: <None / command>
   - Command: `<typecheck command>`
   - test_name: "<snake_case test name>"
   - test_purpose: "<One-line purpose.>"

3. **<Test title — e.g., Linting>**
   - Preparation Command: <None / command>
   - Command: `<lint command>`
   - test_name: "<snake_case test name>"
   - test_purpose: "<One-line purpose.>"

4. **<Test title — e.g., Build>**
   - Preparation Command: <None / command>
   - Command: `<build command>`
   - test_name: "<snake_case test name>"
   - test_purpose: "<One-line purpose.>"

### <Category — e.g., Frontend Tests>

<Same shape as above. One sub-bullet per check with preparation command, command, test_name, and test_purpose.>

### <Category — e.g., Infrastructure Tests>

<Same shape. Include only if the project has infrastructure-as-code to validate.>

## Report

<Preamble — output contract rules for downstream automation. Below are the required instructions for the reporter.>

- IMPORTANT: <Return results exclusively as a JSON object matching the `Output Structure` section.>
- <Rule — sort by status: failed tests first, then warnings, then passed tests.>
- <Rule — include both passed and failed tests.>
- <Rule — the `execution_command` field must contain the exact command to reproduce the test.>
- <Rationale — downstream agents use the output to identify failures and re-run specific tests.>

### Output Structure

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
