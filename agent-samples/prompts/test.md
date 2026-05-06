# Test

Execute the project's validation test suite and report results in structured JSON format. You run tests and report — you do not fix failures.

## Instructions

- Execute each test in the sequence defined by the project
- Always `cd` to the correct directory before each test
- If a test fails, stop immediately — do not run subsequent tests
- Capture stderr output for the error field on failure
- Timeout commands after 5 minutes
- Do NOT fix any failures — only report them
- Do NOT modify any source files

## Test Execution Sequence

Discover and run the project's configured tests in this standard order:

1. **Syntax Check** — Validate source files compile/parse without errors
2. **Linting** — Check for style violations, unused imports, potential bugs
3. **Unit Tests** — Run the project's unit test suite
4. **Type Check** — Run static type analysis (if applicable)
5. **Build** — Run the production build process

Adapt the specific commands to match the project's toolchain (e.g., `pytest`, `npm test`, `cargo test`, `tsc --noEmit`, etc.).

## Output

Return ONLY a JSON array — no additional text, explanations, or markdown. The output will be parsed with `JSON.parse()`.

Sort with failed tests (`passed: false`) at the top.

```json
[
  {
    "test_name": "string",
    "passed": true,
    "execution_command": "string — the exact command that was run",
    "test_purpose": "string",
    "error": "optional string — only present if passed is false"
  }
]
```
