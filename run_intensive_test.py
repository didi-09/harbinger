#!/usr/bin/env python3
"""
run_intensive_test.py — Automated full-pipeline test across all 10 attack logs.

Runs without OpenClaw. Implements the same decision logic as SKILL.md in Python
so you can verify the entire stack (classifier → container → simulator → behavior
switch → report) in one shot.

Usage:
  python3 run_intensive_test.py [--intensity 1|2|3] [--log ssh_001] [--logs-wait 15]

Options:
  --intensity   1=light, 2=medium, 3=heavy (default: 2)
  --log         run a single log only (e.g. ssh_001)
  --logs-wait   seconds to wait for simulator traffic to register (default: 15)
  --no-stop     keep containers running after test (for manual inspection)
"""

import argparse
import json
import subprocess
import sys
import time
import threading
from pathlib import Path

BASE = Path(__file__).parent.resolve()
LOGS_DIR = BASE / "attack_logs"
MANAGER = str(BASE / "honeypot_manager.py")

# Import the canonical policy engine so decision logic is not duplicated  (#13)
sys.path.insert(0, str(BASE))
from policy.policy_engine import decide_switch, should_stop  # noqa: E402

RESULTS = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def mgr(*args) -> dict:
    """Run a honeypot_manager.py command, return parsed JSON output."""
    cmd = ["python3", MANAGER] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE)
    if result.returncode != 0:
        err = result.stderr.strip()
        raise RuntimeError(f"manager error: {err}")
    return json.loads(result.stdout)


def run_sim(log_path: str, session_id: str, intensity: int):
    """Run simulate_attack.py in a subprocess (blocking)."""
    cmd = ["python3", str(BASE / "simulate_attack.py"),
           "--log", log_path,
           "--session", session_id,
           "--intensity", str(intensity)]
    subprocess.run(cmd, cwd=BASE)


def banner(text: str):
    w = 72
    print()
    print("=" * w)
    print(f"  {text}")
    print("=" * w)


def section(text: str):
    print(f"\n  ── {text}")


# Decision logic now lives in policy/policy_engine.py (imported above).
# decide_switch(blueprint, logs_result, current_mode) → mode | None
# should_stop(logs_result, post_switch_polls) → bool


# ---------------------------------------------------------------------------
# Single log pipeline
# ---------------------------------------------------------------------------

def run_log(log_id: str, intensity: int, logs_wait: int, keep_running: bool) -> dict:
    log_path = str(LOGS_DIR / f"{log_id}.json")
    session_id = f"hp_{log_id}"

    result = {
        "log_id": log_id,
        "session_id": session_id,
        "classify_ok": False,
        "deploy_ok": False,
        "blueprint": None,
        "behavior_switches": [],
        "events_total": 0,
        "engagement_score": 0,
        "report_ok": False,
        "steps": 0,
        "error": None,
    }

    banner(f"LOG: {log_id}  |  intensity={intensity}")

    try:
        # ── Classify ────────────────────────────────────────────────────────
        section("Classify")
        clf = mgr("classify", "--log", log_path)
        bp = clf["suggested_blueprint"]
        conf = clf["confidence"]
        print(f"    attack_type={clf['attack_type']}  confidence={conf}  blueprint={bp}")
        result["classify_ok"] = True
        result["blueprint"] = bp

        # ── Deploy ──────────────────────────────────────────────────────────
        section("Deploy")
        dep = mgr("deploy", "--blueprint", bp, "--session", session_id)
        print(f"    container_id={dep['container_id']}  status={dep['status']}  ports={dep['ports']}")
        result["deploy_ok"] = True
        current_mode = "default"

        if bp == "monitor_only":
            print("    [monitor_only] No simulation, no switches. Polling once.")
            time.sleep(3)
            lr = mgr("logs", "--session", session_id)
            result["steps"] = lr["step_count"]
            section("Report")
            rpt = mgr("report", "--session", session_id)
            print(f"    report → {rpt['report_path']}")
            result["report_ok"] = True
            if not keep_running:
                mgr("stop", "--session", session_id)
                print("    [stopped]")
            return result

        # ── Simulate (background thread) ────────────────────────────────────
        section(f"Simulate (intensity={intensity})")
        print(f"    Launching simulator in background, then polling logs every {logs_wait}s")
        sim_done = threading.Event()

        def _sim():
            run_sim(log_path, session_id, intensity)
            sim_done.set()

        sim_thread = threading.Thread(target=_sim, daemon=True)
        sim_thread.start()

        # ── Monitor loop ─────────────────────────────────────────────────────
        section("Monitor loop")
        post_switch_polls = 0
        switched_modes = set()

        while True:
            time.sleep(logs_wait)
            lr = mgr("logs", "--session", session_id)
            step = lr["step_count"]
            score = lr["engagement_score"]
            new_ev = len(lr["new_events"])
            print(f"    step={step}  score={score}  new_events={new_ev}  mode={current_mode}")

            # Behavior switch decision — via policy_engine (single source of truth)
            switch_to = decide_switch(bp, lr, current_mode)

            if switch_to and switch_to not in switched_modes:
                section(f"Behavior switch → {switch_to}")
                sw = mgr("behavior", "--session", session_id, "--mode", switch_to)
                print(f"    files_written={len(sw['files_written'])}: {sw['files_written'][:2]}")
                current_mode = switch_to
                switched_modes.add(switch_to)
                result["behavior_switches"].append(switch_to)
                post_switch_polls = 0
            elif switch_to:
                post_switch_polls += 1
            else:
                if current_mode != "default":
                    post_switch_polls += 1

            result["steps"] = step
            result["events_total"] = lr["total_events"]
            result["engagement_score"] = score

            if should_stop(lr, post_switch_polls) and sim_done.is_set():
                print(f"    [exit] step={step} score={score} post_switch_polls={post_switch_polls}")
                break

            if not sim_done.is_set():
                print(f"    [sim still running...]")

        # Wait for sim to finish if it hasn't
        sim_thread.join(timeout=10)

        # ── Report ───────────────────────────────────────────────────────────
        section("Report")
        rpt = mgr("report", "--session", session_id)
        print(f"    → {rpt['report_path']}")
        print(f"    score={rpt['engagement_score']}  events={rpt['total_events']}  switches={rpt['behavior_switches']}")
        result["report_ok"] = True

        # ── Stop ─────────────────────────────────────────────────────────────
        if not keep_running:
            mgr("stop", "--session", session_id)
            print("    [container stopped]")

    except RuntimeError as e:
        print(f"    ERROR: {e}")
        result["error"] = str(e)
        # Try to stop orphaned container
        try:
            mgr("stop", "--session", session_id)
        except Exception:
            pass

    return result


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

def print_summary(results: list[dict]):
    banner("RESULTS SUMMARY")

    cols = [
        ("Log ID",        "log_id",            12),
        ("Blueprint",     "blueprint",          16),
        ("Classify",      "classify_ok",         8),
        ("Deploy",        "deploy_ok",           7),
        ("Switches",      "behavior_switches",  30),
        ("Events",        "events_total",        7),
        ("Score",         "engagement_score",    6),
        ("Report",        "report_ok",           7),
        ("Steps",         "steps",               5),
    ]

    header = "  ".join(f"{h:<{w}}" for h, _, w in cols)
    sep    = "  ".join("-" * w for _, _, w in cols)
    print(header)
    print(sep)

    for r in results:
        def fmt(k, w):
            v = r.get(k)
            if isinstance(v, bool):
                return ("✓" if v else "✗").ljust(w)
            if isinstance(v, list):
                return (", ".join(v) or "—").ljust(w)
            return str(v if v is not None else "—").ljust(w)

        row = "  ".join(fmt(k, w) for _, k, w in cols)
        print(row)

    print()
    total = len(results)
    if total == 0:
        return
    classify_acc = sum(1 for r in results if r["classify_ok"]) / total
    deploy_acc   = sum(1 for r in results if r["deploy_ok"]) / total
    report_acc   = sum(1 for r in results if r["report_ok"]) / total
    switch_sess  = sum(1 for r in results if r["behavior_switches"])
    avg_score    = sum(r["engagement_score"] for r in results) / total
    avg_steps    = sum(r["steps"] for r in results) / total
    avg_events   = sum(r["events_total"] for r in results) / total

    print(f"  Classification success : {classify_acc*100:.0f}%")
    print(f"  Deploy success         : {deploy_acc*100:.0f}%")
    print(f"  Report success         : {report_acc*100:.0f}%")
    print(f"  Sessions with switches : {switch_sess}/{total}")
    print(f"  Avg engagement score   : {avg_score:.1f}")
    print(f"  Avg steps per session  : {avg_steps:.1f}")
    print(f"  Avg events per session : {avg_events:.1f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

ALL_LOGS = [
    "ssh_001", "ssh_002", "ssh_003", "ssh_004",
    "web_001", "web_002", "web_003", "web_004",
    "unknown_001", "unknown_002",
]


def main():
    parser = argparse.ArgumentParser(prog="run_intensive_test.py")
    parser.add_argument("--intensity", type=int, default=2, choices=[1, 2, 3])
    parser.add_argument("--log", help="Run a single log only (e.g. ssh_001)")
    parser.add_argument("--logs-wait", type=int, default=15,
                        help="Seconds between log polls (default: 15)")
    parser.add_argument("--no-stop", action="store_true",
                        help="Keep containers running after test")
    args = parser.parse_args()

    target_logs = [args.log] if args.log else ALL_LOGS

    # Clean up any leftover sessions from previous runs
    for log_id in target_logs:
        session_dir = BASE / "running" / f"hp_{log_id}"
        if session_dir.exists():
            print(f"[setup] Removing leftover session: hp_{log_id}")
            import shutil
            shutil.rmtree(session_dir)

    banner(f"INTENSIVE TEST  |  logs={len(target_logs)}  intensity={args.intensity}  poll_interval={args.logs_wait}s")
    print(f"  Logs: {target_logs}")

    results = []
    for log_id in target_logs:
        r = run_log(log_id, args.intensity, args.logs_wait, args.no_stop)
        results.append(r)
        # Brief pause between sessions to let Docker ports free up
        if log_id != target_logs[-1]:
            print("\n  [pause 3s before next session]")
            time.sleep(3)

    print_summary(results)


if __name__ == "__main__":
    main()
