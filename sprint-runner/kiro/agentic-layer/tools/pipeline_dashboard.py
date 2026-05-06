#!/usr/bin/env python3
"""Live HTML dashboard for the sprint_runner pipeline.

Usage:
    python3 tools/pipeline_dashboard.py                    # latest run
    python3 tools/pipeline_dashboard.py --run <run_id>     # specific run
    python3 tools/pipeline_dashboard.py --port 8746        # custom port

Three-level drill-down:
  1. Sprints list
  2. Click sprint → canonical stage flow:
       research → plan → build → test → e2e → review → document → publish
  3. Click stage → its underlying sub-steps (patch cycles, retries, per-spec
     builds, per-spec documents) with duration/retries/credits/error/log paths.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional


REPO = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO / ".developer" / "sprint-runs"


# ---- canonical stages and their member-step prefixes --------------------

# Each canonical stage matches one or more runner step names. Order matters —
# this is the left-to-right flow displayed in the sprint view.
CANONICAL = [
    ("branch",   ["branch"]),
    ("research", ["research"]),
    ("plan",     ["plan"]),
    ("build",    ["build:"]),
    ("test",     ["test"]),
    ("e2e",      ["e2e", "e2e_patch"]),
    ("review",   ["review", "review_patch"]),
    ("document", ["document:"]),
    ("commit",   ["commit:"]),
    ("publish",  ["publish"]),
]


def steps_for_stage(stage: str, all_steps: list[dict]) -> list[dict]:
    """Return the sub-steps that roll up into one canonical stage."""
    prefixes = dict(CANONICAL)[stage]
    out = []
    for s in all_steps:
        name = s.get("name", "")
        # Match on prefix or exact equality, but prevent 'e2e' from
        # swallowing 'e2e_patch' members (both belong to stage 'e2e' — OK here)
        # and prevent 'commit' from swallowing 'commit:sprint-NN-NN' which
        # belongs to 'build' stage (per-spec build+commit pair).
        if stage == "commit":
            # only docs commit rolls into publish-side 'commit'
            if name.startswith("commit:docs-"):
                out.append(s)
        elif stage == "build":
            # per-spec builds AND their sibling per-spec commits
            if name.startswith("build:") or (name.startswith("commit:") and not name.startswith("commit:docs-")):
                out.append(s)
        else:
            for p in prefixes:
                if p.endswith(":"):
                    if name.startswith(p):
                        out.append(s)
                        break
                else:
                    if name == p or name.startswith(p + "-") or name.startswith(p + "_"):
                        out.append(s)
                        break
    return out


def rollup_status(sub_steps: list[dict]) -> str:
    """Aggregate sub-step statuses into one canonical-stage status."""
    if not sub_steps:
        return "pending"
    statuses = [s.get("status", "pending") for s in sub_steps]
    if any(s == "in_progress" for s in statuses):
        return "in_progress"
    if any(s == "failed" for s in statuses):
        # if a later sub-step succeeded after a failure, still call it completed
        # (self-heal). But if the *last* sub-step failed, it's failed.
        return "failed" if statuses[-1] == "failed" else "completed"
    if all(s == "completed" for s in statuses):
        return "completed"
    return "pending"


def rollup_totals(sub_steps: list[dict]) -> dict[str, Any]:
    total_dur = sum(s.get("duration_seconds") or 0 for s in sub_steps)
    total_credits = sum((s.get("credits") or 0) for s in sub_steps)
    total_retries = sum((s.get("transient_retries") or 0) for s in sub_steps)
    return {
        "duration_seconds": total_dur,
        "credits": total_credits if total_credits else None,
        "transient_retries": total_retries,
        "count": len(sub_steps),
    }


def sprint_credits_total(sprint: dict) -> float:
    return sum((s.get("credits") or 0) for s in sprint.get("steps", []))


# ---- IO helpers ---------------------------------------------------------

def latest_run() -> Optional[Path]:
    if not RUNS_DIR.exists():
        return None
    runs = sorted([p for p in RUNS_DIR.iterdir() if p.is_dir()],
                  key=lambda p: p.name, reverse=True)
    return runs[0] if runs else None


def load_state(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "state.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def load_lock(run_dir: Path) -> Optional[dict[str, Any]]:
    path = run_dir / "RUNNING.lock"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def find_sprint(state: dict, sid: str) -> Optional[dict]:
    for sp in state.get("sprints", []):
        if sp.get("sprint_id") == sid:
            return sp
    return None


# ---- formatting ---------------------------------------------------------

def fmt_duration(seconds: float) -> str:
    if not seconds or seconds < 1:
        return "—"
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m{s % 60:02d}s"
    return f"{s // 3600}h{(s % 3600) // 60:02d}m"


def esc(value: Any) -> str:
    """Minimal HTML escape."""
    s = "" if value is None else str(value)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


# ---- render: header -----------------------------------------------------

def render_header(state: dict, lock: Optional[dict], run_dir: Path) -> str:
    run_id = state.get("run_id", run_dir.name)
    selector = state.get("sprint_selector", "")
    status = state.get("status", "pending")
    updated = state.get("updated_at", "")

    if lock:
        heartbeat = lock.get("heartbeat_at", "")
        pid = lock.get("pid", "?")
        try:
            hb = datetime.fromisoformat(heartbeat.replace("Z", "+00:00"))
            age = int((datetime.now(timezone.utc) - hb).total_seconds())
            live = f"● LIVE pid={pid} ({age}s since heartbeat)"
        except (ValueError, AttributeError):
            live = f"● LIVE pid={pid}"
        live_class = "running"
    else:
        live = "○ STOPPED"
        live_class = "fail" if status == "failed" else "pending"

    hk = {"completed": "ok", "in_progress": "running", "failed": "fail"}.get(status, "pending")
    return (
        f'<header class="{hk}">'
        f'<div class="run"><b>{esc(run_id)}</b> <span class="sel">{esc(selector)}</span></div>'
        f'<div class="live {live_class}">{esc(live)}</div>'
        f'<div class="meta">selector <b>{esc(selector)}</b> • status <b>{esc(status)}</b> • updated {esc(updated)}</div>'
        f'</header>'
    )


# ---- render: level 1 — sprint list -------------------------------------

def render_sprints_list(state: dict) -> str:
    cards = []
    for sp in state.get("sprints", []):
        sid = sp.get("sprint_id", "?")
        title = sp.get("title") or sp.get("slug", "")
        status = sp.get("status", "pending")
        dur = fmt_duration(sp.get("duration_seconds") or 0)
        n_steps = len(sp.get("steps", []))
        errs = len(sp.get("errors") or [])
        credits = sprint_credits_total(sp)
        credits_txt = f"◈ {credits:.2f}" if credits else "◈ —"
        klass = {"completed": "ok", "in_progress": "running", "failed": "fail"}.get(status, "pending")
        err_html = f'<span class="errcount">{errs} err</span>' if errs else ""
        cards.append(
            f'<a class="sprint-card {klass}" href="#/sprint/{esc(sid)}">'
            f'<div class="sc-head"><span class="sid">sprint {esc(sid)}</span>'
            f'<span class="sc-dur">{esc(dur)}</span></div>'
            f'<div class="sc-title">{esc(title)}</div>'
            f'<div class="sc-foot"><span class="status {klass}">{esc(status)}</span>'
            f'<span class="credits">{esc(credits_txt)}</span>'
            f'<span class="stepcount">{n_steps} steps</span>{err_html}</div>'
            f'</a>'
        )
    body = "".join(cards) or '<div class="empty">no sprints in state</div>'
    return f'<main class="sprints-list">{body}</main>'


# ---- render: level 2 — sprint workflow ---------------------------------

def render_sprint_view(state: dict, sprint: dict) -> str:
    sid = sprint.get("sprint_id", "?")
    title = sprint.get("title") or sprint.get("slug", "")
    status = sprint.get("status", "pending")
    dur = fmt_duration(sprint.get("duration_seconds") or 0)
    all_steps = sprint.get("steps", [])
    total_credits = sprint_credits_total(sprint)
    credits_txt = f"{total_credits:.2f}" if total_credits else "—"

    stage_boxes = []
    for stage_name, _ in CANONICAL:
        subs = steps_for_stage(stage_name, all_steps)
        rstatus = rollup_status(subs)
        totals = rollup_totals(subs)
        klass = {"completed": "ok", "in_progress": "running", "failed": "fail"}.get(rstatus, "pending")
        count_badge = f'<span class="count">×{totals["count"]}</span>' if totals["count"] > 1 else ""
        retry_badge = f'<span class="retry">⟳{totals["transient_retries"]}</span>' if totals["transient_retries"] else ""
        dur_txt = fmt_duration(totals["duration_seconds"])
        stage_boxes.append(
            f'<a class="stage {klass}" href="#/sprint/{esc(sid)}/stage/{esc(stage_name)}">'
            f'<div class="stage-name">{esc(stage_name)}</div>'
            f'<div class="stage-dur">{esc(dur_txt)}</div>'
            f'<div class="stage-badges">{count_badge}{retry_badge}</div>'
            f'</a>'
        )
    flow = "<div class=\"flow\">" + '<div class="arrow">→</div>'.join(stage_boxes) + "</div>"

    errs_html = ""
    errs = sprint.get("errors") or []
    if errs:
        lines = "".join(
            f'<li><b>{esc(e.get("step", "?"))}</b>: {esc(e.get("error", ""))}</li>'
            for e in errs
        )
        errs_html = f'<section class="sprint-errors"><h3>errors logged</h3><ul>{lines}</ul></section>'

    return (
        f'<main class="sprint-view">'
        f'<div class="breadcrumb"><a href="#/">← all sprints</a></div>'
        f'<div class="sv-head"><h2>sprint {esc(sid)} · {esc(title)}</h2>'
        f'<div class="sv-meta">status <b>{esc(status)}</b> • duration <b>{esc(dur)}</b> • total credits <b>◈ {esc(credits_txt)}</b></div></div>'
        f'{flow}'
        f'{errs_html}'
        f'</main>'
    )


# ---- render: level 3 — stage detail ------------------------------------

def render_substep_row(s: dict, run_dir: Path) -> str:
    name = s.get("name", "?")
    status = s.get("status", "pending")
    klass = {"completed": "ok", "in_progress": "running", "failed": "fail"}.get(status, "pending")
    dur = fmt_duration(s.get("duration_seconds") or 0)
    credits = s.get("credits")
    credits_txt = f"{credits:.2f}" if credits else "—"
    retries = s.get("transient_retries") or 0
    attempts = s.get("attempts") or 1
    exit_code = s.get("exit_code")
    exit_txt = "—" if exit_code is None else str(exit_code)
    error = s.get("error") or ""

    # log/prompt paths relative to repo if possible
    def rel(p):
        if not p:
            return ""
        try:
            return str(Path(p).relative_to(REPO))
        except (ValueError, OSError):
            return str(p)

    log_path = rel(s.get("log_path"))
    prompt_path = rel(s.get("prompt_path"))
    result_path = rel(s.get("result_path"))
    paths = []
    if log_path:
        paths.append(f'<span class="path">log: <code>{esc(log_path)}</code></span>')
    if prompt_path:
        paths.append(f'<span class="path">prompt: <code>{esc(prompt_path)}</code></span>')
    if result_path:
        paths.append(f'<span class="path">result: <code>{esc(result_path)}</code></span>')
    paths_html = '<div class="paths">' + ' · '.join(paths) + '</div>' if paths else ''

    err_html = f'<div class="err">{esc(error)}</div>' if error else ''

    return (
        f'<div class="substep {klass}">'
        f'<div class="ss-head">'
        f'<span class="ss-name">{esc(name)}</span>'
        f'<span class="ss-status {klass}">{esc(status)}</span>'
        f'</div>'
        f'<div class="ss-meta">'
        f'<span>dur <b>{esc(dur)}</b></span>'
        f'<span>credits <b>{esc(credits_txt)}</b></span>'
        f'<span>retries <b>{esc(retries)}</b></span>'
        f'<span>attempts <b>{esc(attempts)}</b></span>'
        f'<span>exit <b>{esc(exit_txt)}</b></span>'
        f'</div>'
        f'{paths_html}'
        f'{err_html}'
        f'</div>'
    )


def render_stage_view(state: dict, sprint: dict, stage: str, run_dir: Path) -> str:
    sid = sprint.get("sprint_id", "?")
    title = sprint.get("title") or sprint.get("slug", "")
    all_steps = sprint.get("steps", [])
    subs = steps_for_stage(stage, all_steps)
    rstatus = rollup_status(subs)
    totals = rollup_totals(subs)
    klass = {"completed": "ok", "in_progress": "running", "failed": "fail"}.get(rstatus, "pending")

    rows = "".join(render_substep_row(s, run_dir) for s in subs) or '<div class="empty">no sub-steps yet</div>'

    credits_total = f'{totals["credits"]:.2f}' if totals["credits"] else "—"
    return (
        f'<main class="stage-view">'
        f'<div class="breadcrumb">'
        f'<a href="#/">all sprints</a> / '
        f'<a href="#/sprint/{esc(sid)}">sprint {esc(sid)}</a> / '
        f'<b>{esc(stage)}</b>'
        f'</div>'
        f'<div class="sv-head"><h2>stage · {esc(stage)}</h2>'
        f'<div class="sv-meta">'
        f'sprint <b>{esc(sid)}</b> — {esc(title)} • '
        f'status <span class="status {klass}">{esc(rstatus)}</span> • '
        f'total dur <b>{esc(fmt_duration(totals["duration_seconds"]))}</b> • '
        f'credits <b>{esc(credits_total)}</b> • '
        f'transient retries <b>{totals["transient_retries"]}</b>'
        f'</div></div>'
        f'<section class="substeps">{rows}</section>'
        f'</main>'
    )


# ---- render: dispatch by hash route -------------------------------------

def render_body(run_dir: Path, route: str) -> str:
    state = load_state(run_dir)
    lock = load_lock(run_dir)
    if not state:
        return '<div class="empty">no state.json found</div>'

    header = render_header(state, lock, run_dir)

    # routes:
    #   ""  or  "/"              → sprints list
    #   "/sprint/05"             → sprint 05 workflow
    #   "/sprint/05/stage/e2e"   → e2e stage detail for sprint 05
    parts = [p for p in route.strip("/").split("/") if p]
    if len(parts) >= 4 and parts[0] == "sprint" and parts[2] == "stage":
        sp = find_sprint(state, parts[1])
        if sp is None:
            return header + f'<div class="empty">sprint {esc(parts[1])} not found</div>'
        return header + render_stage_view(state, sp, parts[3], run_dir)
    if len(parts) >= 2 and parts[0] == "sprint":
        sp = find_sprint(state, parts[1])
        if sp is None:
            return header + f'<div class="empty">sprint {esc(parts[1])} not found</div>'
        return header + render_sprint_view(state, sp)
    return header + render_sprints_list(state)


# ---- page shell --------------------------------------------------------

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>pipeline — {run_id}</title>
<style>
  :root {{
    --bg: #0e1116; --fg: #e6edf3; --muted: #8b949e;
    --ok: #2ea043; --run: #1f6feb; --fail: #da3633; --pend: #30363d;
    --card: #161b22; --border: #30363d; --hover: #1c2330;
  }}
  * {{ box-sizing: border-box; }}
  body {{ background: var(--bg); color: var(--fg); font: 13px/1.4 -apple-system,system-ui,sans-serif; margin: 0; padding: 16px; }}
  a {{ color: inherit; text-decoration: none; }}
  code {{ font: 11.5px/1.3 ui-monospace,monospace; color: var(--fg); background: rgba(255,255,255,0.05); padding: 1px 4px; border-radius: 3px; }}

  /* header */
  header {{ padding: 12px 16px; border-radius: 8px; background: var(--card); border: 1px solid var(--border); margin-bottom: 16px; display: grid; grid-template-columns: 1fr auto; grid-template-rows: auto auto; gap: 4px 16px; }}
  header.ok {{ border-left: 4px solid var(--ok); }}
  header.running {{ border-left: 4px solid var(--run); }}
  header.fail {{ border-left: 4px solid var(--fail); }}
  header.pending {{ border-left: 4px solid var(--pend); }}
  header .run {{ font-size: 16px; }}
  header .sel {{ color: var(--muted); font-weight: normal; margin-left: 12px; }}
  header .live {{ justify-self: end; font-weight: 600; letter-spacing: 0.3px; }}
  header .live.running {{ color: var(--run); animation: pulse 1.5s ease-in-out infinite; }}
  header .live.fail {{ color: var(--fail); }}
  header .live.pending {{ color: var(--muted); }}
  header .meta {{ grid-column: 1 / -1; color: var(--muted); font-size: 12px; }}
  @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.55; }} }}

  /* breadcrumb */
  .breadcrumb {{ color: var(--muted); margin-bottom: 16px; font-size: 12px; }}
  .breadcrumb a {{ color: var(--run); }}
  .breadcrumb a:hover {{ text-decoration: underline; }}

  /* level 1: sprints list */
  .sprints-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }}
  .sprint-card {{ display: block; background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; cursor: pointer; transition: background 0.12s, border-color 0.12s; }}
  .sprint-card:hover {{ background: var(--hover); border-color: var(--muted); }}
  .sprint-card.ok {{ border-left: 4px solid var(--ok); }}
  .sprint-card.running {{ border-left: 4px solid var(--run); }}
  .sprint-card.fail {{ border-left: 4px solid var(--fail); }}
  .sprint-card.pending {{ border-left: 4px solid var(--pend); }}
  .sc-head {{ display: flex; justify-content: space-between; align-items: baseline; }}
  .sc-head .sid {{ font-weight: 700; font-size: 14px; }}
  .sc-head .sc-dur {{ color: var(--muted); font: 11px/1.3 ui-monospace,monospace; }}
  .sc-title {{ margin: 6px 0 10px 0; color: var(--fg); font-size: 12.5px; }}
  .sc-foot {{ display: flex; gap: 8px; align-items: center; font-size: 10.5px; color: var(--muted); }}
  .status {{ padding: 2px 6px; border-radius: 3px; font-weight: 600; font-size: 10px; text-transform: uppercase; letter-spacing: 0.3px; }}
  .status.ok {{ background: rgba(46,160,67,0.15); color: var(--ok); }}
  .status.running {{ background: rgba(31,111,235,0.15); color: var(--run); }}
  .status.fail {{ background: rgba(218,54,51,0.15); color: var(--fail); }}
  .status.pending {{ background: rgba(139,148,158,0.15); color: var(--muted); }}
  .errcount {{ color: var(--fail); font-weight: 600; }}
  .sc-foot .credits {{ color: var(--fg); font: 10.5px/1 ui-monospace,monospace; font-weight: 600; margin-left: auto; }}

  /* level 2: sprint workflow */
  .sv-head h2 {{ margin: 0; font-size: 18px; }}
  .sv-head .sv-meta {{ color: var(--muted); margin-top: 4px; font-size: 12px; }}
  .flow {{ display: flex; flex-wrap: wrap; gap: 4px; align-items: stretch; margin: 24px 0; }}
  .stage {{ flex: 1 1 0; min-width: 110px; background: var(--card); border: 1px solid var(--border); border-radius: 6px; padding: 10px 8px; text-align: center; cursor: pointer; transition: background 0.12s, border-color 0.12s; }}
  .stage:hover {{ background: var(--hover); }}
  .stage.ok {{ border-top: 3px solid var(--ok); }}
  .stage.running {{ border-top: 3px solid var(--run); animation: pulse 1.5s ease-in-out infinite; }}
  .stage.fail {{ border-top: 3px solid var(--fail); }}
  .stage.pending {{ border-top: 3px solid var(--pend); color: var(--muted); }}
  .stage-name {{ font-weight: 700; font-size: 12.5px; text-transform: lowercase; }}
  .stage-dur {{ color: var(--muted); font: 11px/1.4 ui-monospace,monospace; margin-top: 4px; }}
  .stage-badges {{ margin-top: 4px; display: flex; gap: 4px; justify-content: center; font: 10px/1 ui-monospace,monospace; }}
  .stage-badges .count {{ background: rgba(139,148,158,0.2); padding: 1px 4px; border-radius: 3px; color: var(--fg); }}
  .stage-badges .retry {{ background: rgba(218,54,51,0.2); padding: 1px 4px; border-radius: 3px; color: var(--fail); }}
  .arrow {{ display: flex; align-items: center; color: var(--muted); font-size: 14px; padding: 0 2px; }}

  .sprint-errors {{ margin-top: 24px; background: rgba(218,54,51,0.06); border: 1px solid var(--fail); border-radius: 6px; padding: 12px; }}
  .sprint-errors h3 {{ margin: 0 0 8px 0; font-size: 13px; color: var(--fail); }}
  .sprint-errors ul {{ margin: 0; padding-left: 18px; font-size: 12px; }}

  /* level 3: stage detail */
  .substeps {{ display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }}
  .substep {{ background: var(--card); border: 1px solid var(--border); border-radius: 6px; padding: 10px 12px; }}
  .substep.ok {{ border-left: 3px solid var(--ok); }}
  .substep.running {{ border-left: 3px solid var(--run); }}
  .substep.fail {{ border-left: 3px solid var(--fail); }}
  .substep.pending {{ border-left: 3px solid var(--pend); }}
  .ss-head {{ display: flex; justify-content: space-between; align-items: baseline; }}
  .ss-name {{ font: 12.5px/1.3 ui-monospace,monospace; font-weight: 700; }}
  .ss-status {{ padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; text-transform: uppercase; }}
  .ss-meta {{ display: flex; gap: 16px; margin-top: 6px; color: var(--muted); font-size: 11.5px; flex-wrap: wrap; }}
  .ss-meta b {{ color: var(--fg); font-weight: 600; }}
  .paths {{ margin-top: 6px; font-size: 11px; color: var(--muted); }}
  .paths .path {{ margin-right: 10px; }}
  .err {{ margin-top: 8px; padding: 8px; background: rgba(218,54,51,0.08); border: 1px solid var(--fail); border-radius: 4px; color: var(--fail); font-size: 11.5px; white-space: pre-wrap; }}

  .empty {{ padding: 40px; text-align: center; color: var(--muted); }}
  footer {{ margin-top: 24px; color: var(--muted); font-size: 11px; text-align: right; }}
</style>
</head>
<body>
<div id="root">{body}</div>
<footer>auto-refresh every 3s · <span id="clock"></span></footer>
<script>
  function currentRoute() {{
    const h = window.location.hash || '';
    return h.replace(/^#/, '');
  }}
  function tick() {{
    document.getElementById('clock').textContent = new Date().toLocaleTimeString();
  }}
  async function refresh() {{
    try {{
      const r = await fetch('/body?route=' + encodeURIComponent(currentRoute()));
      if (!r.ok) return;
      document.getElementById('root').innerHTML = await r.text();
    }} catch (e) {{ /* swallow */ }}
  }}
  tick();
  setInterval(tick, 1000);
  setInterval(refresh, 3000);
  window.addEventListener('hashchange', refresh);
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    run_dir: Path  # set by main

    def _send(self, code: int, body: str, ctype: str = "text/html; charset=utf-8") -> None:
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        # parse query
        path = self.path
        query = ""
        if "?" in path:
            path, query = path.split("?", 1)
        route = ""
        for part in query.split("&"):
            if part.startswith("route="):
                import urllib.parse
                route = urllib.parse.unquote(part[len("route="):])

        if path == "/body":
            self._send(200, render_body(self.run_dir, route))
            return
        if path in ("/", "/index.html"):
            state = load_state(self.run_dir)
            self._send(200, PAGE.format(run_id=state.get("run_id", self.run_dir.name),
                                         body=render_body(self.run_dir, "")))
            return
        self._send(404, "not found", "text/plain")

    def log_message(self, *_: Any) -> None:  # quiet
        pass


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", help="run id (directory name under .developer/sprint-runs/)")
    ap.add_argument("--port", type=int, default=8746)
    args = ap.parse_args()

    if args.run:
        run_dir = RUNS_DIR / args.run
        if not run_dir.exists():
            raise SystemExit(f"run not found: {run_dir}")
    else:
        run_dir = latest_run()
        if run_dir is None:
            raise SystemExit(f"no runs found under {RUNS_DIR}")

    Handler.run_dir = run_dir
    addr = ("127.0.0.1", args.port)
    print(f"pipeline dashboard: http://{addr[0]}:{addr[1]}/  run={run_dir.name}")
    ThreadingHTTPServer(addr, Handler).serve_forever()


if __name__ == "__main__":
    main()
