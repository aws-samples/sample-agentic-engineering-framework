# Agentic Pipeline Runner

Project-agnostic orchestrator that drives an end-to-end SDLC pipeline
(Research → Plan → Build → Test → E2E → Review → Document → Commit → Publish)
on top of `kiro-cli chat --no-interactive --trust-all-tools`.

## Install order

1. **Authenticate Kiro** — `kiro-cli login` or export `KIRO_API_KEY=...`.
2. **Install into a target project**:
   ```
   python <agentic_pipeline>/tools/install.py <target-project>
   ```
   Add `--no-detect` to skip the tech-stack detect + adapt passes.
   Add `--force` to overwrite existing `.kiro/` files.
3. **Verify discovery**:
   ```
   cd <target-project>
   python tools/sprint_runner.py --list-sprints
   ```
4. **Run a sprint**:
   ```
   python tools/sprint_runner.py --sprint 03
   ```

## What the installer produces

```
<target>/
├── .kiro/
│   ├── agents/                 # pipeline-plan, pipeline-execute,
│   │                           # pipeline-execute-browser + builder/tester/
│   │                           # codebase-* (md + json manifests)
│   ├── prompts/                # all master prompts, stack-adapted by Task 5
│   ├── steering/               # pipeline.md + mcp-servers.md (minimal by design)
│   └── settings/mcp.json       # Playwright MCP entry
├── tools/
│   ├── sprint_runner.py        # the runner
│   └── pipeline.yaml           # paths + stack commands + cycle caps + timeouts
└── .developer/sprint-runs/     # per-run logs + state.json + RUNNING.lock
```

Installed steering is intentionally minimal (`pipeline.md`, `mcp-servers.md`).
Drop additional steering files into the target's `.kiro/steering/` after
install if a project needs more (e.g. design-system guides) — the installer
does not ship project-specific steering on purpose.

## `pipeline.yaml` reference

| Key | Meaning |
|---|---|
| `sprint_dir` | where sprint briefs live (`NN-<slug>.md`, `00-*` skipped) |
| `research_dir` / `specs_dir` / `patch_specs_dir` / `ai_docs_dir` / `e2e_dir` | output locations per stage |
| `runs_dir` | per-run logs + state under here (default `.developer/sprint-runs`) |
| `learnings_file` | append-only merge-conflict learnings |
| `agents.plan` / `agents.execute` / `agents.browser` | role-agent names (Amendment B) |
| `test_patch_max` (4) / `e2e_patch_max` (3) / `review_patch_max` (4) | self-healing cycle caps |
| `timeouts.*` | per-stage wall-clock seconds |
| `max_transient_retries` / `transient_backoff_base` / `transient_backoff_cap` | API-error retry policy |
| `stack.{lint,typecheck,build,test,e2e,package_manager,language,test_runner}` | filled by installer's detect pass; `"TODO:"` means "unset" |

## CLI

```
sprint_runner.py --sprint <selector>       # 03 | 03-08 | 03,07,11
                 --run-id <id>             # default: YYYYmmdd-HHMMSS
                 --resume <run_id>         # pick up where you left off
                 --resume-from <run>[:<sprint>[:<step>]]
                 --list-sprints
                 --dry-run                 # no Kiro calls, still writes state
                 --force-step <step>       # rerun one step even if cached
                 --config tools/pipeline.yaml
```

Resume/rewind examples:

```bash
# Resume unfinished sprints in a run
python tools/sprint_runner.py --resume 20260420-120000

# Rewind sprint 03 to the plan step and re-execute from there
python tools/sprint_runner.py --resume-from 20260420-120000:03:plan

# Force-rerun just the review step of the next sprint
python tools/sprint_runner.py --sprint 03 --force-step review
```

## KPI snapshot

```bash
python tools/kpi_report.py                  # newest run
python tools/kpi_report.py --all            # every run
python tools/kpi_report.py --format json    # dashboard piping
```

## Troubleshooting recipes

- **Something failed** — open `state.json`, jump to the first step with
  `"status":"failed"`, follow its `log_path`.
- **Transient retry churn** — `ls .developer/sprint-runs/<run>/*/*-retry-*`.
- **Patch-loop failures** — inspect
  `specs/patch/patch-sprint-<id>-{test,e2e,review}-<cycle>.md` plus the
  matching `<step>_patch-cycle-<N>.log` in the run dir.
- **Merge conflicts** — if the agent escalated, a `MERGE_CONFLICT.md` lives
  next to `merge-outcome.json` in the run's sprint subdir.
- **Stale heartbeat** — a `RUNNING.lock` whose `heartbeat_at` is stale by
  > 30s means the previous run crashed.

## Subagent smoke test

If Kiro's in-session subagent fan-out needs verification:

```bash
python <agentic_pipeline>/tools/smoke_subagent.py <target-project>
```

- Exit 0 → leave `implement.md` as-is; Kiro handles `Task`/`subagent` delegation.
- Exit 10 → switch `implement.md` to emit `PHASE:` markers and have the
  runner invoke `--agent builder` sequentially per phase (fallback path
  documented in `tools/smoke_subagent.py`).
