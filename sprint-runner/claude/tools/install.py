#!/usr/bin/env python3
"""Install the sprint-runner pipeline into a target repository.

Usage:
    python install.py <target> [--force] [--no-detect] [--dry-run]

Copies:
    <source>/.claude/                      -> <target>/.claude/
    <source>/tools/sprint_runner.py        -> <target>/tools/
    <source>/tools/pipeline_status_server.py -> <target>/tools/

Creates (empty):
    <target>/sprints/   <target>/specs/   <target>/research/   <target>/ai_docs/

Adapt pass:
    Invokes `claude -p` headless so Claude can read the target's manifests
    (package.json, pyproject.toml, Cargo.toml, go.mod, ...) and rewrite the
    <placeholder> tokens inside the installed prompts with commands that
    match this stack. Skip with --no-detect.

Flags:
    --force       overwrite an existing .claude/ or tools/<script>
    --no-detect   skip the Claude-driven adapt pass
    --dry-run     print actions without touching disk or calling Claude
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SELF_DIR = Path(__file__).resolve().parent          # tools/
PACKAGE_ROOT = SELF_DIR.parent                      # sprint-runner/claude/

SOURCE_CLAUDE_DIR = PACKAGE_ROOT / ".claude"
SOURCE_TOOLS_DIR = PACKAGE_ROOT / "tools"

TOOL_FILES = [
    "sprint_runner.py",
    "pipeline_status_server.py",
]

CONVENTION_DIRS = ["sprints", "specs", "research", "ai_docs"]

ADAPT_PROMPT = """\
You are adapting a freshly installed sprint-runner pipeline to this project's
tech stack. The pipeline was just copied into `.claude/` and `tools/`.

STEP 1 — DETECT STACK
Read any of these files that exist (ignore missing ones):
  package.json, pnpm-lock.yaml, yarn.lock, package-lock.json
  pyproject.toml, uv.lock, poetry.lock, requirements.txt, setup.py
  Cargo.toml, go.mod, Gemfile, pom.xml, build.gradle, build.gradle.kts
  Makefile, justfile, Taskfile.yml

From them, determine:
  - primary language(s)
  - package manager
  - test command (full non-interactive suite)
  - lint command
  - build command
  - typecheck command (if the stack has one)
  - format command
  - main source directory / package path

STEP 2 — REWRITE PROMPTS
Walk every `.md` file under:
  .claude/commands/
  .claude/commands/e2e/
  .claude/agents/

For each file, find angle-bracketed placeholder tokens — e.g.
  <test command>, <lint command>, <build command>, <typecheck command>,
  <format command>, <package path>, <source directory>, <package manager>
— and replace each with the concrete value for this project. Use the Edit
tool; preserve everything else in the file as-is.

If a token is ambiguous or you can't confidently resolve it, LEAVE IT and
note it in your final report rather than guessing.

STEP 3 — REPORT
Print a short bulleted summary:
  - detected language / package manager
  - the exact commands chosen for test / lint / build / format / typecheck
  - any placeholders you left unresolved and why

Do not modify files outside `.claude/`. Do not run tests or builds.
"""


# ─── IO helpers ───────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"[install] {msg}", flush=True)


def die(msg: str, code: int = 1) -> "NoReturn":
    print(f"[install] ERROR: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


# ─── Copy steps ───────────────────────────────────────────────────────────

def _ignore_caches(_dirname: str, entries: list[str]) -> list[str]:
    skip = {"__pycache__", ".pytest_cache", ".DS_Store"}
    return [e for e in entries if e in skip]


def install_claude_dir(target: Path, *, force: bool, dry: bool) -> None:
    dst = target / ".claude"
    if dst.exists():
        if not force:
            die(f"{dst} already exists; re-run with --force to overwrite")
        if dry:
            log(f"would remove existing {dst}")
        else:
            log(f"removing existing {dst}")
            shutil.rmtree(dst)

    if dry:
        log(f"would copy {SOURCE_CLAUDE_DIR} -> {dst}")
        return
    log(f"copying .claude/ -> {dst}")
    shutil.copytree(SOURCE_CLAUDE_DIR, dst, ignore=_ignore_caches)


def install_tool_scripts(target: Path, *, force: bool, dry: bool) -> None:
    dst_dir = target / "tools"
    if dry:
        log(f"would ensure {dst_dir}/ exists")
    else:
        dst_dir.mkdir(parents=True, exist_ok=True)

    for name in TOOL_FILES:
        src = SOURCE_TOOLS_DIR / name
        dst = dst_dir / name
        if not src.exists():
            die(f"missing source file: {src}")
        if dst.exists() and not force:
            die(f"{dst} already exists; re-run with --force to overwrite")
        if dry:
            log(f"would copy {src.name} -> {dst}")
            continue
        shutil.copy2(src, dst)
        log(f"copied {src.name} -> {dst}")


def create_convention_dirs(target: Path, *, dry: bool) -> None:
    for name in CONVENTION_DIRS:
        d = target / name
        if d.exists():
            continue
        if dry:
            log(f"would create {d}/")
            continue
        d.mkdir(parents=True, exist_ok=True)
        log(f"created {d}/")


# ─── Adapt pass ───────────────────────────────────────────────────────────

def run_adapt_pass(target: Path, *, dry: bool) -> None:
    if shutil.which("claude") is None:
        log("skipping adapt pass — `claude` CLI not on PATH "
            "(prompts retain <placeholder> tokens; agent can resolve at runtime)")
        return
    if dry:
        log("would run `claude -p` stack-detect + prompt-adapt pass")
        return

    log("running Claude stack-detect + prompt-adapt pass (takes ~1 min)...")
    try:
        result = subprocess.run(
            [
                "claude", "-p",
                "--permission-mode", "acceptEdits",
                ADAPT_PROMPT,
            ],
            cwd=str(target),
            check=False,
        )
    except FileNotFoundError:
        log("skipping adapt pass — `claude` CLI not available")
        return
    except Exception as exc:  # noqa: BLE001 — don't fail the install on adapt errors
        log(f"adapt pass failed: {exc!r} — prompts retain <placeholder> tokens")
        return

    if result.returncode != 0:
        log(f"adapt pass exited non-zero ({result.returncode}); "
            "some placeholders may remain — inspect .claude/commands/*.md")
    else:
        log("adapt pass complete")


# ─── Entrypoint ───────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", help="path to the target repository")
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing .claude/ or tools/<script>")
    parser.add_argument("--no-detect", action="store_true",
                        help="skip the Claude-driven stack adapt pass")
    parser.add_argument("--dry-run", action="store_true",
                        help="print actions without writing or calling Claude")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        die(f"target does not exist: {target}")
    if not target.is_dir():
        die(f"target is not a directory: {target}")
    if not (target / ".git").exists():
        log(f"warning: {target} is not a git repo — sprint_runner.py needs git at runtime")

    log(f"installing into {target}")
    install_claude_dir(target, force=args.force, dry=args.dry_run)
    install_tool_scripts(target, force=args.force, dry=args.dry_run)
    create_convention_dirs(target, dry=args.dry_run)

    if args.no_detect:
        log("skipped adapt pass (--no-detect); prompts retain <placeholder> tokens")
    else:
        run_adapt_pass(target, dry=args.dry_run)

    log("done.")
    log("next steps:")
    log(f"  cd {target}")
    log("  python tools/sprint_runner.py --list-sprints")
    log("  # drop a sprint brief under ./sprints/ then:")
    log("  python tools/sprint_runner.py --sprint 01")
    return 0


if __name__ == "__main__":
    sys.exit(main())
