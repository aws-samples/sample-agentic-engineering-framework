#!/usr/bin/env python3
"""Task 11: Smoke-test Kiro headless subagent delegation.

Invokes pipeline-execute against a trivial one-phase implement spec and scans
the resulting log for subagent spawn markers. This is a runtime probe — run it
against a target project that has been through `tools/install.py`.

Usage:
  python tools/smoke_subagent.py <target-project>

Interpretation:
  - If the log shows subagent activation (e.g. "Spawning subagent: builder",
    "subagent_id=", "agent: builder"), Kiro's native fan-out works in headless
    → KEEP implement.md as-is, the prompt's `Task`/`subagent` delegation will
    be honored.
  - If the log shows no subagent activity but the implementation still got
    written, Kiro headless ignores subagent directives → FALL BACK to
    Python-driven phase-by-phase fan-out (see docstring below).

Fallback strategy (if smoke test fails):
  implement.md is rewritten to emit one line per phase:
      PHASE: <short description>
  The runner parses these markers, then invokes
      kiro-cli chat --agent builder "<per-phase implement prompt>"
  sequentially until all phases complete.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


FIXTURE_SPEC = """\
# Test Spec: add-sum-helper

## Goal
Add a tiny Python helper function `sum_two(a, b)` to a new file.

## Phase 1: write helper
Create file `smoke_sum.py` in the project root containing exactly:

```python
def sum_two(a, b):
    return a + b
```

## Success Criteria
- File `smoke_sum.py` exists
- Contains `def sum_two(a, b):`

## Validation Commands
- `python3 -c "from smoke_sum import sum_two; assert sum_two(2,3)==5"`
"""


_SUBAGENT_MARKERS = [
    re.compile(r"(?i)spawning\s+subagent"),
    re.compile(r"(?i)subagent[_\s-]*id\s*[:=]"),
    re.compile(r"(?i)delegating\s+to\s+builder"),
    re.compile(r"(?i)agent\s*:\s*builder"),
    re.compile(r"(?i)\[builder\]"),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="smoke_subagent")
    ap.add_argument("target", help="target project directory (must be installed)")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args(argv)

    target = Path(args.target).resolve()
    if not (target / ".kiro" / "agents" / "pipeline-execute.json").exists():
        print(f"FATAL: {target} has no .kiro/agents/pipeline-execute.json — run tools/install.py first",
              file=sys.stderr)
        return 1

    spec_path = target / ".kiro" / "smoke-spec.md"
    spec_path.write_text(FIXTURE_SPEC)
    prompt = (
        "You are implementing a trivial one-phase spec. The spec deliberately\n"
        "tests whether your subagent fan-out works in headless mode.\n\n"
        "Read the spec at `.kiro/smoke-spec.md` and implement its single phase\n"
        "by SPAWNING a `builder` subagent — do NOT write the file inline.\n"
        "Then verify the validation command. Report the log evidence of the\n"
        "subagent spawn on the FINAL line as: SUBAGENT_USED: yes|no\n"
    )
    log_path = target / ".developer" / "smoke-subagent.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[smoke] invoking pipeline-execute against {target}")
    try:
        proc = subprocess.run(
            ["kiro-cli", "chat", "--no-interactive", "--trust-all-tools",
             "--agent", "pipeline-execute", "--", prompt],
            cwd=str(target), capture_output=True, text=True, timeout=args.timeout,
        )
    except FileNotFoundError:
        print("FATAL: kiro-cli not on PATH", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print("FATAL: kiro-cli timed out", file=sys.stderr)
        return 3

    log_path.write_text(proc.stdout + "\n---STDERR---\n" + proc.stderr)
    print(f"[smoke] exit={proc.returncode} log={log_path}")

    self_reported = False
    for line in reversed(proc.stdout.splitlines()):
        m = re.match(r"\s*SUBAGENT_USED:\s*(yes|no)\s*$", line, re.I)
        if m:
            self_reported = m.group(1).lower() == "yes"
            break

    grep_hit = any(pat.search(proc.stdout) for pat in _SUBAGENT_MARKERS)
    file_written = (target / "smoke_sum.py").exists()

    print(f"[smoke] self_reported={self_reported} grep_hit={grep_hit} file_written={file_written}")
    if self_reported and grep_hit:
        print("[smoke] PASS — subagent delegation works in headless. Leave implement.md as-is.")
        return 0
    if file_written and not grep_hit:
        print("[smoke] FAIL — Kiro appears to ignore subagent directives in headless.")
        print("[smoke]        Activate Python-driven phase fan-out fallback.")
        return 10
    print("[smoke] INCONCLUSIVE — inspect the log manually.")
    return 20


if __name__ == "__main__":
    sys.exit(main())
