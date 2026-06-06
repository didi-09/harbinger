#!/usr/bin/env python3
"""
honeypot_manager.py — The only entry point OpenClaw is allowed to call.

Commands:
  classify  --log <path>
  deploy    --blueprint <name> --session <id> [--static]
  logs      --session <id>
  behavior  --session <id> --mode <mode>
  report    --session <id>
  stop      --session <id>
"""

import argparse
import json
import os
import random
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import jinja2

BASE = Path(__file__).parent.resolve()
CONFIG_PATH = BASE / "config.json"
BLUEPRINTS = BASE / "blueprints"
RUNNING = BASE / "running"
REPORTS = BASE / "reports"

# ---------------------------------------------------------------------------
# Session ID validation — closes path-traversal via --session arg  (#10)
# ---------------------------------------------------------------------------

_SESSION_ID_RE = re.compile(r'^[A-Za-z0-9_-]{1,64}$')


def _validate_session_id(session_id: str):
    if not _SESSION_ID_RE.match(session_id):
        err(
            f"Invalid session ID '{session_id}': must match "
            r"^[A-Za-z0-9_-]{1,64}$"
        )


# ---------------------------------------------------------------------------
# Dynamic port allocation — one free OS port per session  (#5)
# ---------------------------------------------------------------------------

def _alloc_free_port() -> int:
    """Bind to port 0, let the kernel pick, return the chosen port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def out(data: dict):
    print(json.dumps(data, indent=2))


def err(msg: str, code: int = 1):
    print(json.dumps({"error": msg}), file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------------------
# Volume-sync verification  (#7)
# ---------------------------------------------------------------------------

def _verify_volume_sync(session_id: str, container_path: str,
                         timeout_ms: float = 5000.0) -> float:
    """
    Poll container until the file at container_path is visible.
    Returns propagation latency in milliseconds, or -1.0 on timeout.
    Only meaningful for real Docker containers (status == 'running').
    """
    deadline = time.perf_counter() + timeout_ms / 1000.0
    while time.perf_counter() < deadline:
        result = subprocess.run(
            ["docker", "exec", session_id, "test", "-f", container_path],
            capture_output=True
        )
        if result.returncode == 0:
            elapsed = (deadline - time.perf_counter() + timeout_ms / 1000.0)
            # Compute actual elapsed from start, not remaining time
            break
        time.sleep(0.05)
    else:
        return -1.0
    # Re-measure properly: caller should use time.perf_counter around this fn.
    # Return a sentinel 0.0 to indicate "visible immediately on first poll".
    return 0.0


def _verify_volume_sync_timed(session_id: str, container_path: str,
                               timeout_ms: float = 5000.0) -> float:
    """Same as above but measures the latency correctly with an internal timer."""
    t0 = time.perf_counter()
    deadline = t0 + timeout_ms / 1000.0
    while time.perf_counter() < deadline:
        result = subprocess.run(
            ["docker", "exec", session_id, "test", "-f", container_path],
            capture_output=True
        )
        if result.returncode == 0:
            return (time.perf_counter() - t0) * 1000.0
        time.sleep(0.05)
    return -1.0


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------

_MAX_EVENTS = 1000
_MAX_EVENT_LEN = 512


def _sanitize_log(log: dict) -> dict:
    """
    Bound and sanitize attack-log fields before classification.
    Prevents oversized/malformed input from affecting rule evaluation  (#9).
    """
    events = log.get("events", [])
    if not isinstance(events, list):
        events = []
    events = [str(e)[:_MAX_EVENT_LEN] for e in events[:_MAX_EVENTS]]
    port = log.get("destination_port", 0)
    try:
        port = int(port)
    except (TypeError, ValueError):
        port = 0
    return {
        "id": str(log.get("id", "unknown"))[:64],
        "source_ip": str(log.get("source_ip", ""))[:64],
        "destination_port": port,
        "timestamp": str(log.get("timestamp", ""))[:32],
        "events": events,
    }


def cmd_classify(args):
    log_path = Path(args.log)
    if not log_path.exists():
        err(f"Log file not found: {log_path}")

    with open(log_path) as f:
        raw_log = json.load(f)

    log = _sanitize_log(raw_log)  # sanitize before any rule evaluation  (#9)

    cfg = load_config()
    rules = cfg["classify_rules"]
    port = log.get("destination_port", 0)
    events = log.get("events", [])
    events_str = " ".join(events).lower()

    scores = {}

    # SSH scoring
    ssh_score = 0
    ssh_rule = rules["ssh_bruteforce"]
    if port in ssh_rule["ports"]:
        ssh_score += 0.4
    for kw in ssh_rule["keywords"]:
        if kw.lower() in events_str:
            ssh_score += 0.1
    for u in ssh_rule["usernames"]:
        pattern = r'\b' + re.escape(u) + r'\b'
        if re.search(pattern, events_str):
            ssh_score += 0.05
    scores["ssh_bruteforce"] = min(ssh_score, 1.0)

    # Web scoring
    web_score = 0
    web_rule = rules["web_attack"]
    if port in web_rule["ports"]:
        web_score += 0.4
    for kw in web_rule["keywords"]:
        if kw.lower() in events_str:
            web_score += 0.08
    for p in web_rule["paths"]:
        if p.lower() in events_str:
            web_score += 0.07
    scores["web_attack"] = min(web_score, 1.0)

    best = max(scores, key=scores.get)
    confidence = scores[best]
    threshold = cfg["confidence_thresholds"]["deploy"]

    if confidence < threshold:
        best = "monitor_only"
        attack_type = "Unknown"
        confidence = round(1.0 - confidence, 2)
    else:
        attack_type = "SSH Brute Force" if best == "ssh_bruteforce" else "Web Attack"

    # Collect indicators
    indicators = {"targeted_ports": [port], "event_count": len(events)}
    if best == "ssh_bruteforce" or scores.get("ssh_bruteforce", 0) > 0.1:
        found_users = []
        for u in ssh_rule["usernames"]:
            if re.search(r'\b' + re.escape(u) + r'\b', events_str):
                found_users.append(u)
        indicators["usernames_attempted"] = found_users
        kw_found = [kw for kw in ssh_rule["keywords"] if kw.lower() in events_str]
        indicators["keywords"] = kw_found
    if best == "web_attack" or scores.get("web_attack", 0) > 0.1:
        path_found = [p for p in web_rule["paths"] if p.lower() in events_str]
        indicators["paths_probed"] = path_found

    log_id = log.get("id", log_path.stem)
    out({
        "log_id": log_id,
        "attack_type": attack_type,
        "confidence": round(confidence, 2),
        "suggested_blueprint": best,
        "indicators": indicators
    })


# ---------------------------------------------------------------------------
# deploy
# ---------------------------------------------------------------------------

def _session_dir(session_id: str) -> Path:
    return RUNNING / session_id


def _load_session(session_id: str) -> dict:
    path = _session_dir(session_id) / "session.json"
    if not path.exists():
        err(f"Session not found: {session_id}")
    with open(path) as f:
        return json.load(f)


def _save_session(session_id: str, session: dict):
    path = _session_dir(session_id) / "session.json"
    with open(path, "w") as f:
        json.dump(session, f, indent=2)


def _write_behavior_files(blueprint_name: str, mode_name: str, session_id: str,
                           extra_context: dict = None, backdate: bool = True):
    """
    Render Jinja2 templates for a behavior mode into the session's honeyfs.

    backdate=True: randomize mtime/atime to a plausible past value so decoys
    do not carry a tell-tale "just created" timestamp visible to an attacker
    watching the filesystem  (#11).
    """
    bp_dir = BLUEPRINTS / blueprint_name
    profiles_path = bp_dir / "behavior_profiles.json"
    with open(profiles_path) as f:
        profiles = json.load(f)

    mode = profiles["modes"].get(mode_name)
    if mode is None:
        err(f"Mode '{mode_name}' not found in blueprint '{blueprint_name}'")

    honeyfs = _session_dir(session_id) / "honeyfs"
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(bp_dir)))

    ctx = extra_context or {}

    written = []
    for file_spec in mode.get("files", []):
        dest = honeyfs / file_spec["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        template = jinja_env.get_template(file_spec["template"])
        rendered = template.render(**ctx)
        dest.write_text(rendered)

        if backdate:
            # Backdate by a random 3–30 day offset so decoy files look aged  (#11)
            age_seconds = random.uniform(3 * 86400, 30 * 86400)
            past_ts = time.time() - age_seconds
            os.utime(dest, (past_ts, past_ts))

        written.append(str(dest.relative_to(BASE)))

    return written


def cmd_deploy(args):
    blueprint_name = args.blueprint
    session_id = args.session
    static_mode = getattr(args, "static", False)  # --static for baseline  (#2)

    _validate_session_id(session_id)

    cfg = load_config()

    if blueprint_name not in cfg["allowed_blueprints"]:
        err(f"Unknown blueprint: {blueprint_name}")

    bp_dir = BLUEPRINTS / blueprint_name
    if not bp_dir.exists():
        err(f"Blueprint directory not found: {bp_dir}")

    session_dir = _session_dir(session_id)
    if session_dir.exists():
        err(f"Session already exists: {session_id}. Use a different session ID.")

    honeyfs = session_dir / "honeyfs"
    logs_dir = session_dir / "logs"
    honeyfs.mkdir(parents=True)
    logs_dir.mkdir(parents=True)

    with open(bp_dir / "blueprint.json") as f:
        blueprint = json.load(f)

    # Static mode: pre-write the union of ALL non-default decoy modes  (#2)
    # The only difference from adaptive is that cmd_behavior becomes a no-op.
    if static_mode:
        with open(bp_dir / "behavior_profiles.json") as f:
            profiles = json.load(f)
        for m_name in profiles["modes"]:
            if m_name != "default":
                _write_behavior_files(blueprint_name, m_name, session_id, backdate=True)
        current_mode = "static_all_modes"
    else:
        _write_behavior_files(blueprint_name, "default", session_id, backdate=False)
        current_mode = "default"

    # Initialize session state
    session = {
        "session_id": session_id,
        "blueprint": blueprint_name,
        "status": "deploying",
        "current_mode": current_mode,
        "static": static_mode,
        "engagement_score": 0,
        "step_count": 0,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "events_seen": [],
        "mode_history": [],
        "log_offset": 0,
        "attempted_usernames": [],
        "paths_visited": {},
        "host_ports": {}
    }
    _save_session(session_id, session)

    # Allocate per-session host ports to allow concurrent sessions  (#5)
    ports = blueprint.get("ports", {})
    host_ports = {}
    compose_file = bp_dir / "docker-compose.yml"
    container_id = "simulated"
    container_status = "simulated"
    compose_error = None

    if compose_file.exists() and blueprint_name != "monitor_only":
        env = os.environ.copy()
        env["SESSION_ID"] = session_id
        env["HONEYFS_PATH"] = str(honeyfs.resolve())
        env["LOGS_PATH"] = str(logs_dir.resolve())

        if "22" in ports:
            allocated = _alloc_free_port()
            host_ports["22"] = str(allocated)
            env["SSH_PORT"] = str(allocated)
        if "80" in ports:
            allocated = _alloc_free_port()
            host_ports["80"] = str(allocated)
            env["WEB_PORT"] = str(allocated)

        result = subprocess.run(
            ["docker-compose", "-f", str(compose_file), "up", "-d"],
            capture_output=True, text=True, env=env
        )
        if result.returncode != 0:
            import shutil
            shutil.rmtree(session_dir)
            err(
                f"Docker compose failed (exit {result.returncode}): "
                f"{result.stderr.strip()[:300]}"
            )

        id_result = subprocess.run(
            ["docker", "ps", "-qf", f"name={session_id}"],
            capture_output=True, text=True
        )
        container_id = id_result.stdout.strip()
        if not container_id:
            import shutil
            shutil.rmtree(session_dir)
            err(
                f"docker-compose up returned 0 but container '{session_id}' "
                f"is not visible in 'docker ps'. Check image availability."
            )
        container_status = "running"
    elif blueprint_name == "monitor_only":
        container_status = "passive"

    session["status"] = container_status
    session["container_id"] = container_id
    session["host_ports"] = host_ports
    _save_session(session_id, session)

    out({
        "session_id": session_id,
        "blueprint": blueprint_name,
        "status": container_status,
        "container_id": container_id,
        "ports": ports,
        "host_ports": host_ports,
        "current_mode": current_mode,
        "static": static_mode,
        "engagement_score": 0,
        "honeyfs_path": str(honeyfs.relative_to(BASE)),
        "logs_path": str(logs_dir.relative_to(BASE))
    })


# ---------------------------------------------------------------------------
# logs
# ---------------------------------------------------------------------------

COWRIE_EVENT_MAP = {
    "cowrie.login.failed": "login_attempt",
    "cowrie.login.success": "login_attempt",
    "cowrie.command.input": "command_executed",
    "cowrie.session.file_download": "file_download",
    "cowrie.session.connect": "connection",
    "cowrie.session.file_upload": "file_read",
}

FLASK_EVENT_MAP = {
    "get": "connection",
    "post": "login_attempt",
    "file_read": "file_read",
    "file_download": "file_download",
}

# Regex patterns for parsing Cowrie stdout (used when JSON log file unavailable)
_COWRIE_LOGIN_OK  = re.compile(r"login attempt \[b'([^']+)'/b'([^']+)'\] succeeded")
_COWRIE_LOGIN_FAIL = re.compile(r"login attempt \[b'([^']+)'/b'([^']+)'\] failed")
_COWRIE_CMD       = re.compile(r"CMD:\s+(.+)")
_COWRIE_CONNECT   = re.compile(r"New connection: (\S+) \(")
_COWRIE_DOWNLOAD  = re.compile(r"file download url: (\S+)")
_COWRIE_TS        = re.compile(r"^(\d{4}-\d{2}-\d{2}T[\d:+]+)")


def _parse_cowrie_docker_logs(session_id: str, offset: int) -> tuple[list[dict], int]:
    """
    Read Cowrie events directly from `docker logs` stdout.
    Cowrie always writes to stdout regardless of JSON log file path.
    `offset` is a line count into the full docker logs output.
    """
    result = subprocess.run(
        ["docker", "logs", session_id],
        capture_output=True, text=True
    )
    raw = (result.stdout + result.stderr).splitlines()
    new_lines = raw[offset:]
    events = []
    ts = datetime.now(timezone.utc).isoformat()

    for line in new_lines:
        ts_match = _COWRIE_TS.match(line)
        if ts_match:
            ts = ts_match.group(1)

        m = _COWRIE_LOGIN_OK.search(line)
        if m:
            events.append({"type": "login_attempt", "username": m.group(1),
                           "password": m.group(2), "success": True, "timestamp": ts})
            continue

        m = _COWRIE_LOGIN_FAIL.search(line)
        if m:
            events.append({"type": "login_attempt", "username": m.group(1),
                           "password": m.group(2), "success": False, "timestamp": ts})
            continue

        m = _COWRIE_CMD.search(line)
        if m:
            events.append({"type": "command_executed", "command": m.group(1).strip(),
                           "timestamp": ts})
            continue

        m = _COWRIE_CONNECT.search(line)
        if m:
            events.append({"type": "connection", "remote": m.group(1), "timestamp": ts})
            continue

        m = _COWRIE_DOWNLOAD.search(line)
        if m:
            events.append({"type": "file_download", "url": m.group(1), "timestamp": ts})

    return events, offset + len(new_lines)


def _parse_cowrie_logs(logs_dir: Path, offset: int, session_id: str = "") -> tuple[list[dict], int]:
    log_file = logs_dir / "cowrie.json"
    candidates = sorted(logs_dir.glob("cowrie.json*")) if not log_file.exists() else [log_file]

    if candidates and candidates[0].stat().st_size > 0:
        lines = candidates[0].read_text().splitlines()
        new_lines = lines[offset:]
        events = []
        for line in new_lines:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            event_id = entry.get("eventid", "")
            etype = COWRIE_EVENT_MAP.get(event_id, "connection")
            ev = {"type": etype, "raw_event": event_id, "timestamp": entry.get("timestamp", "")}
            if event_id == "cowrie.login.failed":
                ev["username"] = entry.get("username", "")
                ev["password"] = entry.get("password", "")
                ev["success"] = False
            elif event_id == "cowrie.login.success":
                ev["username"] = entry.get("username", "")
                ev["password"] = entry.get("password", "")
                ev["success"] = True
            elif event_id == "cowrie.command.input":
                ev["command"] = entry.get("input", "")
            elif event_id == "cowrie.session.file_download":
                ev["file"] = entry.get("outfile", entry.get("shasum", ""))
            events.append(ev)
        return events, offset + len(new_lines)

    if session_id:
        return _parse_cowrie_docker_logs(session_id, offset)
    return [], offset


def _parse_flask_logs(logs_dir: Path, offset: int) -> tuple[list[dict], int]:
    log_file = logs_dir / "requests.json"
    if not log_file.exists():
        return [], offset

    lines = log_file.read_text().splitlines()
    new_lines = lines[offset:]
    events = []

    for line in new_lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = entry.get("method", "GET").lower()
        path = entry.get("path", "/")
        etype = "connection"
        if method == "post":
            etype = "login_attempt"
        if entry.get("file_read"):
            etype = "file_read"
        if entry.get("file_download"):
            etype = "file_download"
        ev = {
            "type": etype,
            "method": method.upper(),
            "path": path,
            "status": entry.get("status", 200),
            "timestamp": entry.get("timestamp", "")
        }
        events.append(ev)

    return events, offset + len(new_lines)


def _parse_simulated_logs(logs_dir: Path, offset: int, session: dict) -> tuple[list[dict], int]:
    sim_file = logs_dir / "sim_events.json"
    if sim_file.exists():
        blueprint = session.get("blueprint", "")
        if blueprint == "ssh_bruteforce":
            return _parse_cowrie_logs(logs_dir, offset)
        else:
            return _parse_flask_logs(logs_dir, offset)
    return [], offset


def _score_event(event: dict, cfg: dict) -> int:
    weights = cfg["score_weights"]
    etype = event.get("type", "connection")
    return weights.get(etype, 0)


def cmd_logs(args):
    session_id = args.session
    _validate_session_id(session_id)
    session = _load_session(session_id)
    cfg = load_config()
    logs_dir = _session_dir(session_id) / "logs"
    blueprint = session["blueprint"]
    offset = session.get("log_offset", 0)

    if blueprint == "ssh_bruteforce":
        events, new_offset = _parse_cowrie_logs(logs_dir, offset, session_id)
    elif blueprint == "web_attack":
        events, new_offset = _parse_flask_logs(logs_dir, offset)
    else:
        events, new_offset = [], offset

    score_delta = 0
    no_new_activity = len(events) == 0

    for ev in events:
        delta = _score_event(ev, cfg)
        ev["score_delta"] = delta
        score_delta += delta
        if ev.get("username") and ev["username"] not in session["attempted_usernames"]:
            session["attempted_usernames"].append(ev["username"])
        if ev.get("path"):
            path = ev["path"]
            session["paths_visited"][path] = session["paths_visited"].get(path, 0) + 1

    if no_new_activity:
        score_delta = cfg["score_weights"]["no_new_activity"]

    session["engagement_score"] = max(0, session["engagement_score"] + score_delta)
    session["step_count"] += 1
    session["log_offset"] = new_offset
    session["events_seen"].extend(events)
    _save_session(session_id, session)

    out({
        "session_id": session_id,
        "new_events": events,
        "total_events": len(session["events_seen"]),
        "no_new_activity": no_new_activity,
        "score_delta": score_delta,
        "engagement_score": session["engagement_score"],
        "current_mode": session["current_mode"],
        "step_count": session["step_count"],
        "attempted_usernames": session["attempted_usernames"],
        "paths_visited": session["paths_visited"]
    })


# ---------------------------------------------------------------------------
# behavior
# ---------------------------------------------------------------------------

def cmd_behavior(args):
    session_id = args.session
    mode_name = args.mode
    _validate_session_id(session_id)
    session = _load_session(session_id)

    # No-op for static baseline sessions  (#2)
    if session.get("static"):
        out({
            "session_id": session_id,
            "previous_mode": session.get("current_mode"),
            "new_mode": session.get("current_mode"),
            "files_written": [],
            "note": "static baseline — switching disabled"
        })
        return

    blueprint_name = session["blueprint"]

    bp_dir = BLUEPRINTS / blueprint_name
    with open(bp_dir / "blueprint.json") as f:
        blueprint = json.load(f)

    if mode_name not in blueprint["allowed_modes"]:
        err(
            f"Mode '{mode_name}' not allowed for blueprint '{blueprint_name}'. "
            f"Allowed: {blueprint['allowed_modes']}"
        )

    prev_mode = session["current_mode"]
    if prev_mode == mode_name:
        out({
            "session_id": session_id,
            "previous_mode": prev_mode,
            "new_mode": mode_name,
            "files_written": [],
            "note": f"Already in mode '{mode_name}'. No change."
        })
        return

    ctx = {
        "attempted_usernames": session.get("attempted_usernames", []),
        "paths_visited": session.get("paths_visited", {}),
        "session_id": session_id,
        "auth_token": f"tok_{session_id}_2024",
        "backup_user": "backupsvc"
    }

    # ── Latency measurement (#3, #7) ──────────────────────────────────────
    t0 = time.perf_counter()
    written = _write_behavior_files(blueprint_name, mode_name, session_id, ctx)
    template_build_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    # Volume-sync timing: how long until the container sees the first new file
    volume_sync_ms = -1.0
    if session.get("status") == "running" and written:
        honeyfs_mount = blueprint.get("honeyfs_mount", "")
        if honeyfs_mount:
            # First written file's path relative to honeyfs root
            first_abs = written[0]  # e.g. "running/hp_x/honeyfs/home/admin/creds.txt"
            honeyfs_prefix = f"running/{session_id}/honeyfs/"
            if honeyfs_prefix in first_abs:
                rel = first_abs.split(honeyfs_prefix, 1)[1]
                container_path = honeyfs_mount.rstrip("/") + "/" + rel
                volume_sync_ms = round(
                    _verify_volume_sync_timed(session_id, container_path), 2
                )

    total_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    # Persist switch latency metrics  (#3)
    metrics_path = _session_dir(session_id) / "switch_metrics.json"
    metrics: list = []
    if metrics_path.exists():
        try:
            metrics = json.loads(metrics_path.read_text())
        except Exception:
            metrics = []
    metrics.append({
        "from": prev_mode,
        "to": mode_name,
        "at_step": session["step_count"],
        "at_score": session["engagement_score"],
        "template_build_ms": template_build_ms,
        "volume_sync_ms": volume_sync_ms,
        "total_ms": total_ms,
        "ts": datetime.now(timezone.utc).isoformat()
    })
    metrics_path.write_text(json.dumps(metrics, indent=2))

    session["current_mode"] = mode_name
    session["mode_history"].append({
        "from": prev_mode,
        "to": mode_name,
        "at_step": session["step_count"],
        "at_score": session["engagement_score"],
        "template_build_ms": template_build_ms,
        "volume_sync_ms": volume_sync_ms,
        "total_ms": total_ms,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    _save_session(session_id, session)

    out({
        "session_id": session_id,
        "previous_mode": prev_mode,
        "new_mode": mode_name,
        "files_written": written,
        "latency": {
            "template_build_ms": template_build_ms,
            "volume_sync_ms": volume_sync_ms,
            "total_ms": total_ms
        },
        "note": "Files live in shared volume. Container reads them immediately. No restart needed."
    })


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def cmd_report(args):
    session_id = args.session
    _validate_session_id(session_id)
    session = _load_session(session_id)
    REPORTS.mkdir(exist_ok=True)

    events = session.get("events_seen", [])
    mode_history = session.get("mode_history", [])
    score = session["engagement_score"]
    blueprint = session["blueprint"]
    start_time = session.get("start_time", "unknown")
    steps = session.get("step_count", 0)
    usernames = session.get("attempted_usernames", [])
    paths = session.get("paths_visited", {})
    host_ports = session.get("host_ports", {})
    static_mode = session.get("static", False)

    # Build timeline table
    timeline_rows = []
    for i, ev in enumerate(events):
        row = f"| {i+1} | {ev.get('timestamp','—')[:19]} | {ev.get('type','—')} | "
        if ev.get("username"):
            row += f"user={ev['username']} "
        if ev.get("command"):
            row += f"cmd={ev['command'][:40]} "
        if ev.get("path"):
            row += f"path={ev['path']} "
        if ev.get("file"):
            row += f"file={ev['file']} "
        row += f"| {ev.get('score_delta', 0)} |"
        timeline_rows.append(row)

    timeline_md = "\n".join(timeline_rows) if timeline_rows else "| — | — | — | — | — |"

    # Mode switch section
    switch_rows = []
    for sw in mode_history:
        lat = f"total={sw.get('total_ms','—')}ms"
        switch_rows.append(
            f"| Step {sw['at_step']} | {sw['from']} → {sw['to']} "
            f"| Score={sw['at_score']} | {lat} | {sw.get('timestamp','')[:19]} |"
        )
    switch_md = "\n".join(switch_rows) if switch_rows else "| — | — | — | — | — |"

    # Decoy engagement
    decoys_accessed = [ev for ev in events if ev.get("type") in ("file_read", "file_download")]
    decoy_list = "\n".join(
        f"- {ev.get('file', ev.get('path','?'))} ({ev['type']})"
        for ev in decoys_accessed
    ) or "- None recorded"

    # Recommendation logic
    if score >= 10:
        recommendation = (
            "HIGH engagement detected. Attacker deeply interacted with decoys. "
            "Recommend: collect all forensic artifacts, block source IP at perimeter, "
            "escalate to threat intel team."
        )
    elif score >= 5:
        recommendation = (
            "MEDIUM engagement. Attacker probed the system but did not fully commit. "
            "Recommend: continue monitoring from a fresh session, review attempted credentials."
        )
    else:
        recommendation = (
            "LOW engagement. Attacker likely moved on or detected the honeypot. "
            "Recommend: log and monitor, no immediate escalation needed."
        )

    credentials_section = ""
    if usernames:
        credentials_section = f"**Usernames attempted:** {', '.join(usernames)}\n\n"
    if paths:
        top_paths = sorted(paths.items(), key=lambda x: x[1], reverse=True)[:5]
        credentials_section += "**Paths probed (top 5):**\n" + "\n".join(
            f"- {p}: {c} hits" for p, c in top_paths
        )

    mode_tag = "STATIC BASELINE" if static_mode else "ADAPTIVE"

    report_md = f"""# Honeypot Incident Report — {session_id}

**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
**Blueprint:** {blueprint}
**Mode:** {mode_tag}
**Session Start:** {start_time[:19]}
**Total Steps:** {steps}
**Host Ports:** {json.dumps(host_ports)}

---

## Attack Summary

| Field | Value |
|---|---|
| Session ID | {session_id} |
| Blueprint Deployed | {blueprint} |
| Mode | {mode_tag} |
| Final Engagement Score | {score} |
| Total Events | {len(events)} |
| Behavior Switches | {len(mode_history)} |

---

## Session Timeline

| # | Timestamp | Event Type | Detail | Score Δ |
|---|---|---|---|---|
{timeline_md}

---

## Behavior Switches

| When | Transition | Score at Switch | Latency | Timestamp |
|---|---|---|---|---|
{switch_md}

---

## Engagement Analysis

- **Final Score:** {score}
- **Peak Engagement:** {score} (final)
- **Steps Monitored:** {steps}
- **Behavior Switches:** {len(mode_history)}

---

## Collected Intelligence

{credentials_section}

---

## Deception Assessment

### Decoys Accessed

{decoy_list}

---

## Recommendation

{recommendation}

---

*Generated by honeypot_manager.py — OpenClaw Honeypot Orchestration System*
"""

    report_path = REPORTS / f"{session_id}_report.md"
    report_path.write_text(report_md)

    out({
        "session_id": session_id,
        "report_path": str(report_path.relative_to(BASE)),
        "engagement_score": score,
        "total_events": len(events),
        "behavior_switches": len(mode_history)
    })


# ---------------------------------------------------------------------------
# stop
# ---------------------------------------------------------------------------

def cmd_stop(args):
    session_id = args.session
    _validate_session_id(session_id)
    session = _load_session(session_id)
    blueprint_name = session["blueprint"]
    compose_file = BLUEPRINTS / blueprint_name / "docker-compose.yml"

    if compose_file.exists() and blueprint_name != "monitor_only":
        session_dir = _session_dir(session_id)
        honeyfs = session_dir / "honeyfs"
        logs_dir = session_dir / "logs"
        env = os.environ.copy()
        env["SESSION_ID"] = session_id
        env["HONEYFS_PATH"] = str(honeyfs.resolve())
        env["LOGS_PATH"] = str(logs_dir.resolve())
        host_ports = session.get("host_ports", {})
        if "22" in host_ports:
            env["SSH_PORT"] = host_ports["22"]
        if "80" in host_ports:
            env["WEB_PORT"] = host_ports["80"]
        subprocess.run(
            ["docker-compose", "-f", str(compose_file), "down"],
            capture_output=True, text=True, env=env
        )

    session["status"] = "stopped"
    session["stopped_at"] = datetime.now(timezone.utc).isoformat()
    _save_session(session_id, session)

    out({
        "session_id": session_id,
        "status": "stopped",
        "engagement_score": session["engagement_score"],
        "total_events": len(session.get("events_seen", [])),
        "note": "All logs and honeyfs preserved for forensic review."
    })


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(prog="honeypot_manager.py")
    sub = parser.add_subparsers(dest="command", required=True)

    p_classify = sub.add_parser("classify")
    p_classify.add_argument("--log", required=True)

    p_deploy = sub.add_parser("deploy")
    p_deploy.add_argument("--blueprint", required=True)
    p_deploy.add_argument("--session", required=True)
    p_deploy.add_argument(
        "--static", action="store_true",
        help="Static baseline mode: pre-write all decoy files at deploy time, "
             "disable adaptive switching. Used for baseline comparison (#2)."
    )

    p_logs = sub.add_parser("logs")
    p_logs.add_argument("--session", required=True)

    p_behavior = sub.add_parser("behavior")
    p_behavior.add_argument("--session", required=True)
    p_behavior.add_argument("--mode", required=True)

    p_report = sub.add_parser("report")
    p_report.add_argument("--session", required=True)

    p_stop = sub.add_parser("stop")
    p_stop.add_argument("--session", required=True)

    args = parser.parse_args()
    dispatch = {
        "classify": cmd_classify,
        "deploy": cmd_deploy,
        "logs": cmd_logs,
        "behavior": cmd_behavior,
        "report": cmd_report,
        "stop": cmd_stop,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
