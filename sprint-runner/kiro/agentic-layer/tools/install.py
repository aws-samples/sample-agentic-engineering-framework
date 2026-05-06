#!/usr/bin/env python3
"""Install the agentic pipeline into a target project.

Usage:
  python tools/install.py <target-project> [--force] [--no-detect]

- Scaffolds .kiro/{agents,prompts,steering,settings}
- Copies prompts/*.md → .kiro/prompts/
- Converts agents/<name>.md → .kiro/agents/<name>.{md,json} manifests
- Writes role agents: pipeline-plan, pipeline-execute, pipeline-execute-browser
- Writes .kiro/settings/mcp.json (Playwright)
- Writes .kiro/steering/pipeline.md
- Copies tools/sprint_runner.py and renders tools/pipeline.yaml
- Optionally runs Kiro detect+adapt passes (Tasks 4/5)
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

# Agents whose tools we need to rewrite for Kiro subagent runtime.
_SUBAGENT_TOOL_OVERRIDES = {
    "codebase-locator": ["fs_read", "execute_bash"],
    "codebase-analyzer": ["fs_read", "execute_bash"],
    "codebase-pattern-finder": ["fs_read", "execute_bash"],
}

# Map Claude-style tool names to Kiro tool names.
_TOOL_MAP = {
    "read": "fs_read", "edit": "fs_write", "write": "fs_write",
    "grep": "grep", "glob": "glob",
    "bash": "execute_bash", "ls": "execute_bash",
    "todowrite": "todo_list",
}


def parse_frontmatter(md: str) -> tuple[dict, str]:
    """Extract YAML-ish frontmatter (between --- markers) and body."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md, flags=re.DOTALL)
    if not m:
        return {}, md
    front_raw, body = m.group(1), m.group(2)
    front: dict = {}
    for line in front_raw.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        front[k.strip()] = v.strip()
    return front, body


def convert_agent_tools(name: str, raw_tools: str) -> list[str]:
    if name in _SUBAGENT_TOOL_OVERRIDES:
        return _SUBAGENT_TOOL_OVERRIDES[name]
    out: list[str] = []
    seen: set[str] = set()
    for t in re.split(r"[,\s]+", raw_tools.strip()):
        key = t.lower().strip()
        if not key:
            continue
        mapped = _TOOL_MAP.get(key, key)
        if mapped not in seen:
            seen.add(mapped)
            out.append(mapped)
    return out


def build_agent_json(name: str, description: str, tools: list[str],
                     target: Path) -> dict:
    md_abs = (target / ".kiro" / "agents" / f"{name}.md").resolve()
    return {
        "name": name,
        "description": description,
        "prompt": f"file://{md_abs}",
        "tools": tools,
    }


def role_agent_json(name: str, description: str, mcp_servers: dict,
                    target: Path) -> dict:
    """Build a pipeline-* role agent JSON with subagent fan-out support."""
    sub_whitelist = [
        "builder", "test-runner",
        "codebase-locator", "codebase-analyzer", "codebase-pattern-finder",
    ]
    steer_abs = (target / ".kiro" / "steering" / "pipeline.md").resolve()
    agent: dict = {
        "name": name,
        "description": description,
        "prompt": f"file://{steer_abs}",
        "tools": ["fs_read", "fs_write", "execute_bash", "grep", "glob",
                  "code", "subagent", "todo_list"],
        "toolsSettings": {
            "crew": {
                "availableAgents": sub_whitelist,
                "trustedAgents": sub_whitelist,
            }
        },
    }
    if mcp_servers:
        agent["mcpServers"] = mcp_servers
    return agent


STEERING_PIPELINE_MD = """# Pipeline Role Agent

You are a pipeline role agent driving one stage of an automated SDLC pipeline
(Research → Plan → Build → Test → E2E → Review → Document → Commit → Publish).

## Stage outputs — emit machine-readable markers on the FINAL line

Every stage must end with a single-line marker the runner parses:

- Research: `RESEARCH_PATH: <absolute path>`
- Plan: one `SPEC_PATH: <abs>` per spec, then `E2E_PATH: <abs>`
- Build: `BUILD_SUMMARY: <one-sentence description>`
- Test/E2E/Review result files: JSON at the path the runner named

## Self-healing contract

Test (4 cycles), E2E (3), and Review (4) are self-healing. The runner passes
prior-cycle context; propose a DIFFERENT root cause each cycle.

## Subagent delegation

Use the `subagent` tool to fan out to `builder` (per phase) and `codebase-*`
(during research/planning). Do not Read/Write source files inline in the main
session when a subagent can handle it — context preservation is mandatory.

## MCP servers are load-bearing — do NOT disable them

See `mcp-servers.md` (same folder) for the full rule, the four config scopes
Kiro resolves (global / project / agent / runtime), and the precedence gotcha
where project `.kiro/settings/mcp.json` can override an agent-level enable.

Short version: every MCP server must stay `"disabled": false` in every scope.
Fix environmental causes (registry, node, missing package, port conflict) —
never toggle the flag to work around a failing run.
"""

STEERING_MCP_SERVERS_MD = """# MCP Servers — Never Disable, Never Edit to Work Around

The pipeline depends on MCP servers (notably Playwright) being live for every
e2e / test / review stage. Disabling any of them to "unblock" a failing run
silently breaks the next cycle: the agent falls back to ad-hoc `/tmp/*.mjs`
scripts, those scripts hit pnpm resolution quirks or missing browser binaries,
and the self-healing patch loop wastes cycles diagnosing phantom test failures
instead of the real environmental cause.

## The rule

Every MCP server listed in any of the four locations below MUST stay
`"disabled": false`. If one is failing, fix the **environmental** cause
(registry auth, node version, missing package, port in use) — do NOT toggle
the flag.

## Where the configs live (MCP resolution order)

Kiro resolves MCP servers by merging these files, with later entries able to
override earlier ones:

| Scope    | Path                                                         | Purpose                                             |
|----------|--------------------------------------------------------------|-----------------------------------------------------|
| Global   | `~/.kiro/settings/mcp.json`                                  | User-level defaults across all projects             |
| Project  | `<repo>/.kiro/settings/mcp.json`                             | Project-level settings — **overrides global**       |
| Agent    | `<repo>/.kiro/agents/<agent>.json` → `mcpServers` block      | Per-agent servers for that agent only               |
| Runtime  | CLI flag `--require-mcp-startup`                             | Forces the run to fail fast if a declared server isn't reachable |

**Precedence gotcha:** project `.kiro/settings/mcp.json` can silently override
a server that the agent config declared as enabled. If the agent config says
`"disabled": false` but the project settings say `"disabled": true`, the
server will NOT start. Always check both.

## Before every pipeline stage — verify

```bash
# All four must show "disabled": false (or omit the flag entirely)
jq '.mcpServers' ~/.kiro/settings/mcp.json
jq '.mcpServers' .kiro/settings/mcp.json
jq '.mcpServers' .kiro/agents/pipeline-execute-browser.json
jq '.mcpServers' .kiro/agents/pipeline-execute.json
```

If any show `"disabled": true`, flip to `false` and commit the fix alongside
whatever environmental repair you made.

## Self-healing coverage

`tools/sprint_runner.py::_ensure_mcp_enabled` sweeps all three
settings-file scopes before every pipeline invocation: the agent config
(`.kiro/agents/<agent>.json`), the project settings (`.kiro/settings/mcp.json`),
and the global settings (`~/.kiro/settings/mcp.json`). Any `"disabled": true`
it finds is flipped back to `false` and logged as
`⚡ re-enabled MCP server '<name>' in <path>`. Runtime-scope enforcement is
via the `--require-mcp-startup` CLI flag the runner passes on e2e/test/review
stages, which makes a failed MCP startup fail the attempt loudly instead of
degrading to no tools.

## Diagnosing an MCP startup failure

When an e2e/test/review attempt logs `Playwright MCP tools are not available`
or `browser_* tools missing`:

1. Confirm the package is installable: `npx -y @playwright/mcp@latest --help`.
2. Check all four config scopes above — the agent is loading a disabled one.
3. Check for a port/socket conflict from a zombie MCP server process:
   `pgrep -fl "@playwright/mcp"` and kill stragglers.
4. Verify browser binaries are present: `pnpm exec playwright install chromium`.
5. If all four check out and it still fails, rerun with `--require-mcp-startup`
   so the failure is loud rather than silent.

NEVER respond to an MCP failure by editing a config to `"disabled": true`.
That response is explicitly prohibited by this steering file and by
`pipeline.md`.
"""

PIPELINE_PLAN_DESC = (
    "Pipeline role agent for research, plan, and merge-conflict stages. "
    "No browser MCP. Delegates heavy reading to codebase-* subagents and "
    "spec writing to builder subagents."
)
PIPELINE_EXECUTE_DESC = (
    "Pipeline role agent for build, document, and commit stages. "
    "No browser MCP. Delegates phase implementation to builder subagents."
)
PIPELINE_EXECUTE_BROWSER_DESC = (
    "Pipeline role agent for test, e2e, and review stages. "
    "Loads Playwright MCP for browser automation."
)

MCP_JSON = {
    "mcpServers": {
        "playwright": {
            "command": "npx",
            "args": ["-y", "@playwright/mcp@latest"],
            "disabled": False,
            "autoApprove": [],
        }
    }
}


DETECT_PROMPT = """\
You are auditing a project to determine its development tech stack.

Read the project manifest files present at the repo root (whichever exist):
  package.json, pnpm-lock.yaml, yarn.lock, package-lock.json,
  pyproject.toml, uv.lock, poetry.lock, requirements.txt,
  Cargo.toml, go.mod, Gemfile, composer.json.

Infer these values and emit EXACTLY ONE single-line marker on the FINAL line
of your response. No prose after it. JSON must be valid and on one line.

STACK_JSON: {"language":"...","package_manager":"...","lint":"...","typecheck":"...","build":"...","test":"...","e2e":"...","test_runner":"..."}

Field rules:
- language: one of "typescript","javascript","python","rust","go","ruby","php","unknown"
- package_manager: "pnpm","npm","yarn","uv","pip","poetry","cargo","go","bundler","composer","unknown"
- lint/typecheck/build/test/e2e: the EXACT shell command a developer would run.
  Use "" (empty string) if not applicable.
- test_runner: the framework name ("vitest","jest","pytest","cargo test","go test", etc.) or "".

If any field is truly unknowable from the project files, use "" — do NOT guess.
"""

STACK_KEYS = ("language", "package_manager", "lint", "typecheck",
              "build", "test", "e2e", "test_runner")


def parse_stack_json(stdout: str) -> dict | None:
    """Extract STACK_JSON marker from Kiro stdout."""
    # Scan from bottom up, first match wins (handles multi-turn).
    for line in reversed(stdout.splitlines()):
        m = re.match(r"^\s*STACK_JSON:\s*(\{.*\})\s*$", line)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                return None
    return None


def run_kiro_detect(target: Path, timeout: int = 600) -> dict | None:
    """Invoke kiro-cli in target as cwd and parse STACK_JSON. Returns None on failure."""
    try:
        proc = subprocess.run(
            ["kiro-cli", "chat", "--no-interactive", "--trust-all-tools",
             "--agent", "pipeline-plan", "--", DETECT_PROMPT],
            cwd=str(target), capture_output=True, text=True, timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"[install] detect pass skipped: {e}")
        return None
    if proc.returncode != 0:
        print(f"[install] detect pass exit={proc.returncode}; leaving TODO: sentinels")
        return None
    return parse_stack_json(proc.stdout)


def merge_stack_into_yaml(yaml_path: Path, stack: dict) -> None:
    """Rewrite the `stack:` block in pipeline.yaml with detected values.

    Only replaces lines under a top-level `stack:` key whose value is still
    "TODO:" (preserves human-authored overrides).
    """
    lines = yaml_path.read_text().splitlines()
    out: list[str] = []
    in_stack = False
    for line in lines:
        if not in_stack and re.match(r"^stack:\s*$", line):
            in_stack = True
            out.append(line)
            continue
        if in_stack:
            # Leave block at the next top-level key or EOF
            if line and not line.startswith(" ") and ":" in line:
                in_stack = False
                out.append(line)
                continue
            m = re.match(r"^(\s+)([a-z_][a-z0-9_]*):\s*\"TODO:\"\s*$", line)
            if m and m.group(2) in stack and stack[m.group(2)] is not None:
                indent, key = m.group(1), m.group(2)
                val = str(stack[key]).replace('"', '\\"')
                out.append(f'{indent}{key}: "{val}"')
                continue
        out.append(line)
    yaml_path.write_text("\n".join(out) + "\n")


_ADAPT_TARGETS = (
    ".kiro/prompts/test.md",
    ".kiro/prompts/test_e2e.md",
    ".kiro/prompts/plan-feature.md",
    ".kiro/prompts/plan-bug.md",
    ".kiro/prompts/plan-task.md",
    ".kiro/prompts/patch.md",
)


def _adapt_prompt_text(stack: dict) -> str:
    def _fmt(k: str) -> str:
        v = stack.get(k, "")
        return v if v else "(not applicable — drop this step)"
    return (
        "You are adapting prompt templates to this project's tech stack.\n\n"
        "DETECTED STACK (authoritative):\n"
        + json.dumps(stack, indent=2) + "\n\n"
        "For EACH of the following files, read it, then use your `write` tool to\n"
        "rewrite ONLY the stack-sensitive commands so they match the detected stack.\n\n"
        "Files to adapt (paths relative to project root):\n"
        + "".join(f"  - {p}\n" for p in _ADAPT_TARGETS)
        + "\nTarget command mapping:\n"
        f"  lint      → {_fmt('lint')}\n"
        f"  typecheck → {_fmt('typecheck')}\n"
        f"  build     → {_fmt('build')}\n"
        f"  test      → {_fmt('test')}\n"
        f"  e2e       → {_fmt('e2e')}\n\n"
        "Rules — read carefully:\n"
        "1. Preserve every heading, section, list structure, JSON schema example,\n"
        "   and placeholder like $ARGUMENTS, $1..$9, {run_id}, {issue_id}.\n"
        "2. Replace hardcoded toolchain commands with the mapped equivalents above.\n"
        "   Example: 'pnpm lint' → the lint command; 'pytest' → the test command.\n"
        "3. If a stack field is empty, drop that validation step cleanly\n"
        "   instead of emitting an empty command.\n"
        "4. Do NOT rename files. Do NOT add new files. Do NOT edit the master\n"
        "   copies under prompts/ (only .kiro/prompts/*).\n"
        "5. Do NOT touch positional-arg syntax or variable names.\n"
        "6. Preserve all Markdown fenced-code examples of JSON schemas verbatim.\n\n"
        "On the FINAL line of your final message, emit exactly:\n"
        "  ADAPT_DONE: <comma-separated list of relative paths you modified>\n"
    )


def run_kiro_adapt(target: Path, stack: dict, timeout: int = 900) -> bool:
    """Invoke Kiro to rewrite stack-sensitive commands in .kiro/prompts/*.

    Returns True on success (ADAPT_DONE marker present), False otherwise.
    """
    try:
        proc = subprocess.run(
            ["kiro-cli", "chat", "--no-interactive", "--trust-all-tools",
             "--agent", "pipeline-plan", "--", _adapt_prompt_text(stack)],
            cwd=str(target), capture_output=True, text=True, timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"[install] adapt pass skipped: {e}")
        return False
    if proc.returncode != 0:
        print(f"[install] adapt pass exit={proc.returncode}")
        return False
    for line in reversed(proc.stdout.splitlines()):
        if re.match(r"^\s*ADAPT_DONE:", line):
            return True
    print("[install] adapt pass: no ADAPT_DONE marker found")
    return False


def emit_install_diff(target: Path) -> None:
    """Write a unified diff of .kiro/prompts/* vs master prompts/ into install-diff.patch."""
    import difflib
    master = TEMPLATE_ROOT / "prompts"
    out_lines: list[str] = []
    for rel in _ADAPT_TARGETS:
        installed = target / rel
        master_file = master / installed.name
        if not installed.exists() or not master_file.exists():
            continue
        a = master_file.read_text().splitlines(keepends=True)
        b = installed.read_text().splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            a, b, fromfile=f"prompts/{installed.name}",
            tofile=rel, n=3))
        out_lines.extend(diff)
    patch_path = target / "install-diff.patch"
    patch_path.write_text("".join(out_lines))
    if out_lines:
        sys.stdout.write("".join(out_lines))
    print(f"[install]   wrote diff → {patch_path}")


def ensure_gitignore_entry(target: Path, entry: str) -> None:
    """Append `entry` to target/.gitignore (create if missing). Idempotent."""
    gi = target / ".gitignore"
    if gi.exists():
        lines = gi.read_text().splitlines()
        if entry in (line.strip() for line in lines):
            return
        sep = "" if gi.read_text().endswith("\n") else "\n"
        gi.write_text(gi.read_text() + sep + entry + "\n")
    else:
        gi.write_text(entry + "\n")


def install(target: Path, force: bool = False, no_detect: bool = False) -> int:
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    kiro = target / ".kiro"
    for sub in ("agents", "prompts", "steering", "settings"):
        (kiro / sub).mkdir(parents=True, exist_ok=True)
    (target / "tools").mkdir(parents=True, exist_ok=True)

    # --- copy prompts ---
    src_prompts = TEMPLATE_ROOT / "prompts"
    for p in sorted(src_prompts.glob("*.md")):
        dst = kiro / "prompts" / p.name
        if dst.exists() and not force:
            continue
        shutil.copyfile(p, dst)

    # --- copy + convert agents ---
    src_agents = TEMPLATE_ROOT / "agents"
    for p in sorted(src_agents.glob("*.md")):
        front, body = parse_frontmatter(p.read_text())
        name = front.get("name") or p.stem
        description = front.get("description", "")
        tools = convert_agent_tools(name, front.get("tools", "read,write,shell"))
        md_dst = kiro / "agents" / f"{name}.md"
        json_dst = kiro / "agents" / f"{name}.json"
        if not md_dst.exists() or force:
            md_dst.write_text(body.lstrip())
        if not json_dst.exists() or force:
            json_dst.write_text(json.dumps(
                build_agent_json(name, description, tools, target), indent=2) + "\n")

    # --- role agents ---
    playwright_mcp = {
        "playwright": {
            "command": "npx",
            "args": ["-y", "@playwright/mcp@latest"],
            "disabled": False,
        }
    }
    role_specs = [
        ("pipeline-plan", PIPELINE_PLAN_DESC, {}),
        ("pipeline-execute", PIPELINE_EXECUTE_DESC, {}),
        ("pipeline-execute-browser", PIPELINE_EXECUTE_BROWSER_DESC, playwright_mcp),
    ]
    for name, desc, mcp_servers in role_specs:
        json_dst = kiro / "agents" / f"{name}.json"
        if not json_dst.exists() or force:
            json_dst.write_text(json.dumps(
                role_agent_json(name, desc, mcp_servers, target), indent=2) + "\n")

    # --- steering + mcp.json ---
    steer_dst = kiro / "steering" / "pipeline.md"
    if not steer_dst.exists() or force:
        steer_dst.write_text(STEERING_PIPELINE_MD)
    mcp_steer_dst = kiro / "steering" / "mcp-servers.md"
    if not mcp_steer_dst.exists() or force:
        mcp_steer_dst.write_text(STEERING_MCP_SERVERS_MD)
    mcp_dst = kiro / "settings" / "mcp.json"
    if not mcp_dst.exists() or force:
        mcp_dst.write_text(json.dumps(MCP_JSON, indent=2) + "\n")

    # --- runner + pipeline.yaml ---
    runner_src = TEMPLATE_ROOT / "tools" / "sprint_runner.py"
    runner_dst = target / "tools" / "sprint_runner.py"
    if not runner_dst.exists() or force:
        shutil.copyfile(runner_src, runner_dst)
        runner_dst.chmod(0o755)
    dashboard_src = TEMPLATE_ROOT / "tools" / "pipeline_dashboard.py"
    dashboard_dst = target / "tools" / "pipeline_dashboard.py"
    if dashboard_src.exists() and (not dashboard_dst.exists() or force):
        shutil.copyfile(dashboard_src, dashboard_dst)
        dashboard_dst.chmod(0o755)
    yaml_src = TEMPLATE_ROOT / "tools" / "pipeline.yaml.template"
    yaml_dst = target / "tools" / "pipeline.yaml"
    if not yaml_dst.exists() or force:
        shutil.copyfile(yaml_src, yaml_dst)

    # --- .gitignore: pipeline + editor + playwright artifacts ---
    for entry in (
        "tsconfig.tsbuildinfo",
        ".playwright-mcp/",
        ".kiro/settings/lsp.json",
        ".claude/",
    ):
        ensure_gitignore_entry(target, entry)

    print(f"[install] target={target}")
    print(f"[install]   .kiro/ scaffolded (agents={len(list((kiro/'agents').glob('*.json')))})")
    print(f"[install]   tools/sprint_runner.py + tools/pipeline.yaml written")
    if no_detect:
        print("[install]   --no-detect: skipping stack detection + adapt passes")
        return 0
    print("[install]   detecting tech stack via Kiro (this can take a minute)...")
    stack = run_kiro_detect(target)
    if stack:
        merge_stack_into_yaml(yaml_dst, stack)
        print(f"[install]   stack detected: {stack}")
        print("[install]   adapting prompts to stack...")
        if run_kiro_adapt(target, stack):
            emit_install_diff(target)
        else:
            print("[install]   adapt pass failed — .kiro/prompts/ left as-is")
    else:
        print("[install]   stack detection failed or ambiguous — pipeline.yaml has TODO: sentinels")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="install")
    ap.add_argument("target", help="target project directory")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--no-detect", action="store_true",
                    help="skip Kiro stack detection + adapt passes")
    args = ap.parse_args(argv)
    return install(Path(args.target), args.force, args.no_detect)


if __name__ == "__main__":
    sys.exit(main())
