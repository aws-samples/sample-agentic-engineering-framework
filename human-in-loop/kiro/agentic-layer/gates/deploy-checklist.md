# Quality Gate: Before Deploy Phase

Verify readiness before running Phase 05 (Deploy).

## Checklist

- [ ] Branch is up to date with the target branch (`git pull --rebase origin main`)
- [ ] No merge conflicts after rebasing
- [ ] Test gate passed (Phase 03 completed with all steps passing)
- [ ] Review gate passed (Phase 04 completed with zero blockers)
- [ ] All previous gates are satisfied (no skipped gates)
- [ ] CI is passing on the current branch (if CI is configured)
- [ ] No uncommitted work-in-progress files in the working directory (`git status` is clean except for staged changes)

## Pass Criteria

All checkboxes must be checked before running the Deploy phase.

## If This Gate Fails

### If the branch is behind the target:

```
git fetch origin
git rebase origin/main
```

If there are merge conflicts, resolve them and re-run Phase 03 (Test) to verify nothing broke.

### If previous gates were not passed:

Go back to the earliest failing gate and resolve it. Do not skip gates. The order matters:

1. Test gate (Phase 03)
2. Review gate (Phase 04)
3. Deploy gate (this checklist)

### If CI is failing:

Check the CI logs for the failure. If it is a flaky test unrelated to your changes, note it in the PR description. If it is related to your changes, go back to the Build phase to fix it.
