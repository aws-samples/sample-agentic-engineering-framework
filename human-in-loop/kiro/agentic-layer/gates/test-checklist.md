# Quality Gate: After Test Phase

Review the test results from Phase 03 before proceeding to Review.

## Checklist

- [ ] All test steps passed (syntax, lint, unit tests, type check, build)
- [ ] Zero test failures in the unit test step
- [ ] No skipped tests (skipped tests hide broken functionality)
- [ ] Coverage is adequate for the changes made (if coverage was reported)
- [ ] No snapshot regressions (if the project uses snapshot testing)
- [ ] Test output contains no unexpected warnings

## Pass Criteria

All checkboxes must be checked to proceed to the Review phase.

## If This Gate Fails

Do not proceed to Review. Instead, paste the failure details back into your coding agent with this resolve prompt:

```
The test phase reported failures. Here are the results:

<paste the JSON test report here>

Diagnose the root cause of each failure. For each one, determine:
1. Is this a test bug (wrong assertion)?
2. Is this an implementation bug (code does not match the plan)?
3. Is this an integration issue (change broke an adjacent module)?

Fix the issues one at a time. After each fix, re-run the full test suite.
Do not fix multiple issues in a single edit. Do not weaken assertions
to make tests pass.

After fixing, re-run Phase 03 (Test) to verify.
```

Then re-run the Test phase (Phase 03) and re-evaluate this gate.
