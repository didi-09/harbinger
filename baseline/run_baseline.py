#!/usr/bin/env python3
"""
run_baseline.py — Run the same attack catalog against STATIC honeypots  (#2).

A static honeypot has all decoy files pre-written at deploy time (--static flag).
cmd_behavior is a no-op; no adaptive switching occurs.  The asset inventory is
identical to the adaptive sessions — the only difference is no runtime switching.

Usage:
  python3 baseline/run_baseline.py [--category <cat>] [--id <id>]
                                    [--logs-wait <s>] [--no-stop]

Output:
  results/adaptive_vs_static.csv — side-by-side comparison per session.
  Session data under running/static_<id>/
"""

import argparse
import csv
import json
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

BASE = Path(__file__).parent.parent.resolve()
CATALOG_PATH = BASE / "attacks" / "catalog.yaml"
MANAGER = str(BASE / "honeypot_manager.py")
RESULTS_DIR = BASE / "results"

sys.path.insert(0, str(BASE))
from policy.policy_engine import should_stop  # noqa: E402


def mgr(*args) -> dict:
    cmd = ["python3", MANAGER] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[:400])
    return json.loads(result.stdout)


def run_tool(command: str, timeout_s: int) -> bool:
    try:
        subprocess.run(
            command, shell=True, timeout=timeout_s,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        return True
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def run_static_session(entry: dict, logs_wait: int, keep_running: bool) -> dict:
    entry_id = entry["id"]
    session_id = f"static_{entry_id}"
    target_bp = entry.get("target_blueprint", "monitor_only")
    port_key = entry.get("port_key")
    timeout_s = entry.get("timeout_s", 120)

    result = {
        "id": entry_id,
        "session_id": session_id,
        "category": entry.get("category", ""),
        "tool": entry.get("tool", ""),
        "blueprint": target_bp,
        "mode": "STATIC",
        "behavior_switches": 0,   # always 0 for static
        "events_total": 0,
        "engagement_score": 0,
        "decoys_accessed": 0,
        "steps": 0,
        "report_ok": False,
        "error": None,
    }

    print(f"\n[static] {entry_id}  blueprint={target_bp}  tool={entry.get('tool')}")

    session_dir = BASE / "running" / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)

    try:
        # Deploy with --static (pre-writes all decoys, no adaptive switching)
        deploy_bp = target_bp if target_bp != "monitor_only" else "monitor_only"
        if deploy_bp == "monitor_only" or not port_key:
            dep = mgr("deploy", "--blueprint", deploy_bp, "--session", session_id)
            time.sleep(2)
            mgr("logs", "--session", session_id)
            rpt = mgr("report", "--session", session_id)
            result["report_ok"] = True
            result["steps"] = 1
            if not keep_running:
                mgr("stop", "--session", session_id)
            return result

        dep = mgr("deploy", "--blueprint", deploy_bp, "--session", session_id,
                  "--static")
        host_ports = dep.get("host_ports", {})
        print(f"  ports={host_ports}  static={dep.get('static')}")

        if port_key == "ssh":
            allocated_port = host_ports.get("22", "2222")
        else:
            allocated_port = host_ports.get("80", "8080")

        wl_base = BASE / "attacks" / "wordlists"
        cmd = entry["command"].format(
            host="localhost",
            port=allocated_port,
            wordlist="/usr/share/wordlists/rockyou.txt",
            dirlist="/usr/share/wordlists/dirb/common.txt",
            smalllist=str(wl_base / "top100_passwords.txt"),
        )
        print(f"  cmd: {cmd}")

        sim_done = threading.Event()

        def _sim():
            time.sleep(4)
            run_tool(cmd, timeout_s)
            sim_done.set()

        sim_thread = threading.Thread(target=_sim, daemon=True)
        sim_thread.start()

        # Monitor loop — static; no switching logic, just count events
        post_switch_polls = 0
        while True:
            time.sleep(logs_wait)
            lr = mgr("logs", "--session", session_id)
            step = lr["step_count"]
            score = lr["engagement_score"]
            new_ev = len(lr["new_events"])
            print(f"  step={step}  score={score}  new_events={new_ev}")
            result["steps"] = step
            result["events_total"] = lr["total_events"]
            result["engagement_score"] = score
            if should_stop(lr, post_switch_polls) and sim_done.is_set():
                break
            if not sim_done.is_set():
                print(f"  [tool still running...]")
            post_switch_polls += 1

        sim_thread.join(timeout=5)

        rpt = mgr("report", "--session", session_id)
        result["report_ok"] = True

        # Count decoys actually accessed (file_read / file_download events)
        session_path = BASE / "running" / session_id / "session.json"
        with open(session_path) as f:
            sess = json.load(f)
        decoy_events = [e for e in sess.get("events_seen", [])
                        if e.get("type") in ("file_read", "file_download")]
        result["decoys_accessed"] = len(decoy_events)

        if not keep_running:
            mgr("stop", "--session", session_id)
            print("  [stopped]")

    except RuntimeError as e:
        print(f"  ERROR: {e}")
        result["error"] = str(e)
        try:
            mgr("stop", "--session", session_id)
        except Exception:
            pass

    return result


def load_adaptive_results() -> dict:
    """Load adaptive results from results/dataset_manifest.csv for comparison."""
    csv_path = RESULTS_DIR / "dataset_manifest.csv"
    if not csv_path.exists():
        return {}
    adaptive = {}
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            adaptive[row["id"]] = row
    return adaptive


def write_comparison(adaptive: dict, static_results: list):
    out_path = RESULTS_DIR / "adaptive_vs_static.csv"
    RESULTS_DIR.mkdir(exist_ok=True)

    fieldnames = [
        "id", "category", "tool",
        "adaptive_score", "static_score",
        "adaptive_events", "static_events",
        "adaptive_switches", "static_switches",
        "adaptive_steps", "static_steps",
        "score_delta", "events_delta",
    ]
    rows = []
    for r in static_results:
        eid = r["id"]
        a = adaptive.get(eid, {})
        a_score = int(a.get("engagement_score", 0) or 0)
        s_score = r["engagement_score"]
        a_events = int(a.get("events_total", 0) or 0)
        s_events = r["events_total"]
        rows.append({
            "id": eid,
            "category": r["category"],
            "tool": r["tool"],
            "adaptive_score": a_score,
            "static_score": s_score,
            "adaptive_events": a_events,
            "static_events": s_events,
            "adaptive_switches": a.get("switches", ""),
            "static_switches": 0,
            "adaptive_steps": int(a.get("steps", 0) or 0),
            "static_steps": r["steps"],
            "score_delta": a_score - s_score,
            "events_delta": a_events - s_events,
        })

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nComparison written: {out_path}")
    if rows:
        avg_adapt = sum(r["adaptive_score"] for r in rows) / len(rows)
        avg_static = sum(r["static_score"] for r in rows) / len(rows)
        avg_delta = sum(r["score_delta"] for r in rows) / len(rows)
        print(f"  Avg adaptive score : {avg_adapt:.1f}")
        print(f"  Avg static score   : {avg_static:.1f}")
        print(f"  Avg score delta    : {avg_delta:+.1f}  (adaptive - static)")


def main():
    parser = argparse.ArgumentParser(prog="run_baseline.py")
    parser.add_argument("--category")
    parser.add_argument("--id", dest="entry_id")
    parser.add_argument("--logs-wait", type=int, default=10)
    parser.add_argument("--no-stop", action="store_true")
    args = parser.parse_args()

    with open(CATALOG_PATH) as f:
        catalog = yaml.safe_load(f)

    entries = [e for e in catalog if not e.get("optional")]
    if args.entry_id:
        entries = [e for e in entries if e["id"] == args.entry_id]
    if args.category:
        entries = [e for e in entries if e.get("category") == args.category]

    print(f"\nBaseline run: {len(entries)} static sessions")

    static_results = []
    for i, entry in enumerate(entries, 1):
        print(f"\n[{i}/{len(entries)}]", end=" ")
        r = run_static_session(entry, args.logs_wait, args.no_stop)
        static_results.append(r)
        if i < len(entries):
            time.sleep(2)

    adaptive = load_adaptive_results()
    write_comparison(adaptive, static_results)


if __name__ == "__main__":
    main()
