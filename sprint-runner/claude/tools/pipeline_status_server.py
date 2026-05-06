#!/usr/bin/env python3
"""
Pipeline status server — flowchart dashboard for the current sprint-runner run.

Reads `.developer/sprint-runs/<run_id>/state.json` plus the per-cycle result
files (test-result-attempt-N.json, e2e-result-attempt-N.json,
review-result-attempt-N.json) and renders a phone-friendly flowchart where
each sprint step is a node, cycles (patch loops, retries) branch off as
sub-nodes, and every node expands to show details, errors, and screenshots.

Run:
    python tools/pipeline_status_server.py            # port 8765 on 0.0.0.0
    python tools/pipeline_status_server.py --port 9000
    python tools/pipeline_status_server.py --run-id 20260427-221809

Endpoints:
    /                HTML dashboard (client-side JSON refresh every 5s)
    /api/status      full snapshot with cycles merged
    /api/runs        list of known runs
    /file?path=<abs> serve a screenshot or log file (safe-rooted)
    /healthz         liveness check
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import mimetypes
import os
import re
import socket
import tempfile
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / ".developer" / "sprint-runs"
SYSTEM_TMP = Path(tempfile.gettempdir()).resolve()

STEP_ORDER = [
    "branch", "research", "plan", "build", "test",
    "e2e", "review", "document", "publish",
]

# Steps that run in cycles (attempt → patch → retry).
CYCLE_STEPS = ("test", "e2e", "review")

STALE_HEARTBEAT_SECONDS = 60

IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
TEXT_EXTS = {".jsonl", ".json", ".log", ".md", ".txt"}


# ─── Run discovery ─────────────────────────────────────────────────────────

def list_runs() -> list[Path]:
    if not RUNS_DIR.exists():
        return []
    return sorted(
        [p for p in RUNS_DIR.iterdir() if p.is_dir() and (p / "state.json").exists()],
        key=lambda p: p.name,
        reverse=True,
    )


def latest_run() -> Optional[Path]:
    runs = list_runs()
    return runs[0] if runs else None


def load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None


# ─── Time helpers ──────────────────────────────────────────────────────────

def parse_iso(s: Optional[str]) -> Optional[dt.datetime]:
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s)
    except ValueError:
        return None


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def humanize(total: Optional[float]) -> str:
    if total is None:
        return "—"
    total = max(0, int(total))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def elapsed_since(iso: Optional[str], until: Optional[dt.datetime] = None) -> Optional[float]:
    start = parse_iso(iso)
    if start is None:
        return None
    end = until or now_utc()
    return (end - start).total_seconds()


# ─── Cycle gathering ───────────────────────────────────────────────────────

_ATTEMPT_RE = re.compile(r"^(test|e2e|review)-result-attempt-(\d+)\.json$")


def gather_cycle_results(log_dir: Path) -> dict[str, list[dict]]:
    """
    Scan log_dir for {test,e2e,review}-result-attempt-N.json files and
    matching patch/commit log paths.
    """
    out: dict[str, list[dict]] = {k: [] for k in CYCLE_STEPS}
    if not log_dir.exists():
        return out

    files = sorted(log_dir.iterdir(), key=lambda p: p.name)
    for p in files:
        m = _ATTEMPT_RE.match(p.name)
        if not m:
            continue
        step = m.group(1)
        cycle = int(m.group(2))
        result = load_json(p) or {}

        cycle_log = log_dir / f"{step}-attempt-{cycle}.jsonl"
        if not cycle_log.exists():
            cycle_log = log_dir / f"{step}.jsonl"
        patch_log = log_dir / f"{step}-patch-{cycle}.jsonl"
        patch_commit_log = log_dir / f"{step}-patch-{cycle}-commit.jsonl"

        entry: dict[str, Any] = {
            "cycle": cycle,
            "result_path": str(p.relative_to(REPO_ROOT)),
            "summary": result.get("summary"),
            "passed": None,
            "errors": [],
            "screenshots": [],
            "failed_steps": [],
            "blockers": [],
            "cycle_log": str(cycle_log.relative_to(REPO_ROOT)) if cycle_log.exists() else None,
            "patch_log": str(patch_log.relative_to(REPO_ROOT)) if patch_log.exists() else None,
            "patch_commit_log": str(patch_commit_log.relative_to(REPO_ROOT)) if patch_commit_log.exists() else None,
        }

        if step == "test":
            entry["passed"] = (
                bool(result.get("build_succeeded"))
                and bool(result.get("tests_passed", True))
            )
            entry["errors"] = result.get("errors", []) or []
            entry["counts"] = {
                "errors": result.get("errors_count"),
                "warnings": result.get("warnings_count"),
                "tests_executed": result.get("tests_executed"),
            }
        elif step == "e2e":
            entry["passed"] = bool(result.get("passed"))
            entry["failed_steps"] = result.get("failed_steps", []) or []
            entry["screenshots"] = result.get("screenshots", []) or []
        elif step == "review":
            issues = result.get("review_issues", []) or []
            entry["blockers"] = [i for i in issues if i.get("issue_severity") == "blocker"]
            entry["non_blockers"] = [i for i in issues if i.get("issue_severity") != "blocker"]
            entry["passed"] = bool(result.get("success")) and not entry["blockers"]
            entry["screenshots"] = result.get("screenshots", []) or []

        out[step].append(entry)

    for k in out:
        out[k].sort(key=lambda e: e["cycle"])
    return out


def _derive_step_from_specs(
    name: str, specs: list[dict], pr: Optional[dict], now: dt.datetime,
) -> Optional[dict]:
    """Synthesize a `steps[]` row for phases the runner tracks per-spec only.

    - `build` status = rollup across every spec's build+commit
    - `document` status = rollup across every spec's `documentation` field,
      PR-gated (docs rarely exist until after publish merges)
    """
    if not specs:
        return None

    if name == "build":
        phases = []
        for sp in specs:
            phases.append((sp.get("build") or {}).get("status", "pending"))
            phases.append((sp.get("commit") or {}).get("status", "pending"))
        started_ats = [
            (sp.get("build") or {}).get("started_at")
            for sp in specs if (sp.get("build") or {}).get("started_at")
        ]
        completed_ats = [
            (sp.get("commit") or {}).get("completed_at") or
            (sp.get("build") or {}).get("completed_at")
            for sp in specs
        ]
        errors = [
            (sp.get("build") or {}).get("error") or (sp.get("commit") or {}).get("error")
            for sp in specs
        ]
        status = _rollup(phases)
        started = min(started_ats) if started_ats else None
        completed = None
        dur = None
        if status == "completed" and all(completed_ats):
            completed = max(completed_ats)
            if started and completed:
                dur = elapsed_since(started, parse_iso(completed))
        elif status == "in_progress" and started:
            dur = elapsed_since(started, now)
        return {
            "name": "build",
            "status": status,
            "started_at": started,
            "completed_at": completed,
            "duration_seconds": dur,
            "attempts": max((sp.get("build") or {}).get("attempts", 0) for sp in specs) or 0,
            "error": next((e for e in errors if e), None),
            "log_path": None,
        }

    if name == "document":
        # Docs only run after publish merges. Don't misreport as "pending"
        # when the sprint hasn't reached that phase yet.
        merged = bool(pr and pr.get("merged"))
        docs = [sp.get("documentation") for sp in specs]
        if not merged and not any(docs):
            return None
        if all(docs):
            return {
                "name": "document",
                "status": "completed",
                "started_at": None, "completed_at": None,
                "duration_seconds": None, "attempts": 1,
                "error": None, "log_path": None,
            }
        if any(docs):
            return {
                "name": "document",
                "status": "in_progress",
                "started_at": None, "completed_at": None,
                "duration_seconds": None, "attempts": 1,
                "error": None, "log_path": None,
            }
        return None
    return None


def _rollup(statuses: list[str]) -> str:
    """Combine several child statuses into one parent status."""
    if any(s == "failed" for s in statuses):
        return "failed"
    if statuses and all(s == "completed" for s in statuses):
        return "completed"
    if any(s == "in_progress" for s in statuses) or any(s == "completed" for s in statuses):
        return "in_progress"
    return "pending"


# ─── Snapshot builder ──────────────────────────────────────────────────────

def build_snapshot(run_dir: Path) -> dict[str, Any]:
    state = load_json(run_dir / "state.json") or {}
    lock = load_json(run_dir / "RUNNING.lock")
    now = now_utc()

    run_status = state.get("status", "unknown")
    started = state.get("started_at")
    completed = state.get("completed_at")

    hb_fresh = False
    hb_age: Optional[float] = None
    if lock:
        hb_age = elapsed_since(lock.get("heartbeat_at"), now)
        if hb_age is not None and hb_age <= STALE_HEARTBEAT_SECONDS:
            hb_fresh = True

    effective_status = run_status
    if run_status == "in_progress" and lock and not hb_fresh:
        effective_status = "abandoned"

    elapsed_total = None
    if started:
        end = parse_iso(completed) if completed else now
        elapsed_total = elapsed_since(started, end)

    sprints_out: list[dict] = []
    current_sprint_id: Optional[str] = None
    current_step: Optional[str] = None
    next_step: Optional[str] = None
    up_next_in_sprint: list[str] = []

    for sp in state.get("sprints", []):
        sp_status = sp.get("status", "pending")
        sp_started = sp.get("started_at")
        sp_completed = sp.get("completed_at")
        sp_elapsed = None
        if sp_started:
            end = parse_iso(sp_completed) if sp_completed else now
            sp_elapsed = elapsed_since(sp_started, end)

        log_dir = run_dir / sp["sprint_id"]
        cycles = gather_cycle_results(log_dir)

        steps_by_name = {s["name"]: s for s in sp.get("steps", [])}
        specs_list = sp.get("specs", []) or []
        step_rows: list[dict] = []
        for name in STEP_ORDER:
            row = steps_by_name.get(name)
            if row is None and name in ("build", "document"):
                row = _derive_step_from_specs(name, specs_list, sp.get("pr"), now)
            if row is None:
                row = {
                    "name": name,
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": None,
                    "attempts": 0,
                    "error": None,
                    "log_path": None,
                }
            dur = row.get("duration_seconds")
            if row.get("status") == "in_progress" and row.get("started_at") and dur is None:
                dur = elapsed_since(row.get("started_at"), now)
            step_cycles = cycles.get(name, []) if name in CYCLE_STEPS else []

            # Surface the in-flight patch row (test_patch, e2e_patch, review_patch)
            # as metadata on the parent step. The runner keeps ONE row per patch
            # phase and bumps `attempts` — status reflects the most recent patch.
            patch_row = None
            if name in CYCLE_STEPS:
                raw = steps_by_name.get(f"{name}_patch")
                if raw:
                    p_dur = raw.get("duration_seconds")
                    if raw.get("status") == "in_progress" and raw.get("started_at") and p_dur is None:
                        p_dur = elapsed_since(raw.get("started_at"), now)
                    patch_row = {
                        "status": raw.get("status", "pending"),
                        "started_at": raw.get("started_at"),
                        "completed_at": raw.get("completed_at"),
                        "duration_seconds": p_dur,
                        "attempts": raw.get("attempts", 0),
                        "error": raw.get("error"),
                        "log_path": raw.get("log_path"),
                    }

            # Override aggregate status: if the parent cycle step is "failed"
            # but a patch is in-flight, the whole phase is still running.
            status = row.get("status", "pending")
            if patch_row and patch_row["status"] == "in_progress" and status == "failed":
                status = "in_progress"

            step_rows.append({
                "name": name,
                "status": status,
                "started_at": row.get("started_at"),
                "completed_at": row.get("completed_at"),
                "duration_seconds": dur,
                "attempts": row.get("attempts", 0),
                "error": row.get("error"),
                "log_path": row.get("log_path"),
                "cycles": step_cycles,
                "patch": patch_row,
            })

        active = next((r for r in step_rows if r["status"] == "in_progress"), None)
        if sp_status == "in_progress" and current_sprint_id is None:
            current_sprint_id = sp["sprint_id"]
            if active:
                current_step = active["name"]
            else:
                pending = [r for r in step_rows if r["status"] == "pending"]
                current_step = pending[0]["name"] if pending else None
            if current_step:
                idx = STEP_ORDER.index(current_step)
                up_next_in_sprint = STEP_ORDER[idx + 1:]
                next_step = up_next_in_sprint[0] if up_next_in_sprint else None

        specs_out: list[dict] = []
        for spec in sp.get("specs", []):
            build = spec.get("build", {}) or {}
            commit = spec.get("commit", {}) or {}
            b_dur = build.get("duration_seconds")
            if build.get("status") == "in_progress" and build.get("started_at") and b_dur is None:
                b_dur = elapsed_since(build.get("started_at"), now)
            specs_out.append({
                "id": spec.get("id"),
                "title": spec.get("title"),
                "path": spec.get("path"),
                "build_status": build.get("status", "pending"),
                "build_duration_seconds": b_dur,
                "build_attempts": build.get("attempts", 0),
                "build_summary": build.get("summary"),
                "build_log_path": build.get("log_path"),
                "build_error": build.get("error"),
                "commit_status": commit.get("status", "pending"),
                "commit_sha": (commit.get("sha") or "")[:7] or None,
                "commit_message": commit.get("message"),
                "commit_log_path": commit.get("log_path"),
                "documentation": spec.get("documentation"),
            })

        sprints_out.append({
            "sprint_id": sp.get("sprint_id"),
            "slug": sp.get("slug"),
            "title": sp.get("title"),
            "branch": sp.get("branch"),
            "status": sp_status,
            "started_at": sp_started,
            "completed_at": sp_completed,
            "elapsed_seconds": sp_elapsed,
            "step_executions": sp.get("step_executions", {}),
            "steps": step_rows,
            "specs": specs_out,
            "errors": sp.get("errors", []),
            "pr": sp.get("pr"),
            "research_doc": sp.get("research_doc"),
            "e2e_test_path": sp.get("e2e_test_path"),
            "tests": sp.get("tests"),
            "e2e": sp.get("e2e"),
            "review": sp.get("review"),
            "documentation": sp.get("documentation", []),
            "active_step": active["name"] if active else None,
        })

    return {
        "run_id": state.get("run_id"),
        "run_dir": str(run_dir.relative_to(REPO_ROOT)),
        "sprint_selector": state.get("sprint_selector"),
        "plan_model": state.get("plan_model"),
        "execute_model": state.get("execute_model"),
        "opus_only": state.get("opus_only"),
        "status": effective_status,
        "declared_status": run_status,
        "started_at": started,
        "completed_at": completed,
        "updated_at": state.get("updated_at"),
        "elapsed_seconds": elapsed_total,
        "heartbeat": {
            "present": lock is not None,
            "fresh": hb_fresh,
            "age_seconds": hb_age,
            "pid": (lock or {}).get("pid"),
            "host": (lock or {}).get("host"),
            "heartbeat_at": (lock or {}).get("heartbeat_at"),
        },
        "current_sprint_id": current_sprint_id,
        "current_step": current_step,
        "next_step": next_step,
        "upcoming_steps_in_current_sprint": up_next_in_sprint,
        "upcoming_sprints": [s["sprint_id"] for s in sprints_out if s["status"] == "pending"],
        "sprints": sprints_out,
        "now": now.isoformat(),
    }


# ─── Safe file serving ─────────────────────────────────────────────────────

SAFE_ROOTS: tuple[Path, ...] = (REPO_ROOT.resolve(), SYSTEM_TMP)


def is_safe_path(p: Path) -> bool:
    try:
        real = p.resolve()
    except OSError:
        return False
    if not real.is_file():
        return False
    for root in SAFE_ROOTS:
        try:
            real.relative_to(root)
            return True
        except ValueError:
            continue
    return False


# ─── HTML / JS ─────────────────────────────────────────────────────────────

PAGE_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#0A0A0B">
  <title>Pipeline · Status</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Fira+Sans:wght@300;400;500;600;700&display=swap">
  <style>
    :root {
      /* Dark OLED base — true black with layered surfaces */
      --bg: #0A0A0B;
      --bg-grid: rgba(34, 197, 94, 0.035);
      --surface-1: #101115;
      --surface-2: #16181F;
      --surface-3: #1D202A;
      --border: #222530;
      --border-strong: #2F333F;
      --fg: #F5F7FA;
      --fg-dim: #C3C7D1;
      --muted: #7A7F8B;
      --subtle: #4D5260;

      /* Semantic status tokens */
      --ok: #22C55E;
      --ok-glow: rgba(34, 197, 94, 0.45);
      --run: #3B82F6;
      --run-glow: rgba(59, 130, 246, 0.55);
      --fail: #EF4444;
      --fail-glow: rgba(239, 68, 68, 0.45);
      --warn: #F59E0B;
      --warn-glow: rgba(245, 158, 11, 0.45);
      --pend: #3A3E49;

      /* Elevation & rhythm */
      --radius-sm: 6px;
      --radius: 12px;
      --radius-lg: 18px;
      --shadow-card: 0 1px 0 rgba(255,255,255,0.02) inset, 0 8px 24px rgba(0,0,0,0.4);
      --shadow-glow: 0 0 0 1px rgba(34,197,94,0.25), 0 0 30px rgba(34,197,94,0.18);
      --ease: cubic-bezier(0.22, 0.61, 0.36, 1);
    }
    *, *::before, *::after { box-sizing: border-box; }
    html { -webkit-text-size-adjust: 100%; }
    html, body { margin: 0; background: var(--bg); color: var(--fg); }
    body {
      font-family: "Fira Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 15px; line-height: 1.5;
      font-feature-settings: "ss01", "cv11";
      padding-bottom: env(safe-area-inset-bottom);
      background-image:
        radial-gradient(1200px 600px at 50% -200px, rgba(34,197,94,0.07), transparent 60%),
        linear-gradient(180deg, rgba(59,130,246,0.03) 0%, transparent 40%),
        repeating-linear-gradient(0deg,   var(--bg-grid) 0 1px, transparent 1px 48px),
        repeating-linear-gradient(90deg,  var(--bg-grid) 0 1px, transparent 1px 48px);
      background-attachment: fixed;
      min-height: 100vh;
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation: none !important; transition: none !important; }
    }

    a { color: var(--run); text-decoration: none; transition: color 160ms var(--ease); }
    a:hover { color: #7FB5FF; text-decoration: underline; text-underline-offset: 3px; }
    a:focus-visible, button:focus-visible, select:focus-visible, summary:focus-visible {
      outline: 2px solid var(--ok);
      outline-offset: 2px;
      border-radius: 4px;
    }

    code, pre, .mono { font-family: "Fira Code", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    code {
      background: var(--surface-1); color: var(--fg-dim);
      padding: 1px 6px; border-radius: 4px;
      border: 1px solid var(--border);
      font-size: 0.88em;
    }
    pre {
      white-space: pre-wrap; word-break: break-word;
      background: var(--surface-1); padding: 12px; border-radius: var(--radius-sm);
      border: 1px solid var(--border); font-size: 12px;
      max-height: 320px; overflow: auto;
    }

    /* ─── Header ─────────────────────────────────────────────────── */
    header.top {
      position: sticky; top: 0; z-index: 20;
      padding: 14px 20px 12px;
      background: linear-gradient(180deg, rgba(10,10,11,0.95), rgba(10,10,11,0.65));
      backdrop-filter: blur(16px) saturate(1.2);
      -webkit-backdrop-filter: blur(16px) saturate(1.2);
      border-bottom: 1px solid var(--border);
    }
    .top-row { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
    .brand {
      display: inline-flex; align-items: center; gap: 10px;
      font-weight: 600; font-size: 15px; letter-spacing: -0.01em;
    }
    .brand-logo {
      width: 32px; height: 32px; border-radius: 8px;
      background:
        radial-gradient(circle at 30% 25%, rgba(34,197,94,0.6), transparent 55%),
        linear-gradient(135deg, var(--surface-3), var(--surface-1));
      border: 1px solid var(--border-strong);
      display: grid; place-items: center; color: var(--ok);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }
    .brand-kicker {
      display: block; font-size: 11px; color: var(--muted);
      text-transform: uppercase; letter-spacing: 0.08em;
      font-weight: 500;
    }
    .brand-title { font-size: 15px; color: var(--fg); }
    .top-actions { margin-left: auto; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }

    .badge {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 4px 10px 4px 8px; border-radius: 999px;
      font-size: 11.5px; font-weight: 600; letter-spacing: 0.02em;
      text-transform: uppercase;
      font-family: "Fira Code", ui-monospace, monospace;
      border: 1px solid transparent;
    }
    .badge .badge-dot {
      width: 7px; height: 7px; border-radius: 50%; background: currentColor;
    }
    .status-in_progress { color: var(--run); background: color-mix(in srgb, var(--run) 14%, transparent); border-color: color-mix(in srgb, var(--run) 32%, transparent); }
    .status-in_progress .badge-dot { animation: pulse-dot 1.4s var(--ease) infinite; }
    .status-completed   { color: var(--ok);   background: color-mix(in srgb, var(--ok) 14%,   transparent); border-color: color-mix(in srgb, var(--ok)   32%, transparent); }
    .status-failed      { color: var(--fail); background: color-mix(in srgb, var(--fail) 14%, transparent); border-color: color-mix(in srgb, var(--fail) 32%, transparent); }
    .status-pending     { color: var(--muted);background: color-mix(in srgb, var(--muted) 12%,transparent); border-color: var(--border); }
    .status-abandoned, .status-interrupted { color: var(--warn); background: color-mix(in srgb, var(--warn) 14%, transparent); border-color: color-mix(in srgb, var(--warn) 32%, transparent); }
    .status-unknown     { color: var(--muted);background: color-mix(in srgb, var(--muted) 12%,transparent); border-color: var(--border); }

    select, button {
      background: var(--surface-2); color: var(--fg);
      border: 1px solid var(--border-strong);
      padding: 7px 12px; border-radius: var(--radius-sm);
      font: inherit; font-size: 13px;
      cursor: pointer;
      transition: background 160ms var(--ease), border-color 160ms var(--ease), transform 120ms var(--ease);
    }
    select:hover, button:hover { background: var(--surface-3); border-color: var(--ok); }
    button.ghost {
      display: inline-flex; align-items: center; justify-content: center; gap: 6px;
      width: 36px; height: 36px; padding: 0;
    }
    button.ghost:active { transform: scale(0.96); }

    .subline {
      margin-top: 8px; display: flex; gap: 14px; flex-wrap: wrap;
      color: var(--muted); font-size: 12.5px;
      font-family: "Fira Code", ui-monospace, monospace;
    }
    .subline-item { display: inline-flex; align-items: center; gap: 6px; }
    .subline-item .ico { color: var(--subtle); }

    main { padding: 20px; max-width: 1080px; margin: 0 auto; }

    /* ─── Hero (bento) ────────────────────────────────────────────── */
    .hero {
      display: grid; gap: 14px;
      grid-template-columns: repeat(12, 1fr);
      margin-bottom: 22px;
    }
    .tile {
      position: relative; overflow: hidden;
      background: linear-gradient(180deg, var(--surface-2), var(--surface-1));
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px 18px;
      box-shadow: var(--shadow-card);
      transition: border-color 200ms var(--ease), transform 200ms var(--ease);
    }
    .tile::after {
      content: ""; position: absolute; inset: 0;
      background: radial-gradient(500px 160px at 100% 0%, rgba(34,197,94,0.08), transparent 60%);
      pointer-events: none;
    }
    .tile.span-6 { grid-column: span 12; }
    .tile.span-3 { grid-column: span 6; }
    @media (min-width: 720px) {
      .tile.span-6 { grid-column: span 6; }
      .tile.span-3 { grid-column: span 3; }
    }
    .tile .label {
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 11px; text-transform: uppercase; letter-spacing: 0.09em;
      color: var(--muted); font-weight: 500;
    }
    .tile .ico { color: var(--subtle); }
    .tile-value {
      margin-top: 8px; font-size: 22px; font-weight: 600;
      letter-spacing: -0.01em; word-break: break-word;
      color: var(--fg);
    }
    .tile-sub { margin-top: 4px; color: var(--fg-dim); font-size: 13px; }
    .tile-sub.mono { color: var(--muted); }
    .tile.accent { border-color: color-mix(in srgb, var(--ok) 30%, var(--border)); box-shadow: var(--shadow-card), var(--shadow-glow); }
    .tile.accent .tile-value { color: var(--ok); font-family: "Fira Code", ui-monospace, monospace; }
    .tile.accent::after { background: radial-gradient(500px 180px at 100% 0%, rgba(34,197,94,0.2), transparent 55%); }
    .tile.tile-run   .tile-value { color: var(--run); }
    .tile.tile-run   { border-color: color-mix(in srgb, var(--run) 30%, var(--border)); }

    /* Mini progress strip (steps as chips) */
    .chain {
      display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px;
    }
    .chain-chip {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 4px 10px; border-radius: 999px;
      font-family: "Fira Code", ui-monospace, monospace;
      font-size: 11px; border: 1px solid var(--border);
      color: var(--muted); background: var(--surface-1);
      transition: border-color 160ms var(--ease), color 160ms var(--ease);
    }
    .chain-chip .dot {
      width: 6px; height: 6px; border-radius: 50%; background: var(--pend);
    }
    .chain-chip.done    { color: var(--ok);   border-color: color-mix(in srgb, var(--ok) 35%, transparent); }
    .chain-chip.done    .dot { background: var(--ok); }
    .chain-chip.active  { color: var(--run);  border-color: color-mix(in srgb, var(--run) 40%, transparent); background: color-mix(in srgb, var(--run) 10%, var(--surface-1)); }
    .chain-chip.active  .dot { background: var(--run); box-shadow: 0 0 10px var(--run-glow); animation: pulse-dot 1.4s var(--ease) infinite; }
    .chain-chip.failed  { color: var(--fail); border-color: color-mix(in srgb, var(--fail) 40%, transparent); }
    .chain-chip.failed  .dot { background: var(--fail); }

    /* ─── Meta tiles ──────────────────────────────────────────────── */
    .meta-grid {
      display: grid; gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      margin-bottom: 22px;
    }
    .meta-tile {
      background: var(--surface-2);
      border: 1px solid var(--border);
      padding: 12px 14px; border-radius: var(--radius-sm);
    }
    .meta-tile .label { display: flex; align-items: center; gap: 6px; }
    .meta-tile .value { margin-top: 4px; font-size: 14px; color: var(--fg-dim); word-break: break-word; }
    .meta-tile.full { grid-column: 1 / -1; }

    /* ─── Section heading ────────────────────────────────────────── */
    .section-title {
      display: flex; align-items: center; gap: 10px;
      font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em;
      color: var(--muted); font-weight: 600;
      margin: 4px 0 12px;
    }
    .section-title::before {
      content: ""; width: 24px; height: 1px; background: var(--border-strong);
    }

    /* ─── Sprint card ─────────────────────────────────────────────── */
    .sprint {
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      margin-bottom: 18px;
      overflow: hidden;
      box-shadow: var(--shadow-card);
      transition: border-color 200ms var(--ease);
    }
    .sprint.status-ring-in_progress { border-color: color-mix(in srgb, var(--run) 40%, var(--border)); }
    .sprint.status-ring-failed      { border-color: color-mix(in srgb, var(--fail) 40%, var(--border)); }
    .sprint-head {
      display: grid; grid-template-columns: auto 1fr auto; gap: 12px;
      align-items: center;
      padding: 14px 18px;
      background: linear-gradient(180deg, var(--surface-3), var(--surface-2));
      border-bottom: 1px solid var(--border);
      cursor: pointer; user-select: none;
    }
    .sprint-head h2 {
      margin: 0; font-size: 15.5px; font-weight: 600; letter-spacing: -0.01em;
    }
    .sprint-head h2 .sprint-id {
      font-family: "Fira Code", ui-monospace, monospace;
      color: var(--muted); margin-right: 8px; font-weight: 500;
    }
    .sprint-head .chevron {
      color: var(--muted); transition: transform 200ms var(--ease);
    }
    .sprint.collapsed .sprint-head .chevron { transform: rotate(-90deg); }
    .sprint-meta {
      grid-column: 1 / -1; color: var(--muted); font-size: 12px;
      font-family: "Fira Code", ui-monospace, monospace;
      display: flex; flex-wrap: wrap; gap: 12px;
    }
    .sprint-meta .sep { color: var(--subtle); }
    .sprint.collapsed .sprint-body { display: none; }
    .sprint-body { padding: 16px 20px 20px; }

    /* ─── Flowchart ───────────────────────────────────────────────── */
    .flow { position: relative; padding-left: 30px; }
    .flow::before {
      content: ""; position: absolute; left: 15px; top: 16px; bottom: 16px;
      width: 2px;
      background: linear-gradient(180deg, var(--border-strong), var(--border) 30%, var(--border) 70%, var(--border-strong));
      border-radius: 2px;
    }
    .node {
      position: relative; padding: 12px 0 12px 10px;
      border-left: 0;
    }
    .node::before {
      content: ""; position: absolute; left: -24px; top: 16px;
      width: 18px; height: 18px; border-radius: 50%;
      background: var(--surface-1);
      border: 2px solid var(--border-strong);
      transition: all 200ms var(--ease);
    }
    .node::after {
      content: ""; position: absolute; left: -18px; top: 22px;
      width: 6px; height: 6px; border-radius: 50%;
      background: var(--pend);
      transition: all 200ms var(--ease);
    }
    .node.status-completed::before   { border-color: var(--ok); }
    .node.status-completed::after    { background: var(--ok); box-shadow: 0 0 10px var(--ok-glow); }
    .node.status-in_progress::before { border-color: var(--run); box-shadow: 0 0 0 4px color-mix(in srgb, var(--run) 15%, transparent); }
    .node.status-in_progress::after  { background: var(--run); animation: pulse-dot 1.4s var(--ease) infinite; }
    .node.status-failed::before      { border-color: var(--fail); }
    .node.status-failed::after       { background: var(--fail); box-shadow: 0 0 10px var(--fail-glow); }

    @keyframes pulse-dot {
      0%, 100% { box-shadow: 0 0 0 0 var(--run-glow); transform: scale(1); }
      50%      { box-shadow: 0 0 0 6px transparent;   transform: scale(1.25); }
    }

    .node-head {
      display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    }
    .node-icon {
      display: inline-flex; align-items: center; justify-content: center;
      width: 28px; height: 28px; border-radius: 7px;
      background: var(--surface-1);
      border: 1px solid var(--border);
      color: var(--muted);
      flex-shrink: 0;
    }
    .node.status-completed   .node-icon { color: var(--ok);   border-color: color-mix(in srgb, var(--ok)   35%, var(--border)); }
    .node.status-in_progress .node-icon { color: var(--run);  border-color: color-mix(in srgb, var(--run)  35%, var(--border)); background: color-mix(in srgb, var(--run) 8%, var(--surface-1)); }
    .node.status-failed      .node-icon { color: var(--fail); border-color: color-mix(in srgb, var(--fail) 35%, var(--border)); }
    .node-name {
      font-weight: 600; font-size: 14.5px; letter-spacing: -0.01em;
      text-transform: capitalize;
    }
    .node-status {
      font-family: "Fira Code", ui-monospace, monospace;
      font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.08em;
      color: var(--muted); padding: 2px 7px; border-radius: 999px;
      border: 1px solid var(--border); background: var(--surface-1);
    }
    .node-status.status-in_progress { color: var(--run); border-color: color-mix(in srgb, var(--run) 35%, transparent); }
    .node-status.status-completed   { color: var(--ok);  border-color: color-mix(in srgb, var(--ok)  35%, transparent); }
    .node-status.status-failed      { color: var(--fail);border-color: color-mix(in srgb, var(--fail)35%, transparent); }
    .node-dur {
      margin-left: auto; font-family: "Fira Code", ui-monospace, monospace;
      font-size: 11.5px; color: var(--muted); font-variant-numeric: tabular-nums;
    }
    .node-summary { color: var(--fg-dim); font-size: 13px; margin-top: 6px; margin-left: 38px; }
    .node-err {
      color: var(--fail); font-size: 12.5px; margin-top: 6px; margin-left: 38px;
      padding: 8px 10px; border-radius: 6px;
      background: color-mix(in srgb, var(--fail) 8%, transparent);
      border: 1px solid color-mix(in srgb, var(--fail) 25%, transparent);
      font-family: "Fira Code", ui-monospace, monospace;
    }

    .patch-strip {
      display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
      margin: 8px 0 0 38px;
      padding: 8px 12px;
      background: color-mix(in srgb, var(--run) 6%, var(--surface-1));
      border: 1px solid color-mix(in srgb, var(--run) 25%, var(--border));
      border-radius: 8px;
    }
    .patch-strip.failed {
      background: color-mix(in srgb, var(--fail) 6%, var(--surface-1));
      border-color: color-mix(in srgb, var(--fail) 30%, var(--border));
    }
    .patch-strip.done {
      background: color-mix(in srgb, var(--ok) 6%, var(--surface-1));
      border-color: color-mix(in srgb, var(--ok) 30%, var(--border));
    }
    .patch-strip .patch-dur { margin-left: auto; color: var(--muted); font-size: 11.5px; }
    .patch-strip .patch-err {
      color: var(--fail); font-size: 12px; width: 100%;
      font-family: "Fira Code", ui-monospace, monospace;
    }

    .node-details { margin-top: 8px; margin-left: 38px; }
    .node-details summary {
      cursor: pointer; color: var(--muted); font-size: 12px;
      user-select: none; outline: none; list-style: none;
      display: inline-flex; align-items: center; gap: 6px;
      padding: 3px 9px; border-radius: 6px; border: 1px solid var(--border);
      background: var(--surface-1);
      transition: all 160ms var(--ease);
      font-family: "Fira Code", ui-monospace, monospace;
    }
    .node-details summary:hover { color: var(--fg); border-color: var(--border-strong); }
    .node-details summary::-webkit-details-marker { display: none; }
    .node-details summary .chev { transition: transform 160ms var(--ease); }
    .node-details[open] summary .chev { transform: rotate(90deg); }
    .detail-body { padding: 10px 0 4px; }

    /* ─── Cycles ──────────────────────────────────────────────────── */
    .cycles {
      margin-top: 12px; margin-left: 38px; padding-left: 22px; position: relative;
    }
    .cycles::before {
      content: ""; position: absolute; left: 10px; top: 0; bottom: 8px;
      width: 2px; background: var(--border);
    }
    .cycle {
      position: relative; padding: 8px 0 8px 2px;
    }
    .cycle::before {
      content: ""; position: absolute; left: -18px; top: 14px;
      width: 10px; height: 10px; border-radius: 50%;
      background: var(--surface-1);
      border: 2px solid var(--border-strong);
    }
    .cycle::after {
      content: ""; position: absolute; left: -14px; top: 18px;
      width: 2px; height: 2px; border-radius: 50%;
      background: var(--pend);
    }
    .cycle.pass::before { border-color: var(--ok); }
    .cycle.pass::after  { background: var(--ok); box-shadow: 0 0 6px var(--ok-glow); }
    .cycle.fail::before { border-color: var(--fail); }
    .cycle.fail::after  { background: var(--fail); box-shadow: 0 0 6px var(--fail-glow); }
    .cycle-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 13px; }
    .cycle-label { font-weight: 500; font-family: "Fira Code", ui-monospace, monospace; }
    .cycle-verdict {
      font-size: 10.5px; padding: 2px 7px; border-radius: 999px;
      font-family: "Fira Code", ui-monospace, monospace; text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .cycle.pass .cycle-verdict { color: var(--ok);   background: color-mix(in srgb, var(--ok)   12%, transparent); }
    .cycle.fail .cycle-verdict { color: var(--fail); background: color-mix(in srgb, var(--fail) 12%, transparent); }

    /* ─── Specs (build detail) ─────────────────────────────────────── */
    .specs-list {
      margin-top: 10px; margin-left: 38px; padding-left: 22px;
      position: relative;
    }
    .specs-list::before {
      content: ""; position: absolute; left: 10px; top: 0; bottom: 8px;
      width: 2px; background: var(--border);
    }
    .spec {
      position: relative; padding: 10px 0;
      border-bottom: 1px solid var(--border);
    }
    .spec:last-child { border-bottom: none; }
    .spec::before {
      content: ""; position: absolute; left: -18px; top: 16px;
      width: 10px; height: 10px; border-radius: 50%;
      background: var(--surface-1); border: 2px solid var(--border-strong);
    }
    .spec.status-completed::before   { border-color: var(--ok); background: var(--ok); }
    .spec.status-in_progress::before { border-color: var(--run); background: var(--run); box-shadow: 0 0 0 3px color-mix(in srgb, var(--run) 20%, transparent); }
    .spec.status-failed::before      { border-color: var(--fail); background: var(--fail); }
    .spec-head {
      display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap;
    }
    .spec-id {
      font-family: "Fira Code", ui-monospace, monospace;
      color: var(--muted); font-size: 11.5px;
      padding: 1px 6px; border: 1px solid var(--border); border-radius: 4px;
      background: var(--surface-1);
    }
    .spec-title { font-size: 14px; font-weight: 500; color: var(--fg); }
    .spec-row {
      display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
      margin-top: 8px; font-size: 12px; color: var(--muted);
    }

    .pill {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 3px 9px; border-radius: 999px;
      font-size: 10.5px; font-weight: 600; letter-spacing: 0.04em;
      text-transform: uppercase;
      font-family: "Fira Code", ui-monospace, monospace;
      border: 1px solid transparent;
    }
    .pill .pill-dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }

    /* ─── Screenshots ─────────────────────────────────────────────── */
    .screenshots {
      display: grid; gap: 10px; margin-top: 10px;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    }
    .screenshots a {
      display: block; border: 1px solid var(--border); border-radius: var(--radius-sm);
      overflow: hidden; background: var(--surface-1); position: relative;
      transition: transform 200ms var(--ease), border-color 200ms var(--ease);
    }
    .screenshots a:hover { border-color: var(--ok); }
    .screenshots a::after {
      content: ""; position: absolute; inset: 0;
      background: linear-gradient(180deg, transparent 60%, rgba(0,0,0,0.5));
      pointer-events: none; opacity: 0; transition: opacity 200ms var(--ease);
    }
    .screenshots a:hover::after { opacity: 1; }
    .screenshots img {
      width: 100%; height: 110px; object-fit: cover; display: block;
    }
    .screenshots .missing {
      display: flex; align-items: center; justify-content: center;
      height: 110px; color: var(--muted); font-size: 12px;
      padding: 10px; text-align: center;
      font-family: "Fira Code", ui-monospace, monospace;
    }

    /* ─── Key/value & lists ──────────────────────────────────────── */
    .kv-row {
      display: grid; grid-template-columns: 120px 1fr; gap: 10px;
      padding: 4px 0; font-size: 12.5px; align-items: baseline;
    }
    .kv-row .k {
      color: var(--muted); text-transform: uppercase;
      letter-spacing: 0.06em; font-size: 10.5px; font-weight: 500;
    }
    .kv-row .v { color: var(--fg-dim); word-break: break-word; }

    ul.issue-list {
      margin: 8px 0 0; padding: 0; font-size: 13px;
      list-style: none;
    }
    ul.issue-list li {
      margin-bottom: 6px; padding: 6px 10px; border-radius: 6px;
      background: var(--surface-1); border: 1px solid var(--border);
      line-height: 1.45;
    }
    ul.issue-list li.blocker     { border-color: color-mix(in srgb, var(--fail) 30%, var(--border)); color: var(--fg-dim); }
    ul.issue-list li.non-blocker { border-color: color-mix(in srgb, var(--warn) 30%, var(--border)); color: var(--fg-dim); }

    footer {
      color: var(--muted); font-size: 12px; text-align: center;
      margin: 24px 0 40px;
      font-family: "Fira Code", ui-monospace, monospace;
    }
    footer a { color: var(--muted); }

    @media (max-width: 640px) {
      header.top { padding: 12px 14px 10px; }
      main { padding: 14px; }
      .hero { gap: 10px; }
      .tile { padding: 14px; }
      .tile-value { font-size: 18px; }
      .sprint-head { padding: 12px 14px; }
      .sprint-body { padding: 14px; }
      .flow { padding-left: 26px; }
      .flow::before { left: 13px; }
      .node::before { left: -22px; width: 16px; height: 16px; top: 14px; }
      .node::after  { left: -17px; top: 20px; }
      .node-summary, .node-err, .node-details, .cycles, .specs-list { margin-left: 36px; }
      .kv-row { grid-template-columns: 1fr; gap: 2px; }
    }

    /* ─── SVG sprite container (hidden) ──────────────────────────── */
    svg.ico {
      width: 16px; height: 16px; flex-shrink: 0;
      vertical-align: -3px;
    }
    .node-icon svg.ico { width: 15px; height: 15px; }
  </style>
</head>
<body>
  <header class="top">
    <div class="top-row">
      <div class="brand">
        <div class="brand-logo" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
          </svg>
        </div>
        <div>
          <span class="brand-kicker">Blast Radius</span>
          <span class="brand-title">Pipeline Status</span>
        </div>
      </div>
      <div class="top-actions">
        <span id="status-badge" class="badge status-unknown" aria-live="polite">
          <span class="badge-dot" aria-hidden="true"></span>
          <span id="status-badge-text">loading</span>
        </span>
        <label class="brand-kicker" for="run-select" style="margin-right:-4px">Run</label>
        <select id="run-select" onchange="selectRun(this.value)" aria-label="Select run"></select>
        <button class="ghost" onclick="refresh()" aria-label="Refresh" title="Refresh">
          <svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12a9 9 0 1 1-2.64-6.36"/>
            <path d="M21 4v5h-5"/>
          </svg>
        </button>
      </div>
    </div>
    <div id="subline" class="subline"></div>
  </header>
  <main>
    <section id="hero" class="hero" aria-label="Run overview"></section>
    <div class="section-title">Run context</div>
    <section id="meta" class="meta-grid"></section>
    <div class="section-title">Sprints</div>
    <div id="sprints"></div>
    <footer id="footer"></footer>
  </main>

<!-- SVG icon sprite -->
<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">
  <defs>
    <symbol id="i-branch" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></symbol>
    <symbol id="i-research" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></symbol>
    <symbol id="i-plan" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="13" y2="17"/></symbol>
    <symbol id="i-build" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></symbol>
    <symbol id="i-test" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 2v6l-5 10a2 2 0 0 0 2 3h12a2 2 0 0 0 2-3l-5-10V2"/><line x1="9" y1="2" x2="15" y2="2"/></symbol>
    <symbol id="i-e2e" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></symbol>
    <symbol id="i-review" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></symbol>
    <symbol id="i-document" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 22H6.5A2.5 2.5 0 0 1 4 19.5V4.5A2.5 2.5 0 0 1 6.5 2H20z"/><line x1="8" y1="7" x2="16" y2="7"/><line x1="8" y1="11" x2="16" y2="11"/><line x1="8" y1="15" x2="13" y2="15"/></symbol>
    <symbol id="i-publish" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"/><polyline points="5 12 12 5 19 12"/></symbol>
    <symbol id="i-clock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></symbol>
    <symbol id="i-activity" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></symbol>
    <symbol id="i-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></symbol>
    <symbol id="i-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></symbol>
    <symbol id="i-stack" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></symbol>
    <symbol id="i-pulse" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></symbol>
    <symbol id="i-cpu" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="2" x2="9" y2="4"/><line x1="15" y1="2" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="22"/><line x1="15" y1="20" x2="15" y2="22"/><line x1="20" y1="9" x2="22" y2="9"/><line x1="20" y1="14" x2="22" y2="14"/><line x1="2" y1="9" x2="4" y2="9"/><line x1="2" y1="14" x2="4" y2="14"/></symbol>
    <symbol id="i-calendar" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></symbol>
    <symbol id="i-terminal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></symbol>
  </defs>
</svg>

<script>
const STEP_ORDER = ["branch","research","plan","build","test","e2e","review","document","publish"];
const CYCLE_STEPS = new Set(["test","e2e","review"]);
const STEP_ICONS = {
  branch: "i-branch", research: "i-research", plan: "i-plan",
  build: "i-build", test: "i-test", e2e: "i-e2e",
  review: "i-review", document: "i-document", publish: "i-publish",
};
const REFRESH_MS = 5000;

const openKeys = new Set();
let currentRun = null;

function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "html") el.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined || c === false) continue;
    el.append(c.nodeType ? c : document.createTextNode(String(c)));
  }
  return el;
}

function svgIcon(id, extraClass = "") {
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("class", "ico " + extraClass);
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("focusable", "false");
  const use = document.createElementNS(NS, "use");
  use.setAttributeNS("http://www.w3.org/1999/xlink", "href", "#" + id);
  use.setAttribute("href", "#" + id);
  svg.appendChild(use);
  return svg;
}

function humanize(total) {
  if (total === null || total === undefined) return "—";
  total = Math.max(0, Math.floor(total));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (h) return `${h}h ${String(m).padStart(2,"0")}m`;
  if (m) return `${m}m ${String(s).padStart(2,"0")}s`;
  return `${s}s`;
}

function fmtTimestamp(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  const pad = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function qs(key) {
  return new URLSearchParams(window.location.search).get(key);
}

function selectRun(runId) {
  const p = new URLSearchParams(window.location.search);
  p.set("run", runId);
  window.location.search = p.toString();
}

async function refresh() {
  const params = new URLSearchParams();
  const run = qs("run");
  if (run) params.set("run", run);
  try {
    const [runs, snap] = await Promise.all([
      fetch("/api/runs").then(r => r.json()),
      fetch("/api/status" + (params.toString() ? "?" + params : "")).then(r => r.json()),
    ]);
    currentRun = snap.run_id;
    renderRuns(runs);
    render(snap);
  } catch (e) {
    console.error(e);
  }
}

function renderRuns(runs) {
  const sel = document.getElementById("run-select");
  const current = qs("run") || currentRun;
  sel.innerHTML = "";
  for (const r of runs) {
    const o = document.createElement("option");
    o.value = r;
    o.textContent = r;
    if (r === current) o.selected = true;
    sel.append(o);
  }
}

function render(snap) {
  const badge = document.getElementById("status-badge");
  badge.className = "badge status-" + (snap.status || "unknown");
  document.getElementById("status-badge-text").textContent = snap.status || "unknown";

  const sub = document.getElementById("subline");
  sub.innerHTML = "";
  sub.append(
    sublineItem("i-stack",    snap.run_id || "—"),
    sublineItem("i-clock",    "elapsed " + humanize(snap.elapsed_seconds)),
    sublineItem("i-activity", "updated " + fmtTimestamp(snap.updated_at)),
  );

  // ── Hero bento ──
  const hero = document.getElementById("hero");
  hero.innerHTML = "";
  const currSprint = snap.sprints.find(s => s.sprint_id === snap.current_sprint_id);
  if (currSprint) {
    const stepRow = currSprint.steps.find(s => s.name === snap.current_step);
    const stepDur = stepRow ? humanize(stepRow.duration_seconds) : "—";

    hero.append(heroTile({
      span: 6,
      icon: "i-activity",
      label: "Current sprint",
      value: `${currSprint.sprint_id} · ${currSprint.title || ""}`,
      sub: [
        ["branch ", codeEl(currSprint.branch || "—")],
      ],
      chain: chainStrip(currSprint, snap.current_step),
      accent: currSprint.status === "in_progress",
    }));

    hero.append(heroTile({
      span: 3,
      icon: "i-pulse",
      label: "Stage",
      value: snap.current_step || "—",
      sub: [[`running ${stepDur}`]],
      tone: "run",
    }));

    hero.append(heroTile({
      span: 3,
      icon: "i-arrow",
      label: "Coming next",
      value: snap.next_step || "—",
      sub: [[
        snap.upcoming_steps_in_current_sprint.length
          ? snap.upcoming_steps_in_current_sprint.join(" → ")
          : "(last step of sprint)"
      ]],
    }));

    hero.append(heroTile({
      span: 6,
      icon: "i-calendar",
      label: "Upcoming sprints",
      value: snap.upcoming_sprints.length ? snap.upcoming_sprints.join(" · ") : "(none)",
      sub: [[`${snap.sprints.length} total in run`]],
    }));
  } else {
    hero.append(heroTile({
      span: 6,
      icon: "i-activity",
      label: "Run status",
      value: snap.status || "—",
      sub: [[snap.completed_at ? `completed ${fmtTimestamp(snap.completed_at)}` : "no sprint currently running"]],
      accent: snap.status === "completed",
    }));
    hero.append(heroTile({
      span: 6,
      icon: "i-clock",
      label: "Elapsed",
      value: humanize(snap.elapsed_seconds),
      sub: [[`started ${fmtTimestamp(snap.started_at)}`]],
    }));
  }

  // ── Meta grid ──
  const meta = document.getElementById("meta");
  meta.innerHTML = "";
  const hb = snap.heartbeat || {};
  const hbMsg = hb.present
    ? `heartbeat ${hb.fresh ? "fresh" : "stale"} · ${humanize(hb.age_seconds)} ago · pid ${hb.pid}@${hb.host}`
    : "no lock file — runner not actively heartbeating";
  meta.append(
    metaTile("i-terminal", "Selector",      snap.sprint_selector || "—"),
    metaTile("i-calendar", "Started",       fmtTimestamp(snap.started_at)),
    metaTile("i-clock",    "Elapsed",       humanize(snap.elapsed_seconds)),
    metaTile("i-cpu",      "Plan model",    codeEl(snap.plan_model || "—")),
    metaTile("i-cpu",      "Execute model", codeEl(snap.execute_model || "—")),
    metaTile("i-pulse",    "Liveness",      hbMsg, true),
  );

  // ── Sprints ──
  const host = document.getElementById("sprints");
  host.innerHTML = "";
  if (snap.sprints.length === 0) {
    host.append(h("p", {style: "color:var(--muted)"}, "No sprints in this run yet."));
  } else {
    for (const sp of snap.sprints) host.append(renderSprint(sp));
  }

  document.getElementById("footer").innerHTML =
    `auto-refresh 5s · <a href="/api/status" target="_blank">/api/status</a> · ${escapeHtml(snap.run_dir || "")}`;
}

function sublineItem(iconId, text) {
  return h("span", {class: "subline-item"}, svgIcon(iconId), text);
}

function codeEl(text) {
  return h("code", {}, text);
}

function heroTile({span, icon, label, value, sub, chain, accent, tone}) {
  const classes = ["tile", "span-" + span];
  if (accent) classes.push("accent");
  if (tone === "run") classes.push("tile-run");
  const tile = h("div", {class: classes.join(" ")},
    h("div", {class: "label"}, svgIcon(icon), label),
    h("div", {class: "tile-value"}, value),
  );
  if (sub && sub.length) {
    for (const parts of sub) {
      const sEl = h("div", {class: "tile-sub"});
      for (const p of parts) sEl.append(p.nodeType ? p : document.createTextNode(String(p)));
      tile.append(sEl);
    }
  }
  if (chain) tile.append(chain);
  return tile;
}

function metaTile(iconId, label, value, full=false) {
  return h("div", {class: "meta-tile" + (full ? " full" : "")},
    h("div", {class: "label"}, svgIcon(iconId), label),
    h("div", {class: "value"},
      typeof value === "string" ? value : value),
  );
}

function chainStrip(sprint, currentStep) {
  const wrap = h("div", {class: "chain"});
  for (const name of STEP_ORDER) {
    const step = sprint.steps.find(s => s.name === name);
    let cls = "chain-chip";
    if (step) {
      if (step.status === "completed")     cls += " done";
      else if (step.status === "in_progress") cls += " active";
      else if (step.status === "failed")   cls += " failed";
    }
    wrap.append(
      h("span", {class: cls},
        h("span", {class: "dot"}),
        name,
      )
    );
  }
  return wrap;
}

function escapeHtml(s) {
  if (s === null || s === undefined) return "";
  return String(s).replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));
}

function renderSprint(sp) {
  const storageKey = `sprint-collapsed:${sp.sprint_id}`;
  const userSet = sessionStorage.getItem(storageKey);
  const defaultCollapsed = sp.status === "completed" && sp.sprint_id !== sp.current_sprint_id;
  const collapsed = userSet === null ? defaultCollapsed : userSet === "1";

  const wrap = h("section", {
    class: "sprint status-ring-" + sp.status + (collapsed ? " collapsed" : "")
  });

  const head = h("div", {class: "sprint-head", onclick: () => {
    wrap.classList.toggle("collapsed");
    sessionStorage.setItem(storageKey, wrap.classList.contains("collapsed") ? "1" : "0");
  }},
    h("span", {class: "badge status-" + sp.status},
      h("span", {class: "badge-dot"}),
      sp.status),
    h("h2", {},
      h("span", {class: "sprint-id"}, `#${sp.sprint_id}`),
      sp.title || ""
    ),
    svgIcon("i-chevron", "chevron"),
    h("div", {class: "sprint-meta"},
      sublineItem("i-clock",    "elapsed " + humanize(sp.elapsed_seconds)),
      sp.active_step ? sublineItem("i-pulse", "on " + sp.active_step) : null,
      sp.branch ? sublineItem("i-branch", sp.branch) : null,
    ),
  );
  wrap.append(head);

  const body = h("div", {class: "sprint-body"});
  const flow = h("div", {class: "flow"});
  for (const step of sp.steps) flow.append(renderStep(sp, step));
  body.append(flow);

  if (sp.errors && sp.errors.length) {
    body.append(
      h("div", {style: "margin-top:14px"},
        h("div", {class: "section-title", style: "color: var(--fail); margin: 0 0 8px;"}, "Sprint errors"),
        h("ul", {class: "issue-list"},
          ...sp.errors.map(e => h("li", {class: "blocker"},
            h("code", {}, e.step), " ", e.error))),
      )
    );
  }

  if (sp.pr) {
    const pr = sp.pr;
    body.append(
      h("div", {style: "margin-top:14px"},
        h("div", {class: "section-title", style: "margin: 0 0 8px"}, "Pull request"),
        h("div", {class: "meta-tile"},
          h("div", {class: "label"}, svgIcon("i-publish"), `#${pr.number} · ${pr.merged ? "merged" : "open"}`),
          h("div", {class: "value"},
            h("a", {href: pr.url, target: "_blank", rel: "noopener"}, pr.url || ""))
        ),
      )
    );
  }

  wrap.append(body);
  return wrap;
}

function renderStep(sp, step) {
  const node = h("div", {class: "node status-" + step.status});
  const dur = humanize(step.duration_seconds);

  node.append(h("div", {class: "node-head"},
    h("span", {class: "node-icon"}, svgIcon(STEP_ICONS[step.name] || "i-activity")),
    h("span", {class: "node-name"}, step.name),
    h("span", {class: "node-status status-" + step.status}, step.status),
    h("span", {class: "node-dur"}, dur + (step.attempts > 1 ? ` · ${step.attempts}×` : "")),
  ));

  // In-flight patch work for test/e2e/review cycle steps.
  if (step.patch) node.append(renderPatchStrip(step));

  if (step.error && !(step.patch && step.patch.status === "in_progress")) {
    node.append(h("div", {class: "node-err"}, step.error));
  }

  const sub = stepSummary(sp, step);
  if (sub) node.append(h("div", {class: "node-summary"}, sub));

  const det = buildStepDetails(sp, step);
  if (det) node.append(det);

  if (CYCLE_STEPS.has(step.name) && step.cycles && step.cycles.length) {
    node.append(renderCycles(step));
  }
  if (step.name === "build" && sp.specs && sp.specs.length) {
    node.append(renderSpecsList(sp.specs));
  }
  return node;
}

function renderPatchStrip(step) {
  const p = step.patch;
  const pdur = humanize(p.duration_seconds);
  const statusClass = p.status === "in_progress" ? "active"
                    : p.status === "failed"      ? "failed"
                    : p.status === "completed"   ? "done"
                    : "";
  const verb = p.status === "in_progress" ? "patching"
             : p.status === "completed"   ? "patched"
             : p.status === "failed"      ? "patch failed"
             : "patch " + p.status;
  return h("div", {class: "patch-strip " + statusClass},
    h("span", {class: "chain-chip " + statusClass},
      h("span", {class: "dot"}),
      verb + " · cycle " + p.attempts,
    ),
    h("span", {class: "patch-dur mono"}, pdur),
    p.error ? h("span", {class: "patch-err"}, p.error) : null,
  );
}

function stepSummary(sp, step) {
  switch (step.name) {
    case "research":
      return sp.research_doc ? `→ ${sp.research_doc}` : null;
    case "plan":
      return sp.specs && sp.specs.length
        ? `${sp.specs.length} specs planned · e2e ${sp.e2e_test_path || "—"}`
        : null;
    case "build": {
      if (!sp.specs || sp.specs.length === 0) return null;
      const done = sp.specs.filter(x => x.commit_status === "completed").length;
      return `${done} of ${sp.specs.length} specs committed`;
    }
    case "test":
      return sp.tests
        ? `${sp.tests.patch_cycles || 0} patch cycle(s) · ${sp.tests.summary || ""}`
        : null;
    case "e2e":
      return sp.e2e
        ? `${sp.e2e.patch_cycles || 0} patch cycle(s) · ${sp.e2e.summary || ""}`
        : null;
    case "review":
      return sp.review
        ? `${sp.review.patch_cycles || 0} patch cycle(s) · ${(sp.review.review_issues || []).length} issue(s)`
        : null;
    case "document":
      return sp.documentation && sp.documentation.length
        ? `${sp.documentation.length} doc(s) written`
        : null;
    case "publish":
      return sp.pr ? `PR #${sp.pr.number} ${sp.pr.merged ? "merged" : "open"}` : null;
  }
  return null;
}

function buildStepDetails(sp, step) {
  const hasDetail = step.log_path
    || (step.name === "research" && sp.research_doc)
    || (step.name === "plan" && sp.e2e_test_path)
    || (step.name === "test" && sp.tests)
    || (step.name === "e2e" && sp.e2e)
    || (step.name === "review" && sp.review);
  if (!hasDetail) return null;

  const key = `${sp.sprint_id}:${step.name}`;
  const det = h("details", {class: "node-details", ontoggle: (e) => {
    if (e.target.open) openKeys.add(key); else openKeys.delete(key);
  }});
  if (openKeys.has(key)) det.open = true;
  det.append(h("summary", {}, svgIcon("i-chevron", "chev"), "details"));

  const body = h("div", {class: "detail-body"});

  if (step.log_path) body.append(kvLine("log", fileLink(step.log_path)));

  if (step.name === "research" && sp.research_doc) {
    body.append(kvLine("research", fileLink(sp.research_doc)));
  }
  if (step.name === "plan") {
    if (sp.e2e_test_path) body.append(kvLine("e2e spec", fileLink(sp.e2e_test_path)));
    if (sp.specs) for (const sp2 of sp.specs) body.append(kvLine(sp2.id, fileLink(sp2.path)));
  }
  if (step.name === "test" && sp.tests) {
    body.append(kvLine("summary", sp.tests.summary || "—"));
    body.append(kvLine("tests executed", String(sp.tests.tests_executed ?? "—")));
    if (sp.tests.errors && sp.tests.errors.length) {
      body.append(sectionLabel(`Errors (${sp.tests.errors.length})`));
      body.append(renderErrors(sp.tests.errors));
    }
  }
  if (step.name === "e2e" && sp.e2e) {
    body.append(kvLine("summary", sp.e2e.summary || "—"));
    if (sp.e2e.failed_steps && sp.e2e.failed_steps.length) {
      body.append(sectionLabel("Failed steps (last cycle)"));
      body.append(h("ul", {class: "issue-list"},
        ...sp.e2e.failed_steps.map(f => h("li", {class: "blocker"},
          h("code", {}, f.step || "?"), " ", f.error || ""))));
    }
    if (sp.e2e.screenshots && sp.e2e.screenshots.length) {
      body.append(sectionLabel("Screenshots (last cycle)"));
      body.append(renderScreenshots(sp.e2e.screenshots));
    }
  }
  if (step.name === "review" && sp.review) {
    const issues = sp.review.review_issues || [];
    const blk = issues.filter(i => i.issue_severity === "blocker");
    const nb  = issues.filter(i => i.issue_severity !== "blocker");
    body.append(kvLine("summary", sp.review.review_summary || "—"));
    if (blk.length) {
      body.append(sectionLabel(`Blockers (${blk.length})`));
      body.append(h("ul", {class: "issue-list"},
        ...blk.map(i => h("li", {class: "blocker"}, i.issue_title || JSON.stringify(i)))));
    }
    if (nb.length) {
      body.append(sectionLabel(`Non-blockers (${nb.length})`));
      body.append(h("ul", {class: "issue-list"},
        ...nb.map(i => h("li", {class: "non-blocker"}, i.issue_title || JSON.stringify(i)))));
    }
    if (sp.review.screenshots && sp.review.screenshots.length) {
      body.append(sectionLabel("Screenshots"));
      body.append(renderScreenshots(sp.review.screenshots));
    }
  }

  det.append(body);
  return det;
}

function sectionLabel(text) {
  return h("div", {
    class: "label",
    style: "margin-top: 10px; display:block",
  }, text);
}

function fileLink(path) {
  return h("a", {
    href: "/file?path=" + encodeURIComponent(path),
    target: "_blank", rel: "noopener"
  }, path);
}

function kvLine(k, v) {
  const el = h("div", {class: "kv-row"});
  el.append(h("span", {class: "k"}, k));
  const vEl = h("span", {class: "v"});
  vEl.append(typeof v === "string" ? document.createTextNode(v) : v);
  el.append(vEl);
  return el;
}

function renderErrors(errs) {
  const ul = h("ul", {class: "issue-list"});
  for (const e of errs.slice(0, 25)) {
    const loc = e.file ? `${e.file}${e.line ? ":" + e.line : ""}` : "";
    ul.append(h("li", {class: "blocker"},
      loc ? h("code", {}, loc) : null,
      loc ? " " : "",
      e.message || ""));
  }
  if (errs.length > 25) ul.append(h("li", {style:"color:var(--muted); background:transparent; border:none; padding-left:0"},
    `(${errs.length - 25} more)`));
  return ul;
}

function renderScreenshots(paths) {
  const grid = h("div", {class: "screenshots"});
  for (const p of paths) {
    const link = h("a", {href: "/file?path=" + encodeURIComponent(p), target: "_blank", rel: "noopener"});
    const img = h("img", {
      src: "/file?path=" + encodeURIComponent(p),
      alt: "screenshot: " + p,
      loading: "lazy",
      onerror: function() {
        this.replaceWith(Object.assign(document.createElement("div"), {
          className: "missing",
          textContent: "unavailable"
        }));
      }
    });
    link.append(img);
    grid.append(link);
  }
  return grid;
}

function renderCycles(step) {
  const wrap = h("div", {class: "cycles"});
  for (const c of step.cycles) {
    const cls = c.passed === true ? "pass" : c.passed === false ? "fail" : "";
    const node = h("div", {class: "cycle " + cls});
    const label = `cycle ${c.cycle} · ${step.name}`;
    const verdict = c.passed === true ? "passed" : c.passed === false ? "failed" : "unknown";

    node.append(h("div", {class: "cycle-head"},
      h("span", {class: "cycle-label"}, label),
      h("span", {class: "cycle-verdict"}, verdict),
    ));
    if (c.summary) node.append(h("div", {style: "margin-top:4px; color: var(--fg-dim); font-size: 12.5px;"}, c.summary));

    const key = `cycle:${step.name}:${c.cycle}`;
    const det = h("details", {class: "node-details", style: "margin-left:0", ontoggle: (e) => {
      if (e.target.open) openKeys.add(key); else openKeys.delete(key);
    }});
    if (openKeys.has(key)) det.open = true;
    det.append(h("summary", {}, svgIcon("i-chevron", "chev"), "details"));
    const body = h("div", {class: "detail-body"});

    if (c.result_path)      body.append(kvLine("result",       fileLink(c.result_path)));
    if (c.cycle_log)        body.append(kvLine("cycle log",    fileLink(c.cycle_log)));
    if (c.patch_log)        body.append(kvLine("patch log",    fileLink(c.patch_log)));
    if (c.patch_commit_log) body.append(kvLine("patch commit", fileLink(c.patch_commit_log)));

    if (c.errors && c.errors.length) {
      body.append(sectionLabel(`Errors (${c.errors.length})`));
      body.append(renderErrors(c.errors));
    }
    if (c.failed_steps && c.failed_steps.length) {
      body.append(sectionLabel("Failed steps"));
      const ul = h("ul", {class: "issue-list"});
      for (const f of c.failed_steps) {
        const li = h("li", {class: "blocker"}, h("code", {}, f.step || "?"), " ", f.error || "");
        if (f.screenshot) li.append(" ", h("a", {href: "/file?path=" + encodeURIComponent(f.screenshot), target: "_blank", rel: "noopener"}, "screenshot"));
        ul.append(li);
      }
      body.append(ul);
    }
    if (c.blockers && c.blockers.length) {
      body.append(sectionLabel(`Blockers (${c.blockers.length})`));
      body.append(h("ul", {class: "issue-list"},
        ...c.blockers.map(i => h("li", {class: "blocker"}, i.issue_title || JSON.stringify(i)))));
    }
    if (c.non_blockers && c.non_blockers.length) {
      body.append(sectionLabel(`Non-blockers (${c.non_blockers.length})`));
      body.append(h("ul", {class: "issue-list"},
        ...c.non_blockers.map(i => h("li", {class: "non-blocker"}, i.issue_title || JSON.stringify(i)))));
    }
    if (c.screenshots && c.screenshots.length) {
      body.append(sectionLabel("Screenshots"));
      body.append(renderScreenshots(c.screenshots));
    }

    det.append(body);
    node.append(det);
    wrap.append(node);
  }
  return wrap;
}

function renderSpecsList(specs) {
  const wrap = h("div", {class: "specs-list"});
  for (const sp of specs) {
    const status = sp.build_status === "completed" && sp.commit_status === "completed"
      ? "completed" : sp.build_status;
    const node = h("div", {class: "spec status-" + status});
    node.append(h("div", {class: "spec-head"},
      h("span", {class: "spec-id"}, sp.id),
      h("span", {class: "spec-title"}, sp.title || ""),
    ));
    node.append(h("div", {class: "spec-row"},
      statusPill(sp.build_status, "build"),
      statusPill(sp.commit_status, "commit"),
      sp.commit_sha ? h("code", {}, sp.commit_sha) : null,
      h("span", {style: "margin-left:auto"}, humanize(sp.build_duration_seconds)),
    ));
    if (sp.build_summary)  node.append(h("div", {style: "margin-top:6px; color: var(--fg-dim); font-size:13px;"}, sp.build_summary));
    if (sp.commit_message) node.append(h("div", {style: "margin-top:2px; color: var(--muted); font-size:12.5px;"}, sp.commit_message));
    if (sp.build_error)    node.append(h("div", {class: "node-err", style:"margin-left:0"}, sp.build_error));

    const key = `spec:${sp.id}`;
    const det = h("details", {class: "node-details", style: "margin-left:0", ontoggle: (e) => {
      if (e.target.open) openKeys.add(key); else openKeys.delete(key);
    }});
    if (openKeys.has(key)) det.open = true;
    det.append(h("summary", {}, svgIcon("i-chevron", "chev"), "details"));
    const body = h("div", {class: "detail-body"});
    body.append(kvLine("spec", fileLink(sp.path)));
    if (sp.build_log_path)  body.append(kvLine("build log",  fileLink(sp.build_log_path)));
    if (sp.commit_log_path) body.append(kvLine("commit log", fileLink(sp.commit_log_path)));
    if (sp.documentation)   body.append(kvLine("doc",        fileLink(sp.documentation)));
    det.append(body);
    node.append(det);

    wrap.append(node);
  }
  return wrap;
}

function statusPill(status, prefix) {
  return h("span", {class: "pill status-" + status},
    h("span", {class: "pill-dot"}),
    `${prefix} ${status}`);
}

refresh();
setInterval(refresh, REFRESH_MS);
</script>
</body>
</html>"""


# ─── HTTP handler ──────────────────────────────────────────────────────────

class StatusHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        return  # silence default access log

    def _resolve_run(self) -> Optional[Path]:
        qs = self.path.split("?", 1)[1] if "?" in self.path else ""
        params = urllib.parse.parse_qs(qs)
        requested = (params.get("run") or [None])[0]
        if requested:
            candidate = RUNS_DIR / requested
            if candidate.is_dir() and (candidate / "state.json").exists():
                return candidate
        forced = getattr(self.server, "forced_run_id", None)
        if forced:
            pinned = RUNS_DIR / forced
            return pinned if pinned.is_dir() else None
        return latest_run()

    def _send(self, status: int, body: bytes, ctype: str,
              extra_headers: Optional[dict] = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status: int, text: str, ctype: str = "text/html; charset=utf-8") -> None:
        self._send(status, text.encode("utf-8"), ctype)

    def _send_json(self, status: int, data: Any) -> None:
        self._send(status, json.dumps(data, indent=2).encode("utf-8"),
                   "application/json; charset=utf-8")

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]

        if path == "/healthz":
            self._send_text(200, "ok\n", "text/plain; charset=utf-8")
            return

        if path == "/":
            self._send_text(200, PAGE_HTML)
            return

        if path == "/api/runs":
            self._send_json(200, [p.name for p in list_runs()])
            return

        if path == "/api/status":
            run_dir = self._resolve_run()
            if run_dir is None:
                self._send_json(404, {"error": "no runs found"})
                return
            self._send_json(200, build_snapshot(run_dir))
            return

        if path == "/file":
            self._serve_file()
            return

        self._send_text(404, "not found", "text/plain")

    def _serve_file(self) -> None:
        qs = self.path.split("?", 1)[1] if "?" in self.path else ""
        params = urllib.parse.parse_qs(qs)
        raw = (params.get("path") or [""])[0]
        if not raw:
            self._send_text(400, "missing path", "text/plain")
            return
        # Accept both absolute paths and REPO_ROOT-relative ones.
        p = Path(raw)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not is_safe_path(p):
            self._send_text(403, "path outside safe roots or not a file", "text/plain")
            return
        ext = p.suffix.lower()
        if ext in IMG_EXTS:
            ctype, _ = mimetypes.guess_type(str(p))
            ctype = ctype or "application/octet-stream"
            try:
                data = p.read_bytes()
            except OSError as e:
                self._send_text(500, f"read error: {e}", "text/plain")
                return
            self._send(200, data, ctype)
            return
        if ext in TEXT_EXTS or ext == "":
            try:
                text = p.read_text(errors="replace")
            except OSError as e:
                self._send_text(500, f"read error: {e}", "text/plain")
                return
            # Tail large text files to keep the page responsive.
            lines = text.splitlines()
            if len(lines) > 2000:
                text = "… (truncated to last 2000 lines) …\n" + "\n".join(lines[-2000:])
            self._send_text(200, text, "text/plain; charset=utf-8")
            return
        self._send_text(415, f"unsupported extension: {ext}", "text/plain")


# ─── Server bootstrap ──────────────────────────────────────────────────────

class StatusServer(ThreadingHTTPServer):
    forced_run_id: Optional[str] = None


def detect_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--run-id", default=None,
                        help="pin the server to a specific run id; default = latest")
    args = parser.parse_args()

    server = StatusServer((args.host, args.port), StatusHandler)
    server.forced_run_id = args.run_id

    ip = detect_lan_ip()
    print(f"Pipeline status on http://{ip}:{args.port}/ "
          f"(also http://localhost:{args.port}/)")
    if args.run_id:
        print(f"Pinned to run: {args.run_id}")
    else:
        latest = latest_run()
        print(f"Latest run: {latest.name if latest else '(none yet)'}")
    print("Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
        server.server_close()


if __name__ == "__main__":
    main()
