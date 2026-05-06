#!/usr/bin/env python3
"""Agentic pipeline sprint runner (Kiro CLI, headless).

Single-file stdlib orchestrator. Driven by pipeline.yaml in target project.
Grown task-by-task per plans/agentic-pipeline-runner-plan.md.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import select
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional


def now_iso() -> str:
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0, tzinfo=None).isoformat() + "Z"


def log(msg: str) -> None:
    import datetime as _dt
    ts = _dt.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def fail(msg: str, code: int = 1) -> None:
    log(f"FATAL: {msg}")
    sys.exit(code)


# -------- minimal YAML loader (stdlib only) --------
# Supports the subset we emit: nested mappings, scalar strings/ints, lists of scalars.
def _parse_scalar(v: str) -> Any:
    v = v.strip()
    if v == "" or v.lower() in {"null", "~"}:
        return None
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    return v


def load_yaml(path: Path) -> dict:
    """Parse a restricted YAML subset: nested maps (2-space indent), scalars, inline lists []."""
    text = path.read_text()
    root: dict = {}
    # stack of (indent, container)
    stack: list[tuple[int, Any]] = [(-1, root)]
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        # pop until we find a parent with lesser indent
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        content = line.strip()
        # strip trailing comments (unquoted)
        if "#" in content:
            in_str = False
            qc = ""
            cut = -1
            for i, ch in enumerate(content):
                if ch in ("'", '"'):
                    if not in_str:
                        in_str = True
                        qc = ch
                    elif qc == ch:
                        in_str = False
                elif ch == "#" and not in_str and (i == 0 or content[i - 1].isspace()):
                    cut = i
                    break
            if cut >= 0:
                content = content[:cut].rstrip()
        if ":" not in content:
            fail(f"yaml parse error at line: {raw_line!r}")
        key, _, rest = content.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest == "":
            # either a map or a list follows at deeper indent
            new: dict = {}
            parent[key] = new
            stack.append((indent, new))
        elif rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            parent[key] = [_parse_scalar(x) for x in inner.split(",")] if inner else []
        else:
            parent[key] = _parse_scalar(rest)
    return root


# -------- Kiro runner --------
# Amendment A: Kiro headless emits a trailer line of shape:
#   ▸ Credits: 0.29 • Time: 5s         (< 1 minute)
#   ▸ Credits: 11.71 • Time: 5m 51s    (≥ 1 minute)
#   ▸ Credits: 99.00 • Time: 1h 2m 3s  (≥ 1 hour, defensive)
# Parse the LAST match (multi-turn).
_CREDITS_RE = re.compile(
    r"(?m)^\s*[▸>]\s*Credits:\s*([0-9.]+)\s*[•\*]\s*Time:\s*"
    r"(?:([0-9]+)h\s*)?(?:([0-9]+)m\s*)?(?:([0-9]+)s)?\s*$"
)

# Transient-error pattern (applied to captured stdout when exit==1).
_TRANSIENT_RE = re.compile(r"(?i)5\d\d|overloaded|rate[_ -]?limit|timeout")

MAX_TRANSIENT_RETRIES = 5
TRANSIENT_BACKOFF_BASE = 120
TRANSIENT_BACKOFF_CAP = 300


def classify_kiro_error(exit_code: int, stdout: str) -> str:
    """Return 'ok' | 'transient' | 'fatal'."""
    if exit_code == 0:
        return "ok"
    if exit_code == 3:  # MCP startup failure
        return "fatal"
    if exit_code == 1 and _TRANSIENT_RE.search(stdout):
        return "transient"
    return "fatal"


def parse_credits(text: str) -> tuple[Optional[float], Optional[int]]:
    """Return (credits, kiro_reported_seconds) or (None, None).

    Handles all three trailer forms Kiro emits:
      Time: 5s          -> 5
      Time: 5m 51s      -> 351
      Time: 1h 2m 3s    -> 3723
    """
    last = None
    for m in _CREDITS_RE.finditer(text):
        last = m
    if not last:
        return (None, None)
    credits = float(last.group(1))
    h = int(last.group(2) or 0)
    mi = int(last.group(3) or 0)
    s = int(last.group(4) or 0)
    return (credits, h * 3600 + mi * 60 + s)


@dataclasses.dataclass
class KiroResult:
    exit_code: int
    duration_seconds: float
    stdout: str
    log_path: Path
    prompt_path: Path
    prompt_bytes: int = 0
    stdout_bytes: int = 0
    error: Optional[str] = None
    error_kind: Optional[str] = None  # "transient" | "fatal" | None
    transient_retries: int = 0
    credits: Optional[float] = None
    kiro_reported_seconds: Optional[int] = None

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0 and not self.error


class KiroRunner:
    """Single invocation wrapper around `kiro-cli chat`."""

    BIN = "kiro-cli"

    def __init__(self, log_dir: Path, cwd: Path, dry_run: bool = False):
        self.log_dir = log_dir
        self.cwd = cwd
        self.dry_run = dry_run
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_mcp_enabled(self, agent: str) -> None:
        """Force every MCP server to `disabled: false` across all scopes Kiro merges.

        Self-healing patch cycles have repeatedly toggled MCP servers to
        `disabled: true` as a "workaround" when the browser wasn't reachable,
        which silently breaks the next e2e/test/review cycle. This re-enables
        them before every run so the agent always gets its tools.

        Kiro resolves MCP servers from four scopes (global, project, agent,
        runtime); project `.kiro/settings/mcp.json` can override the agent
        config, so sweeping only the agent file is not enough — all settings
        files must be patched too.
        """
        candidates = [
            self.cwd / ".kiro" / "agents" / f"{agent}.json",
            self.cwd / ".kiro" / "settings" / "mcp.json",
            Path.home() / ".kiro" / "settings" / "mcp.json",
        ]
        for cfg_path in candidates:
            if not cfg_path.exists():
                continue
            try:
                cfg = json.loads(cfg_path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            servers = cfg.get("mcpServers") or {}
            changed = False
            for name, spec in servers.items():
                if isinstance(spec, dict) and spec.get("disabled") is True:
                    spec["disabled"] = False
                    changed = True
                    log(f"  ⚡ re-enabled MCP server '{name}' in {cfg_path}")
            if changed:
                _atomic_write(cfg_path, json.dumps(cfg, indent=2) + "\n")

    def _kill_stale_mcp_servers(self) -> None:
        """Kill leftover `@playwright/mcp` processes before MCP-dependent stages.

        A crashed or aborted prior run can leave the Playwright MCP server
        holding a lock on its chrome profile directory. The next e2e/test/review
        stage then sees `browser_*` tools unavailable, falls back to writing
        ad-hoc `.mjs` scripts, and dirties the working tree. Killing stragglers
        here frees the profile lock so MCP starts cleanly.
        """
        try:
            result = subprocess.run(
                ["pgrep", "-f", "@playwright/mcp"],
                capture_output=True, text=True, check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return
        pids = [p for p in result.stdout.split() if p.strip().isdigit()]
        for pid in pids:
            try:
                os.kill(int(pid), signal.SIGTERM)
                log(f"  ⚡ killed stale @playwright/mcp pid={pid}")
            except (OSError, ProcessLookupError):
                continue

    def _paths(self, step: str, attempt: int, retry: int) -> tuple[Path, Path]:
        suffix = f"-attempt-{attempt}" if attempt else ""
        if retry:
            suffix += f"-retry-{retry}"
        prompt_path = self.log_dir / f"{step}{suffix}.prompt.txt"
        log_path = self.log_dir / f"{step}{suffix}.log"
        return prompt_path, log_path

    def _invoke_once(
        self,
        step: str,
        prompt: str,
        agent: str,
        timeout: int,
        attempt: int = 1,
        retry: int = 0,
        require_mcp_startup: bool = False,
    ) -> KiroResult:
        prompt_path, log_path = self._paths(step, attempt, retry)
        prompt_path.write_text(prompt)
        prompt_bytes = len(prompt.encode("utf-8"))
        self._ensure_mcp_enabled(agent)
        if require_mcp_startup:
            self._kill_stale_mcp_servers()
        log(f"→ {step} agent={agent}")

        if self.dry_run:
            stub = {"dry_run": True, "step": step, "agent": agent}
            log_path.write_text(json.dumps(stub) + "\n[dry run]\n")
            return KiroResult(
                exit_code=0, duration_seconds=0.0, stdout="[dry run]",
                log_path=log_path, prompt_path=prompt_path,
                prompt_bytes=prompt_bytes, stdout_bytes=0,
            )

        cmd = [self.BIN, "chat", "--no-interactive", "--trust-all-tools",
               "--agent", agent]
        if require_mcp_startup:
            cmd.append("--require-mcp-startup")
        cmd.append("--")
        cmd.append(prompt)

        t0 = time.monotonic()
        error: Optional[str] = None
        stdout_parts: list[str] = []
        exit_code = 1
        try:
            proc = subprocess.Popen(
                cmd, cwd=str(self.cwd), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, bufsize=1,
            )
            with log_path.open("w") as logf:
                assert proc.stdout is not None
                deadline = t0 + timeout
                # Kill if no stdout for this long (seconds). Guards against
                # wedged HTTP streams where kiro-cli stops emitting output.
                idle_limit = int(os.environ.get("KIRO_IDLE_TIMEOUT", "1400"))
                last_output = time.monotonic()
                while True:
                    if proc.poll() is not None:
                        rest = proc.stdout.read()
                        if rest:
                            logf.write(rest); logf.flush()
                            stdout_parts.append(rest)
                        break
                    ready, _, _ = select.select([proc.stdout], [], [], 5.0)
                    now = time.monotonic()
                    if ready:
                        line = proc.stdout.readline()
                        if line:
                            logf.write(line); logf.flush()
                            stdout_parts.append(line)
                            last_output = now
                    if now > deadline:
                        self._kill_proc(proc)
                        error = f"timeout after {timeout}s"
                        break
                    if now - last_output > idle_limit:
                        self._kill_proc(proc)
                        error = f"idle timeout: no stdout for {idle_limit}s"
                        # Append so classify_kiro_error sees 'idle timeout'.
                        stdout_parts.append(f"\n[runner] {error}\n")
                        break
                proc.wait(timeout=max(1, int(deadline - time.monotonic())))
            exit_code = proc.returncode if proc.returncode is not None else 1
        except subprocess.TimeoutExpired:
            self._kill_proc(proc)
            error = f"timeout after {timeout}s"
            exit_code = 124
        except KeyboardInterrupt:
            try:
                proc.send_signal(signal.SIGINT)
                proc.wait(timeout=5)
            except Exception:
                pass
            raise
        except Exception as e:
            error = repr(e)

        duration = time.monotonic() - t0
        stdout = "".join(stdout_parts)
        credits, kiro_s = parse_credits(stdout)
        result = KiroResult(
            exit_code=exit_code,
            duration_seconds=round(duration, 3),
            stdout=stdout,
            log_path=log_path,
            prompt_path=prompt_path,
            prompt_bytes=prompt_bytes,
            stdout_bytes=len(stdout.encode("utf-8")),
            error=error,
            credits=credits,
            kiro_reported_seconds=kiro_s,
        )
        log(f"← {step} exit={result.exit_code} dur={duration:.1f}s "
            f"credits={credits} agent={agent}")
        return result

    @staticmethod
    def _kill_proc(proc: subprocess.Popen) -> None:
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGKILL):
            try:
                proc.send_signal(sig)
                proc.wait(timeout=5)
                return
            except subprocess.TimeoutExpired:
                continue
            except ProcessLookupError:
                return

    def run(self, step: str, prompt: str, agent: str, timeout: int,
            attempt: int = 1, require_mcp_startup: bool = False) -> KiroResult:
        """Invoke Kiro with transient-error retry (up to MAX_TRANSIENT_RETRIES)."""
        import random as _random
        for retry in range(MAX_TRANSIENT_RETRIES + 1):
            result = self._invoke_once(step, prompt, agent, timeout,
                                       attempt=attempt, retry=retry,
                                       require_mcp_startup=require_mcp_startup)
            kind = classify_kiro_error(result.exit_code, result.stdout)
            if kind == "ok":
                result.transient_retries = retry
                return result
            result.error_kind = kind
            result.transient_retries = retry
            if kind != "transient" or retry >= MAX_TRANSIENT_RETRIES:
                return result
            backoff = min(
                TRANSIENT_BACKOFF_BASE + (2 ** retry) * 30 + _random.random() * 60,
                TRANSIENT_BACKOFF_CAP,
            )
            log(f"⚠ transient error on {step} (exit={result.exit_code}) — "
                f"retry {retry + 1}/{MAX_TRANSIENT_RETRIES} in {backoff:.0f}s")
            time.sleep(backoff)
        return result  # unreachable, satisfies type checker


# -------- Atomic JSON helpers --------
def _atomic_write(path: Path, data: str) -> None:
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}.{threading.get_ident()}")
    tmp.write_text(data)
    os.replace(tmp, path)


# -------- RunLock (heartbeat) --------
HEARTBEAT_INTERVAL = 5  # seconds


class RunLock:
    """Write <run_dir>/RUNNING.lock with a 5s heartbeat; daemon thread refreshes it.

    Clean exit removes the lock; a real crash leaves a stale `heartbeat_at` for
    a dashboard to detect abandonment.
    """

    def __init__(self, run_dir: Path):
        self.path = run_dir / "RUNNING.lock"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _payload(self) -> dict:
        return {
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "started_at": self._started_at,
            "heartbeat_at": now_iso(),
        }

    def _write(self) -> None:
        try:
            _atomic_write(self.path, json.dumps(self._payload(), indent=2))
        except OSError:
            pass  # never crash the run over a heartbeat write

    def _heartbeat_loop(self) -> None:
        while not self._stop.wait(HEARTBEAT_INTERVAL):
            self._write()

    def __enter__(self) -> "RunLock":
        self._started_at = now_iso()
        self._write()
        self._thread = threading.Thread(
            target=self._heartbeat_loop, name="runlock-heartbeat", daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=HEARTBEAT_INTERVAL + 1)
        try:
            self.path.unlink(missing_ok=True)
        except OSError:
            pass


# -------- State (atomic JSON persistence) --------
class State:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            self.data = json.loads(path.read_text())
        else:
            self.data = {}

    def save(self) -> None:
        self.data["updated_at"] = now_iso()
        _atomic_write(self.path, json.dumps(self.data, indent=2, default=str))

    def sprint(self, sprint_id: str) -> dict:
        for s in self.data.get("sprints", []):
            if s.get("sprint_id") == sprint_id:
                return s
        raise KeyError(sprint_id)

    def init_sprint(self, sprint_id: str, defaults: dict) -> dict:
        for s in self.data.setdefault("sprints", []):
            if s.get("sprint_id") == sprint_id:
                return s
        self.data["sprints"].append(defaults)
        return defaults


# -------- Config --------
class Config:
    def __init__(self, data: dict, root: Path):
        self.data = data
        self.root = root

    def path(self, key: str) -> Path:
        v = self.data.get(key)
        if not v:
            fail(f"config missing path key: {key}")
        p = Path(v)
        return p if p.is_absolute() else (self.root / p).resolve()

    @property
    def agents(self) -> dict:
        return self.data.get("agents", {}) or {}

    @property
    def stack(self) -> dict:
        return self.data.get("stack", {}) or {}

    @property
    def prompts_dir(self) -> Path:
        return (self.root / ".kiro" / "prompts").resolve()

    @classmethod
    def load(cls, path: Path) -> "Config":
        if not path.exists():
            fail(f"config not found: {path}")
        data = load_yaml(path)
        # root = parent of pipeline.yaml's containing tools/ dir, else cwd
        root = path.parent.parent if path.parent.name == "tools" else path.parent
        return cls(data, root)


# -------- Prompt renderer --------
def render_prompt(cfg: Config, name: str, vars: dict) -> str:
    """Load .kiro/prompts/<name>.md and substitute variables (literal replace).

    Supports: $ARGUMENTS, $ARGUMENT, $1..$9, {key} for any provided var key.
    """
    p = cfg.prompts_dir / f"{name}.md"
    if not p.exists():
        fail(f"prompt template not found: {p}")
    body = p.read_text()
    # Positional
    for i in range(1, 10):
        k = f"${i}"
        if k in vars:
            body = body.replace(k, str(vars[k]))
        pos_key = str(i)
        if pos_key in vars:
            body = body.replace(f"${i}", str(vars[pos_key]))
    if "ARGUMENTS" in vars:
        body = body.replace("$ARGUMENTS", str(vars["ARGUMENTS"]))
        body = body.replace("$ARGUMENT", str(vars["ARGUMENTS"]))
    # Named {curly} tokens
    for key, val in vars.items():
        if key.startswith("$") or key.isdigit() or key == "ARGUMENTS":
            continue
        body = body.replace("{" + key + "}", str(val))
    return body


# -------- Sprint + selectors --------
@dataclasses.dataclass
class Sprint:
    id: str
    slug: str
    path: Path
    title: str
    band: Optional[str] = None
    blocked_by: list[str] = dataclasses.field(default_factory=list)

    @classmethod
    def from_path(cls, p: Path) -> "Sprint":
        m = re.match(r"^(?:sprint-)?(\d+)-(.+)\.md$", p.name)
        if not m:
            fail(f"unrecognised sprint filename: {p.name}")
        sid = m.group(1).zfill(2)
        slug = m.group(2)
        text = p.read_text()
        tm = re.search(r"^#\s+(?:Sprint\s+\d+\s*[:\-]\s*)?(.+)$", text, re.M)
        title = tm.group(1).strip() if tm else slug
        bm = re.search(r"\*\*Band\*\*:\s*([^·\n]+)", text)
        band = bm.group(1).strip() if bm else None
        bbm = re.search(r"\*\*Blocked by\*\*:\s*([^·\n]+)", text)
        blocked: list[str] = []
        if bbm:
            raw = bbm.group(1).strip()
            if raw.lower() not in {"—", "nothing", "none", "-", ""}:
                blocked = [t for t in re.split(r"[,\s]+", raw) if t]
        return cls(id=sid, slug=slug, path=p.resolve(),
                   title=title, band=band, blocked_by=blocked)

    @property
    def branch(self) -> str:
        return f"sprint/{self.id}-{self.slug}"

    def specs_dir(self, cfg: "Config") -> Path:
        return cfg.path("specs_dir") / f"sprint-{self.id}-{self.slug}"

    def e2e_test_path(self, cfg: "Config") -> Path:
        slug_u = self.slug.replace("-", "_")
        return cfg.path("e2e_dir") / f"test_sprint_{self.id}_{slug_u}.md"


def parse_sprint_selector(sel: str) -> list[str]:
    sel = sel.strip()
    if "-" in sel and "," not in sel:
        a, b = sel.split("-", 1)
        return [f"{i:02d}" for i in range(int(a), int(b) + 1)]
    if "," in sel:
        return [tok.strip().zfill(2) for tok in sel.split(",") if tok.strip()]
    return [sel.zfill(2)]


def parse_resume_from(value: str) -> tuple[str, Optional[str], Optional[str]]:
    parts = value.split(":", 2)
    run_id = parts[0]
    sprint = parts[1].zfill(2) if len(parts) > 1 else None
    step = parts[2] if len(parts) > 2 else None
    if step and step not in STEP_ORDER:
        fail(f"unknown step in --resume-from: {step}")
    return run_id, sprint, step


def discover_sprints(cfg: Config, selector: Optional[str] = None) -> list[Sprint]:
    sprint_dir = cfg.path("sprint_dir")
    if not sprint_dir.exists():
        return []
    all_sprints: dict[str, Sprint] = {}
    for p in sorted(sprint_dir.glob("*.md")):
        if p.name.startswith("00-") or p.name.startswith("sprint-00-"):
            continue
        if not re.match(r"^(?:sprint-)?\d+-.+\.md$", p.name):
            continue  # skip non-sprint files (PRDs, READMEs, etc.)
        s = Sprint.from_path(p)
        all_sprints[s.id] = s
    if selector is None:
        return list(all_sprints.values())
    ids = parse_sprint_selector(selector)
    out: list[Sprint] = []
    for sid in ids:
        if sid not in all_sprints:
            fail(f"sprint {sid} not found under {sprint_dir}")
        out.append(all_sprints[sid])
    return out


def cmd_list_sprints(cfg: Config) -> int:
    sprints = discover_sprints(cfg)
    if not sprints:
        log(f"no sprints found under {cfg.path('sprint_dir')}")
        return 0
    for s in sprints:
        blocked = f" (blocked by {','.join(s.blocked_by)})" if s.blocked_by else ""
        band = f" [{s.band}]" if s.band else ""
        log(f"  {s.id}  {s.title}{band}{blocked}")
    return 0


# -------- Git helpers --------
def git(*args: str, cwd: Path, check: bool = True,
        capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd),
                          capture_output=capture, text=True, check=check)


def current_branch(cwd: Path) -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd).stdout.strip()


def head_sha(cwd: Path) -> str:
    return git("rev-parse", "HEAD", cwd=cwd).stdout.strip()


def working_tree_clean(cwd: Path, ignore: Optional[Path] = None) -> bool:
    # -uall expands nested untracked dirs so our ignore check is precise.
    out = git("status", "--porcelain", "-uall", cwd=cwd).stdout
    if not out.strip():
        return True
    if ignore is None:
        return False
    try:
        ig_rel = str(ignore.resolve().relative_to(cwd.resolve()))
    except ValueError:
        return False
    for line in out.splitlines():
        path = line[3:].strip().strip('"').rstrip("/")
        if path == ig_rel or path.startswith(ig_rel + "/"):
            continue
        return False
    return True


def branch_exists(name: str, cwd: Path) -> bool:
    return git("rev-parse", "--verify", "--quiet", name,
               cwd=cwd, check=False).returncode == 0


def ensure_main_clean(cwd: Path, ignore: Optional[Path] = None) -> None:
    if not working_tree_clean(cwd, ignore=ignore):
        fail("working tree not clean — commit or stash changes before continuing")


def checkout_or_create_branch(branch: str, cwd: Path) -> None:
    if current_branch(cwd) == branch:
        return
    if branch_exists(branch, cwd):
        git("checkout", branch, cwd=cwd)
        return
    git("checkout", "main", cwd=cwd)
    git("pull", "--ff-only", cwd=cwd, check=False)
    git("checkout", "-b", branch, cwd=cwd)


# -------- Step ordering + reset --------
STEP_ORDER = ["branch", "research", "plan", "build", "test",
              "e2e", "review", "document", "publish"]


class StepFailed(Exception):
    def __init__(self, step: str, message: str):
        super().__init__(f"{step}: {message}")
        self.step = step
        self.message = message


def _step_stage(name: str) -> str:
    if ":" in name:
        return name.split(":", 1)[0]
    if name.endswith("_patch"):
        return name[: -len("_patch")]
    return name


def reset_sprint_from(s: dict, step: str) -> None:
    idx = STEP_ORDER.index(step)
    to_clear = set(STEP_ORDER[idx:])
    s["steps"] = [st for st in s.get("steps", [])
                  if _step_stage(st.get("name", "")) not in to_clear]
    s["status"] = "pending"
    s["completed_at"] = None
    if "plan" in to_clear:
        s["specs"] = []
        s["e2e_test_path"] = None
    if "build" in to_clear:
        for sp in s.get("specs", []):
            sp["build"] = {"status": "pending"}
            sp["commit"] = {"status": "pending"}
    if "test" in to_clear:
        s["tests"] = None
    if "e2e" in to_clear:
        s["e2e"] = None
    if "review" in to_clear:
        s["review"] = None
    if "document" in to_clear:
        for sp in s.get("specs", []):
            sp["documentation"] = None
        s["documentation"] = []
    if "publish" in to_clear:
        s["pr"] = None


# -------- Output parsing + snapshot helpers --------
def extract_marker_lines(text: str, marker: str) -> list[str]:
    """Return every value of lines shaped 'MARKER: <value>' (strips backticks)."""
    out: list[str] = []
    pat = re.compile(rf"^\s*{re.escape(marker)}:\s*(.+?)\s*$", re.M)
    for m in pat.finditer(text):
        v = m.group(1).strip().strip("`")
        if v:
            out.append(v)
    return out


def read_json_file(p: Path) -> Optional[dict]:
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def snapshot(dirs: list[Path], pattern: str = "**/*.md") -> set[Path]:
    out: set[Path] = set()
    for d in dirs:
        if d.exists():
            for p in d.glob(pattern):
                out.add(p.resolve())
    return out


def newly_created(before: set[Path], dirs: list[Path],
                  pattern: str = "**/*.md") -> list[Path]:
    after = snapshot(dirs, pattern)
    return sorted(after - before)


def _spec_title(p: Path) -> str:
    try:
        text = p.read_text()
    except OSError:
        return p.stem
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else p.stem


# -------- SprintExecutor (expanded across Tasks 10-19) --------
class SprintExecutor:
    def __init__(self, sprint: Sprint, cfg: Config, state: State,
                 run_log_dir: Path, dry_run: bool = False,
                 force_step: Optional[str] = None):
        self.sprint = sprint
        self.cfg = cfg
        self.state = state
        self.run_log_dir = run_log_dir
        self.log_dir = run_log_dir / sprint.id
        self.dry_run = dry_run
        self.force_step = force_step
        self.kiro = KiroRunner(self.log_dir, cfg.root, dry_run)
        sprint_rel = str(sprint.path)
        try:
            sprint_rel = str(sprint.path.relative_to(cfg.root))
        except ValueError:
            pass
        self.s = state.init_sprint(sprint.id, {
            "sprint_id": sprint.id, "slug": sprint.slug, "title": sprint.title,
            "sprint_file": sprint_rel, "branch": sprint.branch,
            "status": "pending",
            "started_at": None, "completed_at": None, "duration_seconds": 0.0,
            "step_executions": {}, "steps": [], "specs": [],
            "research_doc": None, "e2e_test_path": None,
            "tests": None, "e2e": None, "review": None,
            "documentation": [], "pr": None, "errors": [],
        })

    def _begin_step(self, name: str) -> dict:
        log(f"▶ {name}")
        for rec in self.s["steps"]:
            if rec["name"] == name and rec.get("status") != "completed":
                rec["status"] = "in_progress"
                rec["attempts"] = rec.get("attempts", 0) + 1
                self.s["step_executions"][name] = self.s["step_executions"].get(name, 0) + 1
                self._t0 = time.monotonic()
                self.state.save()
                return rec
        rec = {
            "name": name, "status": "in_progress",
            "started_at": now_iso(), "completed_at": None,
            "duration_seconds": 0.0, "attempts": 1,
            "exit_code": None, "prompt_path": None, "log_path": None,
            "result_path": None, "prompt_bytes": 0, "stdout_bytes": 0,
            "transient_retries": 0, "credits": None,
            "kiro_reported_seconds": None, "error": None,
        }
        self.s["steps"].append(rec)
        self.s["step_executions"][name] = self.s["step_executions"].get(name, 0) + 1
        self._t0 = time.monotonic()
        self.state.save()
        return rec

    def _end_step(self, rec: dict, success: bool, error: Optional[str] = None,
                  cr: Optional[KiroResult] = None,
                  result_path: Optional[Path] = None) -> None:
        rec["status"] = "completed" if success else "failed"
        rec["completed_at"] = now_iso()
        rec["duration_seconds"] = round(time.monotonic() - self._t0, 3)
        if cr is not None:
            rec["exit_code"] = cr.exit_code
            rec["prompt_path"] = str(cr.prompt_path)
            rec["log_path"] = str(cr.log_path)
            rec["prompt_bytes"] = cr.prompt_bytes
            rec["stdout_bytes"] = cr.stdout_bytes
            rec["transient_retries"] = cr.transient_retries
            rec["credits"] = cr.credits
            rec["kiro_reported_seconds"] = cr.kiro_reported_seconds
        if result_path is not None:
            rec["result_path"] = str(result_path)
        if error:
            rec["error"] = error
        self._rollup_totals()
        self.state.save()

    def _empty_stage(self) -> dict:
        return {"duration_seconds": 0.0, "attempts": 0,
                "stdout_bytes": 0, "credits": None, "patch_cycles": 0}

    def _rollup_totals(self) -> None:
        """Recompute sprint.totals + run.totals from steps[]."""
        stages = ["research", "plan", "build", "test", "e2e",
                  "review", "document", "publish", "branch", "commit"]
        sprint_totals = {
            "duration_seconds": 0.0, "stdout_bytes": 0,
            "credits": None,
            "by_stage": {s: self._empty_stage() for s in stages},
        }
        for st in self.s.get("steps", []):
            stage = _step_stage(st.get("name", ""))
            if stage not in sprint_totals["by_stage"]:
                sprint_totals["by_stage"][stage] = self._empty_stage()
            bs = sprint_totals["by_stage"][stage]
            dur = float(st.get("duration_seconds") or 0)
            att = int(st.get("attempts") or 0)
            sob = int(st.get("stdout_bytes") or 0)
            cred = st.get("credits")
            bs["duration_seconds"] = round(bs["duration_seconds"] + dur, 3)
            bs["attempts"] += att
            bs["stdout_bytes"] += sob
            if cred is not None:
                bs["credits"] = round((bs["credits"] or 0.0) + cred, 4)
            sprint_totals["duration_seconds"] = round(
                sprint_totals["duration_seconds"] + dur, 3)
            sprint_totals["stdout_bytes"] += sob
            if cred is not None:
                sprint_totals["credits"] = round(
                    (sprint_totals["credits"] or 0.0) + cred, 4)
        # patch_cycles pulled from result dicts for test/e2e/review
        for k in ("test", "e2e", "review"):
            bucket = self.s.get("tests" if k == "test" else k) or {}
            if isinstance(bucket, dict):
                sprint_totals["by_stage"].setdefault(k, self._empty_stage())
                sprint_totals["by_stage"][k]["patch_cycles"] = int(
                    bucket.get("patch_cycles", 0))
        self.s["totals"] = sprint_totals
        # Run-level rollup: sum across all sprints
        run_totals = {
            "duration_seconds": 0.0, "stdout_bytes": 0,
            "credits": None,
            "by_stage": {s: self._empty_stage() for s in stages},
        }
        for sp in self.state.data.get("sprints", []):
            st_t = sp.get("totals") or {}
            run_totals["duration_seconds"] = round(
                run_totals["duration_seconds"] + float(st_t.get("duration_seconds", 0)), 3)
            run_totals["stdout_bytes"] += int(st_t.get("stdout_bytes", 0))
            if st_t.get("credits") is not None:
                run_totals["credits"] = round(
                    (run_totals["credits"] or 0.0) + float(st_t["credits"]), 4)
            for stage, vals in (st_t.get("by_stage") or {}).items():
                tgt = run_totals["by_stage"].setdefault(stage, self._empty_stage())
                tgt["duration_seconds"] = round(
                    tgt["duration_seconds"] + float(vals.get("duration_seconds", 0)), 3)
                tgt["attempts"] += int(vals.get("attempts", 0))
                tgt["stdout_bytes"] += int(vals.get("stdout_bytes", 0))
                if vals.get("credits") is not None:
                    tgt["credits"] = round(
                        (tgt["credits"] or 0.0) + float(vals["credits"]), 4)
                tgt["patch_cycles"] += int(vals.get("patch_cycles", 0))
        self.state.data["totals"] = run_totals

    def _step_completed(self, name: str) -> bool:
        if self.force_step == name:
            return False
        for rec in self.s["steps"]:
            if rec["name"] == name and rec.get("status") == "completed":
                return True
        return False

    def _timeout(self, step: str, default: int = 1800) -> int:
        tt = (self.cfg.data.get("timeouts") or {})
        return int(tt.get(step, default))

    def _rel(self, p: Path) -> str:
        try:
            return str(Path(p).resolve().relative_to(self.cfg.root.resolve()))
        except ValueError:
            return str(p)

    # --- Step 0: branch ---
    def step_branch(self) -> None:
        if self._step_completed("branch"):
            return
        rec = self._begin_step("branch")
        if self.dry_run:
            self._end_step(rec, True)
            return
        try:
            if current_branch(self.cfg.root) == self.sprint.branch:
                self._end_step(rec, True)
                return
            ensure_main_clean(self.cfg.root, ignore=self.run_log_dir)
            checkout_or_create_branch(self.sprint.branch, self.cfg.root)
            self._end_step(rec, True)
        except subprocess.CalledProcessError as e:
            msg = f"git: {(e.stderr or '').strip() or e}"
            self.s["errors"].append({"step": "branch", "error": msg})
            self._end_step(rec, False, error=msg)
            raise StepFailed("branch", msg)

    # --- Step 1: research ---
    def step_research(self) -> None:
        if self._step_completed("research") and self.s.get("research_doc"):
            return
        rec = self._begin_step("research")
        research_dir = self.cfg.path("research_dir")
        research_dir.mkdir(parents=True, exist_ok=True)
        if self.dry_run:
            doc = research_dir / f"dry-run-sprint-{self.sprint.id}.md"
            doc.write_text("# dry-run research\n")
            self.s["research_doc"] = self._rel(doc)
            self._end_step(rec, True)
            log(f"  ✓ research (dry-run) → {self.s['research_doc']}")
            return
        before = snapshot([research_dir])
        prompt = render_prompt(self.cfg, "research-codebase", {
            "ARGUMENTS": str(self.sprint.path),
            "sprint_path": str(self.sprint.path),
            "run_id": self.state.data.get("run_id", ""),
            "research_dir": self._rel(research_dir),
        }) + (
            "\n\n---\nRUNNER NOTE:\n"
            f"Research target: sprint {self.sprint.id} — {self.sprint.title}\n"
            f"Sprint planning doc (read FULLY before spawning sub-agents):\n"
            f"  {self.sprint.path}\n"
            f"Write the research document under: {self._rel(research_dir)}/\n"
            "On the FINAL line of your final message, emit:\n"
            "  RESEARCH_PATH: <absolute path to the research doc you created>\n"
        )
        agent = self.cfg.agents.get("plan", "pipeline-plan")
        cr = self.kiro.run("research", prompt, agent, self._timeout("research"))
        if not cr.succeeded:
            msg = cr.error or f"exit={cr.exit_code}"
            self.s["errors"].append({"step": "research", "error": msg})
            self._end_step(rec, False, error=msg, cr=cr)
            raise StepFailed("research", msg)
        # Prefer explicit marker; fall back to diffing snapshots.
        markers = extract_marker_lines(cr.stdout, "RESEARCH_PATH")
        doc_path: Optional[Path] = None
        if markers:
            cand = Path(markers[-1])
            if cand.exists():
                doc_path = cand
        if doc_path is None:
            created = newly_created(before, [research_dir])
            if created:
                doc_path = created[0]
        if doc_path is None:
            msg = "no research document produced (no RESEARCH_PATH marker, no new file)"
            self.s["errors"].append({"step": "research", "error": msg})
            self._end_step(rec, False, error=msg, cr=cr)
            raise StepFailed("research", msg)
        self.s["research_doc"] = self._rel(doc_path)
        self._end_step(rec, True, cr=cr)
        log(f"  ✓ research → {self.s['research_doc']}")

    # --- Step 2: plan ---
    def step_plan(self) -> None:
        if self._step_completed("plan") and self.s.get("specs"):
            return
        rec = self._begin_step("plan")
        specs_dir = self.sprint.specs_dir(self.cfg)
        e2e_dir = self.cfg.path("e2e_dir")
        specs_dir.mkdir(parents=True, exist_ok=True)
        e2e_dir.mkdir(parents=True, exist_ok=True)
        if self.dry_run:
            sp1 = specs_dir / "spec-01-dry-run.md"
            sp1.write_text("# Dry-run spec\n")
            e2e = e2e_dir / f"test_sprint_{self.sprint.id}_{self.sprint.slug.replace('-','_')}.md"
            e2e.write_text("# Dry-run e2e\n")
            self.s["specs"] = [{
                "id": f"sprint-{self.sprint.id}-01",
                "path": self._rel(sp1), "title": "Dry-run spec",
                "build":  {"status": "pending"},
                "commit": {"status": "pending"},
                "documentation": None,
            }]
            self.s["e2e_test_path"] = self._rel(e2e)
            self._end_step(rec, True)
            log(f"  ✓ plan (dry-run) → 1 spec")
            return
        before_specs = snapshot([specs_dir])
        before_e2e = snapshot([e2e_dir])
        research_path = self.cfg.root / (self.s.get("research_doc") or "")
        run_id = self.state.data.get("run_id", "")
        stack = self.cfg.stack
        issue_id = f"sprint-{self.sprint.id}"
        issue_json = json.dumps({
            "id": issue_id, "title": self.sprint.title,
            "sprint_file": str(self.sprint.path),
            "research": str(research_path),
        })
        prompt = render_prompt(self.cfg, "plan-feature", {
            "1": issue_id, "2": issue_json,
            "ARGUMENTS": str(self.sprint.path),
            "issue_id": issue_id, "run_id": run_id, "issue_json": issue_json,
        }) + (
            "\n\n---\nRUNNER NOTE — mandatory output contract:\n"
            f"1. Write spec files under `{self._rel(specs_dir)}/spec-NN-<kebab>.md`.\n"
            f"2. Write exactly ONE sprint-level E2E test at\n"
            f"   `{self._rel(e2e_dir)}/test_sprint_{self.sprint.id}_{self.sprint.slug.replace('-','_')}.md`.\n"
            f"3. Command ownership — split validation into two buckets:\n"
            f"   PHASE-OWNED (safe to gate a Phase's Success Criteria on):\n"
            f"     lint: {stack.get('lint','')}\n"
            f"     typecheck: {stack.get('typecheck','')}\n"
            f"     build: {stack.get('build','')}\n"
            f"     test: {stack.get('test','')}\n"
            f"   RUNNER-OWNED (sprint-level; the runner executes these in a\n"
            f"   dedicated stage with its own patch-and-retry loop — do NOT\n"
            f"   list them as per-phase Success Criteria, only in the\n"
            f"   sprint-level Validation Commands section, marked runner-owned):\n"
            f"     e2e: {stack.get('e2e','')}\n"
            "4. On the FINAL lines of your final message, emit one line per spec\n"
            "   and one final E2E_PATH line:\n"
            "     SPEC_PATH: <absolute path>\n"
            "     ...\n"
            "     E2E_PATH: <absolute path>\n"
        )
        agent = self.cfg.agents.get("plan", "pipeline-plan")
        cr = self.kiro.run("plan", prompt, agent, self._timeout("plan"))
        if not cr.succeeded:
            msg = cr.error or f"exit={cr.exit_code}"
            self.s["errors"].append({"step": "plan", "error": msg})
            self._end_step(rec, False, error=msg, cr=cr)
            raise StepFailed("plan", msg)
        # Parse SPEC_PATH markers (preferred)
        spec_paths: list[Path] = []
        for m in extract_marker_lines(cr.stdout, "SPEC_PATH"):
            p = Path(m)
            if p.exists():
                spec_paths.append(p.resolve())
        if not spec_paths:
            spec_paths = newly_created(before_specs, [specs_dir])
        # Parse E2E_PATH (single)
        e2e_markers = extract_marker_lines(cr.stdout, "E2E_PATH")
        e2e_path: Optional[Path] = None
        if e2e_markers:
            cand = Path(e2e_markers[-1])
            if cand.exists():
                e2e_path = cand.resolve()
        if e2e_path is None:
            new_e2e = newly_created(before_e2e, [e2e_dir])
            e2e_path = new_e2e[0] if new_e2e else None
        if not spec_paths:
            msg = "no specs produced (no SPEC_PATH markers, no new files)"
            self.s["errors"].append({"step": "plan", "error": msg})
            self._end_step(rec, False, error=msg, cr=cr)
            raise StepFailed("plan", msg)
        # Seed state.specs
        self.s["specs"] = []
        for i, sp in enumerate(sorted(spec_paths), start=1):
            self.s["specs"].append({
                "id": f"sprint-{self.sprint.id}-{i:02d}",
                "path": self._rel(sp),
                "title": _spec_title(sp),
                "build":  {"status": "pending"},
                "commit": {"status": "pending"},
                "documentation": None,
            })
        self.s["e2e_test_path"] = self._rel(e2e_path) if e2e_path else None
        self._end_step(rec, True, cr=cr)
        log(f"  ✓ plan → {len(self.s['specs'])} specs, "
            f"e2e={self.s['e2e_test_path']}")

    # --- Step 3: build (per spec, implement + commit) ---
    def step_build(self) -> None:
        for i, spec in enumerate(self.s["specs"]):
            self._build_one(i, spec)

    def _build_one(self, i: int, spec: dict) -> None:
        b, c = spec.get("build", {}), spec.get("commit", {})
        if (b.get("status") == "completed"
                and c.get("status") == "completed"
                and self.force_step != "build"):
            log(f"  ✓ build[{spec['id']}] cached")
            return
        if self.dry_run:
            rec = self._begin_step(f"build:{spec['id']}")
            b.update({"status":"completed","summary":"(dry-run)",
                      "started_at":now_iso(),"completed_at":now_iso(),
                      "duration_seconds":0.0,"credits":None})
            self._end_step(rec, True)
            rec2 = self._begin_step(f"commit:{spec['id']}")
            c.update({"status":"completed","sha":"drydrydry",
                      "message":"(dry-run)"})
            self._end_step(rec2, True)
            return
        agent = self.cfg.agents.get("execute", "pipeline-execute")
        step_name = f"build:{spec['id']}"
        spec_abs = self.cfg.root / spec["path"]

        # Implement phase
        if b.get("status") != "completed" or self.force_step == "build":
            rec = self._begin_step(step_name)
            b["status"] = "in_progress"
            b["started_at"] = now_iso()
            self.state.save()
            prompt = render_prompt(self.cfg, "implement", {
                "ARGUMENTS": str(spec_abs),
                "1": str(spec_abs),
                "run_id": self.state.data.get("run_id", ""),
            }) + (
                "\n\n---\nRUNNER NOTE: Do NOT touch git; do NOT commit. On the\n"
                "FINAL line of your final message, emit ONE line:\n"
                "  BUILD_SUMMARY: <one-sentence description of what you implemented>\n"
            )
            cr = self.kiro.run(step_name, prompt, agent, self._timeout("build"))
            b["status"] = "completed" if cr.succeeded else "failed"
            b["completed_at"] = now_iso()
            b["duration_seconds"] = cr.duration_seconds
            b["credits"] = cr.credits
            b["log_path"] = str(cr.log_path)
            markers = extract_marker_lines(cr.stdout, "BUILD_SUMMARY")
            if markers:
                b["summary"] = markers[-1][:300]
            else:
                last = [ln for ln in cr.stdout.splitlines() if ln.strip()]
                b["summary"] = (last[-1][:200] if last else "(no summary)")
            if not cr.succeeded:
                err = cr.error or f"exit={cr.exit_code}"
                b["error"] = err
                self._end_step(rec, False, error=err, cr=cr)
                raise StepFailed("build", f"{spec['id']}: {err}")
            self._end_step(rec, True, cr=cr)

        # Commit phase
        if c.get("status") == "completed" and self.force_step != "build":
            return
        commit_step = f"commit:{spec['id']}"
        if working_tree_clean(self.cfg.root, ignore=self.run_log_dir):
            c["status"] = "completed"
            c["sha"] = head_sha(self.cfg.root)
            c["message"] = "(no changes)"
            self.state.save()
            log(f"  ✓ build[{spec['id']}] produced no diff — skipping commit")
            return
        head_before = head_sha(self.cfg.root)
        status_out = git("status", "--porcelain", cwd=self.cfg.root).stdout
        diff_stat = git("diff", "--stat", "HEAD", cwd=self.cfg.root).stdout
        rec = self._begin_step(commit_step)
        prompt = render_prompt(self.cfg, "commit", {
            "ARGUMENTS": f"pipeline feat {spec['id']}",
            "run_id": self.state.data.get("run_id", ""),
        }) + (
            "\n\n---\nCONTEXT\n"
            f"Spec: {spec['id']}  path={spec['path']}\n"
            f"Build summary: {b.get('summary','')}\n\n"
            f"git status --porcelain:\n{status_out}\n"
            f"git diff --stat HEAD:\n{diff_stat}\n"
            "After committing, push to origin.\n"
        )
        cr = self.kiro.run(commit_step, prompt, agent, self._timeout("commit"))
        new_sha = head_sha(self.cfg.root)
        if cr.succeeded and new_sha != head_before:
            c["status"] = "completed"
            c["sha"] = new_sha
            c["message"] = git("log", "-1", "--format=%s", new_sha,
                                cwd=self.cfg.root).stdout.strip()
            c["log_path"] = str(cr.log_path)
            self._end_step(rec, True, cr=cr)
            log(f"  ✓ commit[{spec['id']}] {new_sha[:8]} {c['message']}")
        else:
            err = cr.error or f"no commit produced (exit={cr.exit_code})"
            c["status"] = "failed"
            c["error"] = err
            c["log_path"] = str(cr.log_path)
            self._end_step(rec, False, error=err, cr=cr)
            raise StepFailed("build", f"{spec['id']}: commit failed — {err}")

    # --- Step 4: test (self-healing patch loop) ---
    def step_test(self) -> None:
        if self._step_completed("test"):
            return
        if self.dry_run:
            rec = self._begin_step("test")
            self.s["tests"] = {"build_succeeded":True,"tests_passed":True,
                               "summary":"(dry-run)","patch_cycles":0}
            self._end_step(rec, True)
            return
        max_cycles = int(self.cfg.data.get("test_patch_max", 4))
        agent = self.cfg.agents.get("browser", "pipeline-execute-browser")
        run_id = self.state.data.get("run_id", "")
        for cycle in range(1, max_cycles + 1):
            rec = self._begin_step("test")
            result_path = self.log_dir / f"test-result-attempt-{cycle}.json"
            prompt = render_prompt(self.cfg, "test", {
                "ARGUMENTS": str(result_path), "run_id": run_id,
                "cycle": str(cycle),
            }) + (
                "\n\n---\nRUNNER NOTE:\n"
                f"Write the final JSON result to: {result_path}\n"
                'Schema: {"build_succeeded":bool,"tests_passed":bool,'
                '"tests_executed":int,"errors_count":int,"warnings_count":int,'
                '"errors":[{"file":"...","line":int,"message":"..."}],'
                '"summary":"..."}\n'
                "Do NOT modify source files.\n"
            )
            cr = self.kiro.run("test", prompt, agent,
                               self._timeout("test"),
                               require_mcp_startup=True)
            result = read_json_file(result_path) or {}
            passed = bool(result.get("build_succeeded") and result.get("tests_passed") and cr.succeeded)
            self.s["tests"] = dict(result, patch_cycles=cycle - 1)
            if passed:
                self._end_step(rec, True, cr=cr, result_path=result_path)
                log(f"  ✓ test passed (cycle {cycle})")
                return
            if cycle >= max_cycles:
                err = "exhausted test patch cycles"
                self.s["errors"].append({"step": "test", "error": err})
                self._end_step(rec, False, error=err, cr=cr, result_path=result_path)
                raise StepFailed("test", err)
            self._end_step(rec, False,
                           error=result.get("summary", "test failed"),
                           cr=cr, result_path=result_path)
            self._test_patch(cycle, result)

    def _test_patch(self, cycle: int, result: dict) -> None:
        patch_dir = self.cfg.path("patch_specs_dir")
        patch_dir.mkdir(parents=True, exist_ok=True)
        patch_name = f"patch-sprint-{self.sprint.id}-test-{cycle}.md"
        patch_path = patch_dir / patch_name
        run_id = self.state.data.get("run_id", "")
        prior_ctx = ""
        if cycle >= 2:
            prior = patch_dir / f"patch-sprint-{self.sprint.id}-test-{cycle-1}.md"
            if prior.exists():
                prior_ctx = (
                    "\n\nPRIOR CYCLE CONTEXT — last cycle's patch is below. Propose a\n"
                    "DIFFERENT root cause, touch DIFFERENT files, apply a DIFFERENT fix.\n\n"
                    f"```md\n{prior.read_text()[:4000]}\n```\n"
                )
        rec = self._begin_step("test_patch")
        # Phase A: write the patch plan
        plan_prompt = render_prompt(self.cfg, "patch", {
            "1": json.dumps(result), "2": str(patch_path),
            "ARGUMENTS": f"sprint-{self.sprint.id}-test-{cycle}",
            "run_id": run_id,
        }) + (
            f"\n\n---\nRUNNER NOTE: Write the patch plan to:\n  {patch_path}\n"
            "Scope rules: modify application code (src/, tests/, configs).\n"
            "Do NOT modify files under specs/.\n" + prior_ctx
        )
        plan_agent = self.cfg.agents.get("plan", "pipeline-plan")
        exec_agent = self.cfg.agents.get("execute", "pipeline-execute")
        cr1 = self.kiro.run(f"test_patch_plan-cycle-{cycle}", plan_prompt,
                            plan_agent, self._timeout("test"))
        if not cr1.succeeded or not patch_path.exists():
            err = cr1.error or "patch plan not produced"
            self._end_step(rec, False, error=err, cr=cr1)
            raise StepFailed("test_patch", err)
        # Phase B: implement the patch
        impl_prompt = render_prompt(self.cfg, "implement", {
            "ARGUMENTS": str(patch_path), "1": str(patch_path),
            "run_id": run_id,
        }) + "\n\n---\nRUNNER NOTE: Do NOT touch git; do NOT commit.\n"
        cr2 = self.kiro.run(f"test_patch-cycle-{cycle}", impl_prompt,
                            exec_agent, self._timeout("build"))
        if not cr2.succeeded:
            err = cr2.error or f"patch implement exit={cr2.exit_code}"
            self._end_step(rec, False, error=err, cr=cr2)
            raise StepFailed("test_patch", err)
        # Phase C: local commit if dirty
        if not working_tree_clean(self.cfg.root, ignore=self.run_log_dir):
            commit_prompt = render_prompt(self.cfg, "commit", {
                "ARGUMENTS": f"pipeline chore test patch cycle {cycle} for sprint {self.sprint.id}",
                "run_id": run_id,
            }) + "\n\n---\nRUNNER NOTE: Local commit only — do NOT push.\n"
            self.kiro.run(f"test_patch_commit-cycle-{cycle}",
                          commit_prompt, exec_agent, self._timeout("commit"))
        self._end_step(rec, True, cr=cr2)

    # --- Step 5: e2e (self-healing patch loop) ---
    def step_e2e(self) -> None:
        if self._step_completed("e2e"):
            return
        e2e_path = self.s.get("e2e_test_path")
        if self.dry_run:
            rec = self._begin_step("e2e")
            self.s["e2e"] = {"passed":True,"summary":"(dry-run)","patch_cycles":0} \
                if e2e_path else {"skipped":True,"reason":"dry-run no e2e"}
            self._end_step(rec, True)
            return
        if not e2e_path:
            rec = self._begin_step("e2e")
            self.s["e2e"] = {"skipped": True, "reason": "no sprint-level E2E test produced"}
            self._end_step(rec, True)
            log("  ⤼ e2e skipped (no test path)")
            return
        max_cycles = int(self.cfg.data.get("e2e_patch_max", 3))
        agent = self.cfg.agents.get("browser", "pipeline-execute-browser")
        run_id = self.state.data.get("run_id", "")
        e2e_abs = self.cfg.root / e2e_path
        for cycle in range(1, max_cycles + 1):
            rec = self._begin_step("e2e")
            result_path = self.log_dir / f"e2e-result-attempt-{cycle}.json"
            prompt = render_prompt(self.cfg, "test_e2e", {
                "ARGUMENTS": str(e2e_abs),
                "run_id": run_id, "cycle": str(cycle),
            }) + (
                "\n\n---\nRUNNER NOTE:\n"
                f"E2E test file: {e2e_abs}\n"
                f"Write the final JSON result to: {result_path}\n"
                'Schema: {"passed":bool,'
                '"failed_steps":[{"step":"...","error":"...","screenshot":null|"..."}],'
                '"screenshots":["..."],"summary":"..."}\n'
            )
            cr = self.kiro.run("e2e", prompt, agent,
                               self._timeout("e2e"),
                               require_mcp_startup=True)
            result = read_json_file(result_path) or {}
            passed = bool(result.get("passed") and cr.succeeded)
            self.s["e2e"] = dict(result, patch_cycles=cycle - 1)
            if passed:
                self._end_step(rec, True, cr=cr, result_path=result_path)
                log(f"  ✓ e2e passed (cycle {cycle})")
                return
            if cycle >= max_cycles:
                err = "exhausted e2e patch cycles"
                self.s["errors"].append({"step": "e2e", "error": err})
                self._end_step(rec, False, error=err, cr=cr, result_path=result_path)
                raise StepFailed("e2e", err)
            self._end_step(rec, False,
                           error=result.get("summary", "e2e failed"),
                           cr=cr, result_path=result_path)
            self._e2e_patch(cycle, result)

    def _e2e_patch(self, cycle: int, result: dict) -> None:
        patch_dir = self.cfg.path("patch_specs_dir")
        patch_dir.mkdir(parents=True, exist_ok=True)
        patch_path = patch_dir / f"patch-sprint-{self.sprint.id}-e2e-{cycle}.md"
        run_id = self.state.data.get("run_id", "")
        prior_ctx = ""
        if cycle >= 2:
            prior = patch_dir / f"patch-sprint-{self.sprint.id}-e2e-{cycle-1}.md"
            if prior.exists():
                prior_ctx = (
                    "\n\nPRIOR CYCLE CONTEXT — different root cause required:\n"
                    f"```md\n{prior.read_text()[:4000]}\n```\n"
                )
        rec = self._begin_step("e2e_patch")
        plan_prompt = render_prompt(self.cfg, "patch", {
            "1": json.dumps({"failed_steps": result.get("failed_steps", [])}),
            "2": str(patch_path),
            "ARGUMENTS": f"sprint-{self.sprint.id}-e2e-{cycle}",
            "run_id": run_id,
        }) + (
            f"\n\n---\nRUNNER NOTE: Write the patch plan to:\n  {patch_path}\n"
            "Scope: application code only, not specs/ files.\n" + prior_ctx
        )
        plan_agent = self.cfg.agents.get("plan", "pipeline-plan")
        exec_agent = self.cfg.agents.get("execute", "pipeline-execute")
        cr1 = self.kiro.run(f"e2e_patch_plan-cycle-{cycle}", plan_prompt,
                            plan_agent, self._timeout("e2e"))
        if not cr1.succeeded or not patch_path.exists():
            err = cr1.error or "patch plan not produced"
            self._end_step(rec, False, error=err, cr=cr1)
            raise StepFailed("e2e_patch", err)
        impl_prompt = render_prompt(self.cfg, "implement", {
            "ARGUMENTS": str(patch_path), "1": str(patch_path),
            "run_id": run_id,
        }) + "\n\n---\nRUNNER NOTE: Do NOT touch git; do NOT commit.\n"
        cr2 = self.kiro.run(f"e2e_patch-cycle-{cycle}", impl_prompt,
                            exec_agent, self._timeout("build"))
        if not cr2.succeeded:
            err = cr2.error or f"patch implement exit={cr2.exit_code}"
            self._end_step(rec, False, error=err, cr=cr2)
            raise StepFailed("e2e_patch", err)
        if not working_tree_clean(self.cfg.root, ignore=self.run_log_dir):
            commit_prompt = render_prompt(self.cfg, "commit", {
                "ARGUMENTS": f"pipeline chore e2e patch cycle {cycle} for sprint {self.sprint.id}",
                "run_id": run_id,
            }) + "\n\n---\nRUNNER NOTE: Local commit only.\n"
            self.kiro.run(f"e2e_patch_commit-cycle-{cycle}",
                          commit_prompt, exec_agent, self._timeout("commit"))
        self._end_step(rec, True, cr=cr2)

    # --- Step 6: review (self-healing patch loop) ---
    def step_review(self) -> None:
        if self._step_completed("review"):
            return
        if self.dry_run:
            rec = self._begin_step("review")
            self.s["review"] = {"success":True,"review_summary":"(dry-run)",
                                "review_issues":[],"patch_cycles":0,"blockers":0}
            self._end_step(rec, True)
            return
        max_cycles = int(self.cfg.data.get("review_patch_max", 4))
        agent = self.cfg.agents.get("browser", "pipeline-execute-browser")
        run_id = self.state.data.get("run_id", "")
        spec_paths = [str(self.cfg.root / s["path"]) for s in self.s.get("specs", [])]
        for cycle in range(1, max_cycles + 1):
            rec = self._begin_step("review")
            result_path = self.log_dir / f"review-result-attempt-{cycle}.json"
            prompt = render_prompt(self.cfg, "review", {
                "1": "\n".join(spec_paths), "2": "review_agent",
                "ARGUMENTS": "\n".join(spec_paths),
                "run_id": run_id, "cycle": str(cycle),
            }) + (
                "\n\n---\nRUNNER NOTE: Review the CURRENT sprint implementation\n"
                "against ALL specs listed above. Treat the whole sprint as one\n"
                f"unit of review. Write the final JSON result to: {result_path}\n"
                'Schema: {"success":bool, "review_summary":"...",\n'
                '  "review_issues":[{"review_issue_id":int,"issue_severity":"blocker|major|minor",\n'
                '     "file":"...","description":"..."}], "screenshots":["..."]}\n'
            )
            cr = self.kiro.run("review", prompt, agent,
                               self._timeout("review"),
                               require_mcp_startup=True)
            result = read_json_file(result_path) or {}
            blockers = [i for i in result.get("review_issues", [])
                        if (i.get("issue_severity") or "").lower() == "blocker"]
            success = bool(result.get("success") and not blockers and cr.succeeded)
            self.s["review"] = dict(result, patch_cycles=cycle - 1,
                                     blockers=len(blockers))
            if success:
                self._end_step(rec, True, cr=cr, result_path=result_path)
                log(f"  ✓ review passed (cycle {cycle})")
                return
            if cycle >= max_cycles:
                err = "exhausted review patch cycles"
                self.s["errors"].append({"step": "review", "error": err})
                self._end_step(rec, False, error=err, cr=cr, result_path=result_path)
                raise StepFailed("review", err)
            self._end_step(rec, False,
                           error=result.get("review_summary", "review failed"),
                           cr=cr, result_path=result_path)
            self._review_patch(cycle, blockers)

    def _review_patch(self, cycle: int, blockers: list) -> None:
        patch_dir = self.cfg.path("patch_specs_dir")
        patch_dir.mkdir(parents=True, exist_ok=True)
        patch_path = patch_dir / f"patch-sprint-{self.sprint.id}-review-{cycle}.md"
        run_id = self.state.data.get("run_id", "")
        prior_ctx = ""
        if cycle >= 2:
            prior = patch_dir / f"patch-sprint-{self.sprint.id}-review-{cycle-1}.md"
            if prior.exists():
                prior_ctx = (
                    "\n\nPRIOR CYCLE CONTEXT — different root cause required:\n"
                    f"```md\n{prior.read_text()[:4000]}\n```\n"
                )
        rec = self._begin_step("review_patch")
        plan_prompt = render_prompt(self.cfg, "patch", {
            "1": json.dumps({"blockers": blockers}),
            "2": str(patch_path),
            "ARGUMENTS": f"sprint-{self.sprint.id}-review-{cycle}",
            "run_id": run_id,
        }) + (
            f"\n\n---\nRUNNER NOTE: Write the patch plan to:\n  {patch_path}\n"
            "Scope: application code only, not specs/ files.\n" + prior_ctx
        )
        plan_agent = self.cfg.agents.get("plan", "pipeline-plan")
        exec_agent = self.cfg.agents.get("execute", "pipeline-execute")
        cr1 = self.kiro.run(f"review_patch_plan-cycle-{cycle}", plan_prompt,
                            plan_agent, self._timeout("review"))
        if not cr1.succeeded or not patch_path.exists():
            err = cr1.error or "patch plan not produced"
            self._end_step(rec, False, error=err, cr=cr1)
            raise StepFailed("review_patch", err)
        impl_prompt = render_prompt(self.cfg, "implement", {
            "ARGUMENTS": str(patch_path), "1": str(patch_path),
            "run_id": run_id,
        }) + "\n\n---\nRUNNER NOTE: Do NOT touch git; do NOT commit.\n"
        cr2 = self.kiro.run(f"review_patch-cycle-{cycle}", impl_prompt,
                            exec_agent, self._timeout("build"))
        if not cr2.succeeded:
            err = cr2.error or f"patch implement exit={cr2.exit_code}"
            self._end_step(rec, False, error=err, cr=cr2)
            raise StepFailed("review_patch", err)
        if not working_tree_clean(self.cfg.root, ignore=self.run_log_dir):
            commit_prompt = render_prompt(self.cfg, "commit", {
                "ARGUMENTS": f"pipeline chore review patch cycle {cycle} for sprint {self.sprint.id}",
                "run_id": run_id,
            }) + "\n\n---\nRUNNER NOTE: Local commit only.\n"
            self.kiro.run(f"review_patch_commit-cycle-{cycle}",
                          commit_prompt, exec_agent, self._timeout("commit"))
        self._end_step(rec, True, cr=cr2)

    # --- Step 7: document (per spec + single docs commit) ---
    def step_document(self) -> None:
        if self._step_completed("document"):
            return
        if self.dry_run:
            for spec in self.s.get("specs", []):
                if not spec.get("documentation"):
                    rec = self._begin_step(f"document:{spec['id']}")
                    spec["documentation"] = f"ai_docs/dry-run-{spec['id']}.md"
                    self.s.setdefault("documentation", []).append(spec["documentation"])
                    self._end_step(rec, True)
            return
        agent = self.cfg.agents.get("execute", "pipeline-execute")
        run_id = self.state.data.get("run_id", "")
        ai_docs = self.cfg.path("ai_docs_dir")
        ai_docs.mkdir(parents=True, exist_ok=True)
        for spec in self.s.get("specs", []):
            if spec.get("documentation"):
                continue
            step_name = f"document:{spec['id']}"
            rec = self._begin_step(step_name)
            before = snapshot([ai_docs])
            spec_abs = self.cfg.root / spec["path"]
            prompt = render_prompt(self.cfg, "document", {
                "1": str(spec_abs), "2": "",
                "ARGUMENTS": f"{spec['id']} {spec_abs}",
                "spec_id": spec["id"], "spec_path": str(spec_abs),
                "run_id": run_id,
            }) + (
                "\n\n---\nRUNNER NOTE: Follow the document.md instructions exactly.\n"
                "After writing the doc and updating implementation-docs.md, return\n"
                "only the doc path on the FINAL line.\n"
            )
            cr = self.kiro.run(step_name, prompt, agent, self._timeout("document"))
            if not cr.succeeded:
                err = cr.error or f"exit={cr.exit_code}"
                self._end_step(rec, False, error=err, cr=cr)
                raise StepFailed("document", f"{spec['id']}: {err}")
            created = newly_created(before, [ai_docs])
            if created:
                doc_rel = self._rel(created[0])
                spec["documentation"] = doc_rel
                self.s.setdefault("documentation", []).append(doc_rel)
            self._end_step(rec, True, cr=cr)
        # Single consolidated docs commit if tree dirty
        if not working_tree_clean(self.cfg.root, ignore=self.run_log_dir):
            commit_step = f"commit:docs-sprint-{self.sprint.id}"
            rec = self._begin_step(commit_step)
            head_before = head_sha(self.cfg.root)
            commit_prompt = render_prompt(self.cfg, "commit", {
                "ARGUMENTS": f"pipeline docs sprint {self.sprint.id} documentation",
                "run_id": run_id,
            }) + "\n\n---\nRUNNER NOTE: One commit for ALL doc files produced above.\n"
            cr = self.kiro.run(commit_step, commit_prompt, agent,
                               self._timeout("commit"))
            new_sha = head_sha(self.cfg.root)
            if cr.succeeded and new_sha != head_before:
                self._end_step(rec, True, cr=cr)
                log(f"  ✓ docs committed {new_sha[:8]}")
            else:
                err = cr.error or "docs commit produced no diff"
                self._end_step(rec, False, error=err, cr=cr)
                raise StepFailed("document", err)

    # --- Step 8: publish ---
    def step_publish(self) -> None:
        if self._step_completed("publish"):
            return
        if self.dry_run:
            rec = self._begin_step("publish")
            self.s["pr"] = {"number":"0","url":"(dry-run)",
                            "merged":True,"had_conflicts":False}
            self._end_step(rec, True)
            return
        rec = self._begin_step("publish")
        pr = self.s.get("pr") or {}
        try:
            # 1. push sprint branch so remote mirrors local
            subprocess.run(["git", "push", "-u", "origin", self.sprint.branch],
                           cwd=str(self.cfg.root), check=True,
                           capture_output=True, text=True)
            # 2. fetch + checkout main + align local main to origin/main
            subprocess.run(["git", "fetch", "origin", "main"],
                           cwd=str(self.cfg.root), check=True,
                           capture_output=True, text=True)
            subprocess.run(["git", "checkout", "main"],
                           cwd=str(self.cfg.root), check=True,
                           capture_output=True, text=True)
            # Prefer fast-forward; if local main is ahead or diverged, fail
            # loudly rather than silently merging onto stale state (which
                # produces an unpushable commit and strands local history).
            ff = subprocess.run(["git", "merge", "--ff-only", "origin/main"],
                                cwd=str(self.cfg.root), check=False,
                                capture_output=True, text=True)
            if ff.returncode != 0:
                # Local main has commits that don't exist on origin, or
                # histories are unrelated. Either way we cannot safely build
                # a mergeable main on top — bail so an operator can look.
                msg = (ff.stderr or ff.stdout or "fast-forward failed").strip()
                err = (f"local main is not a fast-forward of origin/main: "
                       f"{msg}. Fix manually (e.g. `git fetch origin && "
                       f"git reset --hard origin/main`) and re-run publish.")
                self.s["errors"].append({"step": "publish", "error": err})
                self._end_step(rec, False, error=err)
                raise StepFailed("publish", err)
            pre_merge_sha = head_sha(self.cfg.root)
            # 3. local merge sprint branch into main (no fast-forward, so a
            # merge commit records the sprint as one unit).
            title = f"Sprint {self.sprint.id}: {self.sprint.title}"
            body = self._pr_body()
            body_path = self.run_log_dir / self.sprint.id / "merge-body.md"
            body_path.parent.mkdir(parents=True, exist_ok=True)
            body_path.write_text(body)
            merge_msg = f"{title}\n\n{body}"
            merge = subprocess.run(
                ["git", "merge", "--no-ff", "-m", merge_msg,
                 self.sprint.branch],
                cwd=str(self.cfg.root), capture_output=True, text=True)
            pr.setdefault("url", "")  # no forge URL in local-merge mode
            pr.setdefault("number", "local")
            if merge.returncode == 0:
                merge_sha = head_sha(self.cfg.root)
                # 4. push main
                push = subprocess.run(
                    ["git", "push", "origin", "main"],
                    cwd=str(self.cfg.root), capture_output=True, text=True)
                if push.returncode != 0:
                    # Push rejected (race, protected branch, unrelated
                    # history, etc.). Do NOT reset local main — that
                    # destroys the merge commit and strands the sprint
                    # work. Leave local main at merge_sha so the operator
                    # can inspect, fetch, and retry.
                    msg = (push.stderr or push.stdout or "push rejected").strip()
                    err = (f"push to origin/main rejected: {msg}. "
                           f"Local main is at {merge_sha[:8]} (merge "
                           f"preserved). Resolve on origin and re-push, "
                           f"or resume with --resume-from ...:publish.")
                    self.s["errors"].append({"step": "publish", "error": err})
                    self._end_step(rec, False, error=err)
                    raise StepFailed("publish", err)
                pr["merged"] = True
                pr["merge_sha"] = merge_sha
                self.s["pr"] = pr
                self._end_step(rec, True)
                log(f"  ✓ merged {self.sprint.branch} into main {merge_sha[:8]} and pushed")
                return
            # 5. merge conflict — abort, hand off to resolver agent
            subprocess.run(["git", "merge", "--abort"],
                           cwd=str(self.cfg.root), check=False,
                           capture_output=True, text=True)
            pr["had_conflicts"] = True
            self.s["pr"] = pr
            self.state.save()
            resolved = self._merge_conflict_agent(pr)
            if resolved:
                # resolver agent already committed on the sprint branch and
                # merged main into it. Now re-attempt: checkout main, merge
                # sprint branch (should be clean), push.
                subprocess.run(["git", "checkout", "main"],
                               cwd=str(self.cfg.root), check=True,
                               capture_output=True, text=True)
                retry = subprocess.run(
                    ["git", "merge", "--no-ff", "-m", merge_msg,
                     self.sprint.branch],
                    cwd=str(self.cfg.root), capture_output=True, text=True)
                if retry.returncode == 0:
                    merge_sha = head_sha(self.cfg.root)
                    push = subprocess.run(
                        ["git", "push", "origin", "main"],
                        cwd=str(self.cfg.root), capture_output=True, text=True)
                    if push.returncode == 0:
                        pr["merged"] = True
                        pr["merge_sha"] = merge_sha
                        self.s["pr"] = pr
                        self._end_step(rec, True)
                        log(f"  ✓ merged {self.sprint.branch} into main {merge_sha[:8]} after conflict resolution")
                        return
            err = "merge conflict — see MERGE_CONFLICT.md in run logs"
            self.s["errors"].append({"step": "publish", "error": err})
            self._end_step(rec, False, error=err)
            raise StepFailed("publish", err)
        except subprocess.CalledProcessError as e:
            msg = f"{e.stderr or e.stdout or e}".strip()
            self.s["errors"].append({"step": "publish", "error": msg})
            self._end_step(rec, False, error=msg)
            raise StepFailed("publish", msg)

    def _pr_body(self) -> str:
        lines: list[str] = []
        lines.append(f"## Sprint {self.sprint.id}: {self.sprint.title}\n")
        lines.append(f"**Sprint file**: `{self._rel(self.sprint.path)}`")
        if self.s.get("research_doc"):
            lines.append(f"**Research**: `{self.s['research_doc']}`")
        lines.append("\n### Specs")
        for sp in self.s.get("specs", []):
            sha = (sp.get("commit") or {}).get("sha", "")
            short = sha[:7] if sha else ""
            lines.append(f"- `{short}` {sp.get('title','')} (`{sp.get('path','')}`)")
        if self.s.get("e2e_test_path"):
            lines.append("\n### E2E")
            lines.append(f"- `{self.s['e2e_test_path']}`")
        if self.s.get("documentation"):
            lines.append("\n### Documentation")
            for d in self.s["documentation"]:
                lines.append(f"- `{d}`")
        lines.append("\n_Generated by `tools/sprint_runner.py`_")
        return "\n".join(lines) + "\n"

    def _merge_conflict_agent(self, pr: dict) -> bool:
        """Invoke plan agent to classify + possibly auto-resolve merge conflicts.

        Returns True if all conflicts were TRIVIAL and resolved + pushed.
        """
        agent = self.cfg.agents.get("plan", "pipeline-plan")
        outcome_path = self.run_log_dir / self.sprint.id / "merge-outcome.json"
        report_path = self.run_log_dir / self.sprint.id / "MERGE_CONFLICT.md"
        learnings = self.cfg.path("learnings_file")
        stack = self.cfg.stack
        validation = " && ".join(
            v for v in [stack.get("lint"), stack.get("typecheck"),
                       stack.get("build")] if v)
        prompt = (
            f"You are resolving LOCAL merge conflicts between branch\n"
            f"`{self.sprint.branch}` and `main`. The pipeline merges locally\n"
            f"and pushes to origin — there is no remote PR/MR to interact with.\n\n"
            "STEPS:\n"
            f"1. `git fetch origin && git checkout {self.sprint.branch} "
            "&& git merge origin/main` (capture conflict list)\n"
            "2. For each conflicted file (from `git status --porcelain | grep \"^UU\"`), classify:\n"
            "   - TRIVIAL: non-overlapping additions (separate functions/imports/list entries)\n"
            "   - SEMANTIC: overlapping edits, schema/migration changes, view logic, model defs,\n"
            "     anything requiring business-intent judgement\n"
            f"3. If learnings file exists ({learnings}), read prior resolutions for precedent.\n"
            "4. If ALL conflicts TRIVIAL → resolve them, then run:\n"
            f"     {validation or 'echo \"no validation commands configured\"'}\n"
            "   If validation passes, commit with message\n"
            f"     `pipeline chore merge main into sprint-{self.sprint.id}`,\n"
            f"   then `git push origin {self.sprint.branch}`.\n"
            "   Do NOT attempt to push to main — the runner will do the final\n"
            "   merge-into-main and push after your outcome file is written.\n"
            "5. If ANY conflict SEMANTIC → `git merge --abort` and write a detailed\n"
            f"   conflict report at {report_path} (files + hunks + missing context).\n"
            "   Do not commit.\n"
            f"6. Append the decision as ONE JSON line to {learnings}:\n"
            '   {"ts":"...","sprint":"...","branch":"...","files":[...],'
            '"classification":"TRIVIAL|SEMANTIC","auto_resolved":bool,'
            '"build_passed_after":bool|null,"notes":"..."}\n'
            f"7. Write a final outcome file at {outcome_path} with JSON:\n"
            '   {"auto_resolved":bool,"build_passed_after":bool|null,'
            '"files":[...],"report_path":"<abs>|null"}\n'
        )
        cr = self.kiro.run(f"merge-conflict-sprint-{self.sprint.id}", prompt,
                           agent, self._timeout("merge_conflict"))
        outcome = read_json_file(outcome_path) or {}
        pr["conflict_outcome"] = outcome
        self.state.save()
        if not cr.succeeded:
            return False
        auto = bool(outcome.get("auto_resolved"))
        build_ok = outcome.get("build_passed_after")
        return auto and (build_ok is None or bool(build_ok))

    # --- Orchestrator ---
    def run(self) -> None:
        if self.s.get("status") == "completed" and self.force_step is None:
            log(f"  ✓ sprint {self.sprint.id} already completed — skipping")
            return
        self.s["status"] = "in_progress"
        if not self.s.get("started_at"):
            self.s["started_at"] = now_iso()
        self.state.save()
        t0 = time.monotonic()
        try:
            self.step_branch()
            self.step_research()
            self.step_plan()
            self.step_build()
            self.step_test()
            self.step_e2e()
            self.step_review()
            self.step_document()
            self.step_publish()
            self.s["status"] = "completed"
            self.s["completed_at"] = now_iso()
            self.s["duration_seconds"] = round(time.monotonic() - t0, 3)
            self.state.save()
        except StepFailed as e:
            self.s["status"] = "failed"
            self.s["completed_at"] = now_iso()
            self.s["duration_seconds"] = round(time.monotonic() - t0, 3)
            self.s["errors"].append({"step": e.step, "error": e.message})
            self.state.save()
            raise


# -------- CLI --------
def _find_run(cfg: Config, run_id: str) -> Path:
    run_dir = cfg.path("runs_dir") / run_id
    state_path = run_dir / "state.json"
    if not state_path.exists():
        fail(f"no such run: {run_id} (expected {state_path})")
    return run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sprint_runner")
    parser.add_argument("--config", default="tools/pipeline.yaml",
                        help="path to pipeline.yaml (default: tools/pipeline.yaml)")
    parser.add_argument("--sprint", help="sprint selector: '03' | '03-08' | '03,07,11'")
    parser.add_argument("--run-id", help="explicit run id")
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--resume", help="resume a run by id")
    grp.add_argument("--resume-from", help="resume at RUN[:SPRINT[:STEP]]")
    parser.add_argument("--list-sprints", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-step", choices=STEP_ORDER[1:],
                        help="re-run one step even if cached")
    args = parser.parse_args(argv)

    cfg = Config.load(Path(args.config).resolve())
    if args.list_sprints:
        return cmd_list_sprints(cfg)

    # Resolve run_id + selected sprints
    force_step = args.force_step
    if args.resume_from:
        run_id, resume_sprint, resume_step = parse_resume_from(args.resume_from)
        run_dir = _find_run(cfg, run_id)
        run_state = State(run_dir / "state.json")
        if resume_sprint and resume_step:
            try:
                sp_rec = run_state.sprint(resume_sprint)
                reset_sprint_from(sp_rec, resume_step)
                force_step = resume_step
                run_state.save()
            except KeyError:
                fail(f"sprint {resume_sprint} not in run {run_id}")
        selector = args.sprint or run_state.data.get("sprint_selector")
    elif args.resume:
        run_id = args.resume
        run_dir = _find_run(cfg, run_id)
        run_state = State(run_dir / "state.json")
        selector = args.sprint or run_state.data.get("sprint_selector")
    else:
        if not args.sprint:
            fail("--sprint is required for a fresh run")
        import datetime as _dt
        run_id = args.run_id or _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = cfg.path("runs_dir") / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        run_state = State(run_dir / "state.json")
        run_state.data.setdefault("run_id", run_id)
        run_state.data.setdefault("started_at", now_iso())
        run_state.data.setdefault("sprints", [])
        run_state.data["sprint_selector"] = args.sprint
        run_state.data["plan_agent"] = cfg.agents.get("plan", "pipeline-plan")
        run_state.data["execute_agent"] = cfg.agents.get("execute", "pipeline-execute")
        run_state.data["browser_agent"] = cfg.agents.get("browser", "pipeline-execute-browser")
        run_state.data["status"] = "in_progress"
        run_state.save()
        selector = args.sprint

    # Resume safety: clean tree
    if args.resume or args.resume_from:
        if not working_tree_clean(cfg.root, ignore=run_dir):
            fail("working tree not clean — commit or stash before resuming")
        # Clear stale terminal status
        for s in run_state.data.get("sprints", []):
            if s.get("status") in ("failed", "completed", "interrupted"):
                if s.get("status") != "completed":
                    s["status"] = "pending"
                    s["completed_at"] = None
                    s["duration_seconds"] = 0.0
        if run_state.data.get("status") in ("failed", "interrupted"):
            run_state.data["status"] = "in_progress"
            run_state.data["completed_at"] = None
        run_state.save()

    sprints = discover_sprints(cfg, selector)
    t0 = time.monotonic()
    with RunLock(run_dir):
        try:
            for sp in sprints:
                log(f"▶ sprint {sp.id}: {sp.title}")
                ex = SprintExecutor(sp, cfg, run_state, run_dir,
                                    dry_run=args.dry_run,
                                    force_step=force_step)
                ex.run()
                force_step = None  # only applies to first sprint
            run_state.data["status"] = "completed"
            run_state.data["completed_at"] = now_iso()
            run_state.data["duration_seconds"] = round(time.monotonic() - t0, 3)
            run_state.save()
            log(f"✓ run {run_id} completed")
            return 0
        except StepFailed as e:
            run_state.data["status"] = "failed"
            run_state.data["completed_at"] = now_iso()
            run_state.data["duration_seconds"] = round(time.monotonic() - t0, 3)
            run_state.save()
            log(f"⛔ sprint failure: {e}")
            return 2
        except KeyboardInterrupt:
            run_state.data["status"] = "interrupted"
            run_state.save()
            log("⚠ interrupted")
            return 130


if __name__ == "__main__":
    sys.exit(main())
