#!/usr/bin/env python3
"""Print KPI snapshot(s) from sprint_runner state.json files.

Usage:
  python tools/kpi_report.py                    # newest run under runs_dir
  python tools/kpi_report.py --all              # every run
  python tools/kpi_report.py --run-id <id>
  python tools/kpi_report.py --format json      # JSON output
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Reuse Config loader from sprint_runner
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sprint_runner import Config  # noqa: E402


STAGES = ["branch", "research", "plan", "build", "commit",
          "test", "e2e", "review", "document", "publish"]


def _load_state(run_dir: Path) -> dict:
    return json.loads((run_dir / "state.json").read_text())


def _list_runs(runs_dir: Path) -> list[Path]:
    if not runs_dir.exists():
        return []
    return sorted((p for p in runs_dir.iterdir()
                   if p.is_dir() and (p / "state.json").exists()),
                  key=lambda p: p.name)


def _format_table(states: list[dict]) -> str:
    head = f"{'run_id':<20} {'status':<12} {'dur(s)':>8} {'credits':>8}  by_stage"
    lines = [head, "-" * len(head)]
    for s in states:
        tot = s.get("totals") or {}
        dur = tot.get("duration_seconds", 0)
        cred = tot.get("credits")
        cred_s = f"{cred:.2f}" if cred is not None else "-"
        stages = tot.get("by_stage") or {}
        parts = []
        for st in STAGES:
            v = stages.get(st) or {}
            if not v.get("duration_seconds"):
                continue
            pc = v.get("patch_cycles", 0)
            tag = f"{st}={v['duration_seconds']:.0f}s/{v.get('attempts',0)}a"
            if pc:
                tag += f"/pc={pc}"
            parts.append(tag)
        lines.append(f"{s.get('run_id',''):<20} {s.get('status',''):<12} "
                     f"{dur:>8.1f} {cred_s:>8}  {' '.join(parts)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="kpi_report")
    ap.add_argument("--config", default="tools/pipeline.yaml")
    ap.add_argument("--run-id", help="specific run id")
    ap.add_argument("--all", action="store_true", help="report all runs")
    ap.add_argument("--format", choices=["table", "json"], default="table")
    args = ap.parse_args(argv)

    cfg = Config.load(Path(args.config).resolve())
    runs_dir = cfg.path("runs_dir")
    all_runs = _list_runs(runs_dir)
    if not all_runs:
        print(f"no runs under {runs_dir}")
        return 0

    if args.run_id:
        target = [runs_dir / args.run_id]
    elif args.all:
        target = all_runs
    else:
        target = [all_runs[-1]]

    states = [_load_state(p) for p in target]
    if args.format == "json":
        print(json.dumps([{
            "run_id": s.get("run_id"),
            "status": s.get("status"),
            "totals": s.get("totals"),
        } for s in states], indent=2, default=str))
    else:
        print(_format_table(states))
    return 0


if __name__ == "__main__":
    sys.exit(main())
