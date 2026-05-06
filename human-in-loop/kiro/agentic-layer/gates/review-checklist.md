# Quality Gate: After Review Phase

Review the verdict from Phase 04 before proceeding to Deploy.

## Checklist

- [ ] Zero blockers in the review verdict (`"blockers": 0`)
- [ ] Tech debt items are logged (copied to your issue tracker or backlog)
- [ ] Plan adherence verified (no unplanned changes flagged as scope creep)
- [ ] Security concerns addressed (no security-related findings at any severity)
- [ ] The `"success"` field in the verdict is `true`

## Pass Criteria

Zero blockers is the hard requirement. Tech debt and skippable items do not block, but tech debt must be logged somewhere so it is not silently ignored.

## If This Gate Fails

### If blockers were found:

Paste the blocker details back into your coding agent with the Build prompt:

```
The review found blockers that must be resolved before merging.
Here are the blocker findings:

<paste the issues array, filtered to severity "blocker">

For each blocker:
1. Read the file and line referenced
2. Understand what is wrong (see the description)
3. Apply the suggested fix
4. Verify the fix does not break existing tests

After fixing all blockers, re-run Phase 03 (Test) and Phase 04 (Review).
```

### If scope creep was flagged:

Review the unplanned changes. Either:
- Remove them if they are truly out of scope
- Update the plan to include them if they are necessary for the task

Then re-run Phase 04 (Review).
