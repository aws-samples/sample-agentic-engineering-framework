# human-in-loop — Manual Agentic Development Workflow (Claude Code)

A step-by-step workflow for building features with [Claude Code](https://claude.com/claude-code) using quality gates between each phase. Install the prompts from [`../../agent-samples/prompts/`](../../agent-samples/prompts/) as custom slash commands in `.claude/commands/` — or paste them directly into a session. No orchestrator.

This is the Claude-native twin of the Kiro implementation at [`../kiro/`](../kiro/). Same workflow, same gates, same prompts — swapped to use Claude Code's custom slash command primitive.

## Structure

```
human-in-loop/claude/
├── .claude/
│   └── commands/                    # Custom slash commands (installed from agent-samples/prompts)
│       ├── plan.md
│       ├── build.md
│       ├── test.md
│       ├── review.md
│       ├── document.md
│       └── deploy.md
├── agentic-layer/
│   └── gates/                       # Quality gate checklists (copy from ../kiro/)
│       ├── test-checklist.md
│       ├── review-checklist.md
│       └── deploy-checklist.md
├── specs/                           # Plans go here (gitignored)
└── ai_docs/                         # Generated docs go here (gitignored)
```

## Prerequisites

- [Claude Code](https://claude.com/claude-code) installed and authenticated
- Node.js 18+ (if you use the sample app from [`../kiro/`](../kiro/))

## Quick Start

```bash
# From this directory, install the shared prompts as Claude Code custom commands
mkdir -p .claude/commands
cp ../../agent-samples/prompts/*.md .claude/commands/

# Optional: copy the gate checklists from the kiro sample
mkdir -p agentic-layer/gates
cp ../kiro/agentic-layer/gates/*.md agentic-layer/gates/

# Launch Claude Code
claude
```

Once installed, each prompt becomes a slash command in Claude Code: `plan.md` → `/plan`, `build.md` → `/build`, etc.

## The Workflow

Run each phase in order by invoking the slash command. Between phases with gates, open the checklist and verify every box before proceeding.

### Phase 1: Plan

```
/plan <feature description>
```

Claude researches the codebase and writes an implementation plan to `specs/`. Prompt source: [`../../agent-samples/prompts/plan.md`](../../agent-samples/prompts/plan.md).

---

### Phase 2: Build

```
/build specs/<plan-file>.md
```

Claude reads the plan and implements it phase by phase. Prompt source: [`../../agent-samples/prompts/build.md`](../../agent-samples/prompts/build.md).

---

### Phase 3: Test → Gate

```
/test
```

Claude runs the project's test suite and returns a structured JSON report.

**Quality Gate**: Open [`agentic-layer/gates/test-checklist.md`](../kiro/agentic-layer/gates/test-checklist.md) and verify every checkbox. If anything fails, the checklist includes a remediation prompt — paste it back into Claude and re-run `/test`.

---

### Phase 4: Review → Gate

```
/review specs/<plan-file>.md
```

Claude compares the implementation against the spec and reports issues by severity.

**Quality Gate**: Open [`agentic-layer/gates/review-checklist.md`](../kiro/agentic-layer/gates/review-checklist.md). If blockers exist, fix them and loop back to Phase 2.

---

### Phase 5: Document

```
/document
```

Claude analyzes the diff and writes a documentation file to `ai_docs/`. Prompt source: [`../../agent-samples/prompts/document.md`](../../agent-samples/prompts/document.md).

---

### Phase 6: Deploy → Gate

```
/deploy
```

Claude stages the commit and prepares the PR message.

**Quality Gate**: Open [`agentic-layer/gates/deploy-checklist.md`](../kiro/agentic-layer/gates/deploy-checklist.md) and verify every box before merging.

---

## Gates

| Gate | When | What It Checks |
|------|------|----------------|
| `test-checklist.md` | After Phase 3 | All tests pass, no skipped tests, adequate coverage |
| `review-checklist.md` | After Phase 4 | Zero blockers, tech debt logged, no scope creep |
| `deploy-checklist.md` | Before Phase 6 | Branch up to date, previous gates passed, CI green |

## Customizing

- **Prompts**: Edit the files in [`../../agent-samples/prompts/`](../../agent-samples/prompts/) to change how each phase behaves. Re-copy them into `.claude/commands/` to pick up changes (or edit the installed copies directly if you've diverged).
- **Gates**: Edit `agentic-layer/gates/*.md` to add project-specific checks.
- **Project scope**: Install `.claude/commands/` inside a repo to make commands project-local, or copy to `~/.claude/commands/` to make them available globally.

## Without Installing Commands

If you don't want to register slash commands, paste the body of any prompt from [`../../agent-samples/prompts/`](../../agent-samples/prompts/) directly into the Claude Code conversation. Same workflow — just without the `/` shortcut.

## Why Human-in-the-Loop

Each phase stops at a review boundary and hands control back to you. There is no orchestrator auto-advancing between steps. You control the pace — stop between any two phases, edit the spec, re-plan, or bail entirely. If you want an unattended pipeline instead, see [`../../sprint-runner/claude/`](../../sprint-runner/claude/).
