# human-in-loop — Manual Agentic Development Workflow

A step-by-step workflow for building features using AI coding agents with quality gates between each phase. Use the agent configs from `agent-samples/` or run the prompts directly — no engine required.

## Structure

```
human-in-loop/
├── agentic-layer/
│   └── gates/                       # Quality gate checklists
│       ├── test-checklist.md
│       ├── review-checklist.md
│       └── deploy-checklist.md
├── index.html                       # Sample Vite app (demo target)
├── src/
├── public/
├── package.json
├── specs/                           # Plans go here (gitignored)
└── ai_docs/                         # Generated docs go here (gitignored)
```

## Prerequisites

- Any AI coding agent (Kiro CLI, etc.)
- Node.js 18+ (for the sample app)

## Quick Start with the Sample App

```bash
# Install the sample app
npm install
npm run dev
```

## The Workflow

Run each phase in order using the agents and prompts from `../agent-samples/`. Between phases with gates, review the checklist before proceeding.

### Setup: Install the Agents (optional)

Copy the agent configs into your project so you can switch between them:

```bash
mkdir -p .kiro/agents
cp ../agent-samples/agents/*.json .kiro/agents/
```

Then switch agents with `/agent plan`, `/agent build`, etc.

Or skip the agent configs and just paste the prompts directly.

### Phase 1: Plan

Use the **plan** agent/prompt to research the codebase and create an implementation plan.

```
/agent plan
```

Then provide your feature request. The agent will create a plan file in `specs/`.

Prompt reference: `../agent-samples/prompts/plan.md`

---

### Phase 2: Build

Use the **build** agent/prompt to execute the plan.

```
/agent build
```

Provide the path to the plan file from Phase 1. The agent reads the plan and implements it step by step.

Prompt reference: `../agent-samples/prompts/build.md`

---

### Phase 3: Test → Gate

Use the **test** agent/prompt to run the validation suite.

```
/agent test
```

The agent runs the project's tests and returns structured JSON results.

**Quality Gate**: Open `agentic-layer/gates/test-checklist.md` and verify every checkbox before proceeding. If the gate fails, the checklist includes remediation steps — fix the issues and re-run this phase.

---

### Phase 4: Review → Gate

Use the **review** agent/prompt to compare the implementation against the spec.

```
/agent review
```

The agent reads the spec and the code changes, then reports issues classified by severity.

**Quality Gate**: Open `agentic-layer/gates/review-checklist.md` and verify every checkbox. If blockers are found, fix them and re-run from Phase 2 (Build).

---

### Phase 5: Document

Use the **document** agent/prompt to generate documentation.

```
/agent document
```

The agent analyzes the code changes and creates a documentation file in `ai_docs/`.

Prompt reference: `../agent-samples/prompts/document.md`

---

### Phase 6: Deploy → Gate

Use the **deploy** agent/prompt to commit and create a PR.

```
/agent deploy
```

**Quality Gate**: Open `agentic-layer/gates/deploy-checklist.md` and verify every checkbox before merging.

---

## Gates

| Gate | When | What It Checks |
|------|------|----------------|
| `test-checklist.md` | After Phase 3 | All tests pass, no skipped tests, adequate coverage |
| `review-checklist.md` | After Phase 4 | Zero blockers, tech debt logged, no scope creep |
| `deploy-checklist.md` | Before Phase 6 | Branch up to date, previous gates passed, CI green |

## Customizing

- **Prompts**: Edit `../agent-samples/prompts/*.md` to change how each phase behaves
- **Agents**: Edit `../agent-samples/agents/*.json` to adjust tool permissions per phase
- **Gates**: Edit `agentic-layer/gates/*.md` to add project-specific checks

## Without Agent Configs

If you don't want to install the `.json` agent configs, you can run each phase by pasting the prompt content directly into your agent conversation. The prompts are in `../agent-samples/prompts/`.
