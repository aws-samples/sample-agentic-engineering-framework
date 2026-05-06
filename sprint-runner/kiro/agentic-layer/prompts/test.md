# Application Validation Test Suite

<One-sentence framing of what the suite does and how results are returned. State that it runs validation checks across the relevant components (e.g., frontend, backend, infrastructure) and returns results in a standardized JSON format for automated processing.>

## Purpose

<Short lead sentence stating the proactive goal (e.g., "Identify and fix issues before they reach users or downstream agents"). Follow with a bulleted list of 3–5 capabilities the suite provides. Each bullet should name a concrete class of problem the suite catches.>
- <Category of issue detected, e.g., syntax errors, type mismatches, import failures>
- <Category of issue detected, e.g., broken tests, security vulnerabilities>
- <Category of issue detected, e.g., build failures, dependency problems, migration errors>
- <High-level outcome, e.g., "Ensure the application is in a healthy state">

## Variables

<Declare the named variables the prompt references below. Use `NAME: value` format, one per line. Typical variables include a command timeout and an absolute project root path. Add any project-specific variables the tests depend on (e.g., database paths, environment names).>

TEST_COMMAND_TIMEOUT: <timeout value, e.g., "5 minutes">
PROJECT_ROOT: <absolute path to the project root>

## Instructions

<Bulleted list of rules the executing agent must follow. Preserve the imperative tone and IMPORTANT callouts. Cover, in order: execution sequencing, result capture, output-format strictness (JSON-only, JSON.parse-ready), pass/fail field conventions, whether to continue after failures, error-handling rules (exit codes, stderr capture, timeout behavior, stop-on-first-failure policy), test dependencies, working-directory discipline, and any sub-agents that should be delegated to. Use nested bullets where a rule has sub-rules.>

- <Rule about executing tests in the sequence provided>
- <Rule about capturing pass/fail and error messages>
- IMPORTANT: <Rule constraining the output to JSON only>
  - IMPORTANT: <Sub-rule forbidding extra text, explanations, or markdown>
  - <Sub-rule stating the output will be parsed with JSON.parse()>
- <Rule about omitting the error field on pass>
- <Rule about including the error message on fail>
- <Rule about whether to execute all tests or stop early>
- Error Handling:
  - <Rule about non-zero exit codes>
  - <Rule about capturing stderr>
  - <Rule referencing `TEST_COMMAND_TIMEOUT`>
  - IMPORTANT: <Rule about stopping on first failure and returning partial results, if applicable>
- <Rule about inter-test dependencies>
- <Rule about ordering dependencies before dependents>
- <Rule about path resolution relative to the project root>
- <Rule about running `pwd`/`cd` before each test to guarantee the working directory>
- **For test running and fixing code during test**:
        - **<sub-agent name>**: <When and why to delegate to this sub-agent, and what context-window concern it protects>

## Test Execution Sequence

<Group the tests into subsections by category (e.g., Backend Tests, Frontend Tests, Infrastructure Tests). Each category becomes a `###` subsection containing a numbered list of tests. For each test, include a bolded title followed by four fixed sub-fields: Preparation Command, Command, test_name, test_purpose. Add an optional Note line when a test has special pass/fail semantics (e.g., threshold comparisons).>

### <Category 1 name, e.g., Backend Tests>

1. **<Test Title>**
   - Preparation Command: <Shell command that must run before the test, or `None`>
   - Command: <The exact shell command to execute, fully qualified with absolute paths>
   - test_name: "<snake_case identifier used in the JSON output>"
   - test_purpose: "<One sentence describing what the test validates and what class of errors it catches>"

2. **<Test Title>**
   - Preparation Command: <Shell command or `None`>
   - Command: <Exact shell command>
   - test_name: "<snake_case identifier>"
   - test_purpose: "<One sentence describing what is validated>"

3. **<Test Title>**
   - Preparation Command: <Shell command or `None`>
   - Command: <Exact shell command; for multi-line scripts embedded via `node -e`, `python -c`, etc., include the full script body here>
   - test_name: "<snake_case identifier>"
   - test_purpose: "<One sentence describing what is validated>"

4. **<Test Title with a custom pass threshold>**
   - Preparation Command: <Shell command or `None`>
   - Command: <Exact shell command, e.g., one that emits a count>
   - test_name: "<snake_case identifier>"
   - test_purpose: "<One sentence describing the baseline or threshold being enforced>"
   - Note: <Describe the non-standard pass/fail rule, e.g., "This test passes if the count is <= N. Report the count in the result.">

## Report

<Bulleted list governing the final output. Preserve the IMPORTANT callout. Cover: the JSON-array contract, sort order (failed tests first), whether to include passed tests, what the `execution_command` field is for (reproducibility by downstream agents), and any other output-shaping rules.>

- IMPORTANT: <Rule stating results are returned exclusively as a JSON array matching the `Output Structure` section>
- <Rule about sort order, e.g., failed tests at the top>
- <Rule about including both passed and failed tests>
- <Rule explaining what `execution_command` must contain and why>
- <Rule describing how downstream agents use the output>

### Output Structure

<Short lead-in describing the required JSON schema: one object per test, with the fields listed below. Note which fields are required and which are optional. Keep the fenced block tagged as `json`.>

```json
[
  {
    "test_name": "<string>",
    "passed": <boolean>,
    "execution_command": "<string>",
    "test_purpose": "<string>",
    "error": "<optional string — present only when passed is false>"
  },
  ...
]
```

### Example Output

<Short lead-in noting that a good example shows both a failed and a passed test so downstream parsers can see the error-field conventions. Keep the fenced block tagged as `json`.>

```json
[
  {
    "test_name": "<snake_case id of a failing test>",
    "passed": false,
    "execution_command": "<exact command that reproduces the failure>",
    "test_purpose": "<one-sentence purpose>",
    "error": "<captured error message, e.g., a compiler error or stderr excerpt>"
  },
  {
    "test_name": "<snake_case id of a passing test>",
    "passed": true,
    "execution_command": "<exact command that reproduces the check>",
    "test_purpose": "<one-sentence purpose>"
  }
]
```
