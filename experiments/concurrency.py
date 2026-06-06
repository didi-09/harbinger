#!/usr/bin/env python3
"""
concurrency.py — Multi-attacker concurrent session scaling test  (#5).

For each concurrency level (default: 1, 5, 10, 20):
  - Spawn N sessions in parallel, each on a unique dynamic port
  - Run a lightweight attack tool against each (gobuster/hydra small list)
  - Measure: switch success rate, switch latency, container stability, throughput
  - Record resource usage via ResourceMonitor

Usage:
  python3 experiments/concurrency.py --levels 1,5,10,20 [--blueprint ssh|web]

Output:
  results/concurrency_scaling.csv
  results/resource_by_phase.csv  (appended)
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

BASE = Path(__file__).parent.parent.resolve()
MANAGER = str(BASE / "honeypot_manager.py")
RESULTS_DIR = BASE / "results"

sys.path.insert(0, str(BASE))
from policy.policy_engine import decide_switch, should_stop  # noqa: E402
from experiments.resource_monitor import ResourceMonitor  # noqa: E402


def mgr(*args) -> dict:
    cmd = ["python3", MANAGER] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[:400])
    return json.loads(result.stdout)


def run_single_session(session_id: str, blueprint: str, tool_cmd: str,
                        tool_timeout: int = 60,
                        logs_wait: int = 8) -> dict:
    """Run one concurrent session. Returns metrics dict."""
    rec = {
        "session_id": session_id,
        "blueprint": blueprint,
        "deploy_ok": False,
        "switch_triggered": False,
        "switch_success": False,
        "switch_latency_ms": None,
        "events_total": 0,
        "engagement_score": 0,
        "steps": 0,
        "container_crashed": False,
        "error": None,
    }

    sess_dir = BASE / "running" / session_id
    if sess_dir.exists():
        shutil.rmtree(sess_dir)

    try:
        dep = mgr("deploy", "--blueprint", blueprint, "--session", session_id)
        rec["deploy_ok"] = True
        host_ports = dep.get("host_ports", {})

        if blueprint == "ssh_bruteforce":
            port = host_ports.get("22", "2222")
        else:
            port = host_ports.get("80", "8080")

        wl_base = BASE / "attacks" / "wordlists"
        cmd = tool_cmd.format(
            host="localhost", port=port,
            smalllist=str(wl_base / "top100_passwords.txt"),
            dirlist="/usr/share/wordlists/dirb/common.txt",
        )

        # Run tool in background
        sim_done = threading.Event()

        def _sim():
            time.sleep(3)
            try:
                subprocess.run(
                    cmd, shell=True, timeout=tool_timeout,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )
            except Exception:
                pass
            sim_done.set()

        threading.Thread(target=_sim, daemon=True).start()

        # Monitor loop
        current_mode = "default"
        switched = False
        post_switch_polls = 0

        for _ in range(8):  # max 8 steps per session in concurrency test
            time.sleep(logs_wait)
            lr = mgr("logs", "--session", session_id)
            rec["steps"] = lr["step_count"]
            rec["events_total"] = lr["total_events"]
            rec["engagement_score"] = lr["engagement_score"]

            if not switched:
                switch_to = decide_switch(blueprint, lr, current_mode)
                if switch_to:
                    rec["switch_triggered"] = True
                    t0 = time.perf_counter()
                    try:
                        sw = mgr("behavior", "--session", session_id,
                                 "--mode", switch_to)
                        rec["switch_latency_ms"] = sw.get("latency", {}).get("total_ms")
                        rec["switch_success"] = True
                        current_mode = switch_to
                        switched = True
                    except RuntimeError as e:
                        rec["error"] = f"switch failed: {e}"

            if should_stop(lr, post_switch_polls) and sim_done.is_set():
                break
            if switched:
                post_switch_polls += 1

        mgr("stop", "--session", session_id)

        # Check if container is still listed (crash detection)
        ps = subprocess.run(
            ["docker", "ps", "-qf", f"name={session_id}"],
            capture_output=True, text=True
        )
        rec["container_crashed"] = (ps.stdout.strip() == "")

    except RuntimeError as e:
        rec["error"] = str(e)[:200]
    finally:
        try:
            mgr("stop", "--session", session_id)
        except Exception:
            pass
        if sess_dir.exists():
            shutil.rmtree(sess_dir, ignore_errors=True)

    return rec


def run_level(level: int, blueprint: str) -> dict:
    """Run `level` concurrent sessions and return aggregate metrics."""
    print(f"\n  Concurrency level: {level}  blueprint={blueprint}")
    ts = datetime.now(timezone.utc).isoformat()

    # Tool command per blueprint (lightweight for concurrency tests)
    if blueprint == "ssh_bruteforce":
        tool_cmd = ("hydra -l root -P {smalllist} -t 2 -s {port} "
                    "-o /dev/null ssh://{host} 2>/dev/null")
    else:
        tool_cmd = ("gobuster dir -u http://{host}:{port} -w {dirlist} "
                    "-q -t 5 --no-error 2>/dev/null")

    sessions = [f"conc_{blueprint[:3]}_{level:02d}_{i:02d}" for i in range(level)]
    results = [None] * level
    threads = []

    rm_label = f"concurrency_level_{level}"

    with ResourceMonitor(label=rm_label,
                         csv_path=str(RESULTS_DIR / "resource_by_phase.csv"),
                         interval=2.0) as rm:
        t_start = time.perf_counter()

        for i, sid in enumerate(sessions):
            def worker(idx, session_id):
                results[idx] = run_single_session(
                    session_id, blueprint, tool_cmd, tool_timeout=80
                )
            t = threading.Thread(target=worker, args=(i, sid), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        elapsed_s = time.perf_counter() - t_start
        res_summary = rm.summary()

    # Aggregate
    valid = [r for r in results if r is not None]
    deploy_ok = sum(1 for r in valid if r["deploy_ok"])
    switch_triggered = sum(1 for r in valid if r["switch_triggered"])
    switch_success = sum(1 for r in valid if r["switch_success"])
    crashes = sum(1 for r in valid if r["container_crashed"])
    lats = [r["switch_latency_ms"] for r in valid
            if r.get("switch_latency_ms") is not None]
    avg_lat = round(sum(lats) / len(lats), 2) if lats else None
    avg_score = round(sum(r["engagement_score"] for r in valid) / len(valid), 1) if valid else 0

    print(f"    deployed={deploy_ok}/{level}  "
          f"switched={switch_success}/{switch_triggered}  "
          f"crashes={crashes}  avg_switch_lat={avg_lat}ms  "
          f"elapsed={elapsed_s:.1f}s")

    return {
        "ts": ts,
        "blueprint": blueprint,
        "concurrency_level": level,
        "sessions_total": level,
        "deploy_ok": deploy_ok,
        "switch_triggered": switch_triggered,
        "switch_success": switch_success,
        "switch_success_rate_pct": round(100 * switch_success / max(switch_triggered, 1), 1),
        "container_crashes": crashes,
        "avg_switch_latency_ms": avg_lat,
        "avg_engagement_score": avg_score,
        "total_elapsed_s": round(elapsed_s, 1),
        "avg_host_cpu_pct": res_summary.get("avg_host_cpu_pct"),
        "max_host_cpu_pct": res_summary.get("max_host_cpu_pct"),
        "avg_host_mem_pct": res_summary.get("avg_host_mem_pct"),
        "max_containers": res_summary.get("max_containers"),
    }


def main():
    parser = argparse.ArgumentParser(prog="concurrency.py")
    parser.add_argument("--levels", default="1,5,10,20",
                        help="Comma-separated concurrency levels (default: 1,5,10,20)")
    parser.add_argument("--blueprint", choices=["ssh", "web", "both"], default="web",
                        help="Blueprint to test (default: web — faster startup than SSH/Cowrie)")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    levels = [int(x.strip()) for x in args.levels.split(",")]

    blueprints = []
    if args.blueprint in ("ssh", "both"):
        blueprints.append("ssh_bruteforce")
    if args.blueprint in ("web", "both"):
        blueprints.append("web_attack")

    all_rows = []
    for bp in blueprints:
        print(f"\n{'='*60}")
        print(f"Concurrency scaling test: blueprint={bp}")
        print("="*60)
        for level in levels:
            row = run_level(level, bp)
            all_rows.append(row)
            # Cool-down between levels
            time.sleep(5)

    # Write CSV
    if all_rows:
        out_path = RESULTS_DIR / "concurrency_scaling.csv"
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\nResults: {out_path}")

    # Print table
    print(f"\n{'='*60}")
    print("CONCURRENCY SCALING TABLE")
    print("="*60)
    hdr = f"{'Blueprint':<15} {'N':>4} {'DeployOK':>9} {'Switch%':>8} "
    hdr += f"{'AvgLat(ms)':>11} {'Crashes':>8} {'CPU%':>6} {'Mem%':>6}"
    print(hdr)
    print("-" * 70)
    for r in all_rows:
        print(f"{r['blueprint']:<15} {r['concurrency_level']:>4} "
              f"{r['deploy_ok']:>9} {r['switch_success_rate_pct']:>7}% "
              f"{str(r['avg_switch_latency_ms']):>11} {r['container_crashes']:>8} "
              f"{str(r['avg_host_cpu_pct']):>6} {str(r['avg_host_mem_pct']):>6}")


if __name__ == "__main__":
    main()
