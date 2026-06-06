#!/usr/bin/env python3
"""
volume_sync.py — Measure Docker volume propagation latency (#7).

Three measurements per switch:
  t1: host_write       — time for _write_behavior_files to complete (from switch_metrics.json)
  t2: container_visible — time until container sees the file (from switch_metrics.json volume_sync_ms)
  t3: attacker_observable — time until attacker's connection can read the file (measured here)

Reports mean / p50 / p95 / max for each stage.

Usage:
  python3 experiments/volume_sync.py --switches 50 [--blueprint ssh|web]

Output:
  results/volume_sync_latency.csv
"""

import argparse
import csv
import json
import shutil
import socket
import subprocess
import sys
import time
import statistics
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent.resolve()
MANAGER = str(BASE / "honeypot_manager.py")
RESULTS_DIR = BASE / "results"

sys.path.insert(0, str(BASE))


def mgr(*args) -> dict:
    cmd = ["python3", MANAGER] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[:400])
    return json.loads(result.stdout)


def wait_port(host: str, port: int, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            s = socket.create_connection((host, port), timeout=1)
            s.close()
            return True
        except (ConnectionRefusedError, OSError):
            time.sleep(1)
    return False


def measure_attacker_observable_ssh(session_id: str, ssh_port: int,
                                     decoy_path: str = "/home/admin/credentials.txt",
                                     timeout_s: float = 5.0) -> float:
    """
    Time from NOW until an SSH connection can read the decoy file.
    Returns latency in ms, or -1 on failure.
    """
    try:
        import paramiko
    except ImportError:
        return -1.0

    t0 = time.perf_counter()
    deadline = t0 + timeout_s
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            "localhost", port=ssh_port,
            username="root", password="password",
            timeout=5, banner_timeout=8, auth_timeout=5,
            look_for_keys=False, allow_agent=False
        )
        while time.perf_counter() < deadline:
            ch = client.get_transport().open_session()
            ch.exec_command(f"cat {decoy_path} 2>/dev/null | head -1")
            time.sleep(0.1)
            out = ch.recv(256).decode(errors="replace").strip()
            ch.close()
            if out:
                return (time.perf_counter() - t0) * 1000.0
            time.sleep(0.05)
    except Exception:
        pass
    finally:
        try:
            client.close()
        except Exception:
            pass
    return -1.0


def measure_attacker_observable_web(web_port: int, path: str = "/.env",
                                     timeout_s: float = 5.0) -> float:
    """
    Time from NOW until an HTTP request returns the decoy file content.
    Returns latency in ms, or -1 on failure.
    """
    try:
        import requests
        from requests.exceptions import RequestException
    except ImportError:
        return -1.0

    t0 = time.perf_counter()
    deadline = t0 + timeout_s
    base_url = f"http://localhost:{web_port}"
    while time.perf_counter() < deadline:
        try:
            r = requests.get(base_url + path, timeout=2)
            if r.status_code == 200 and len(r.text) > 10:
                return (time.perf_counter() - t0) * 1000.0
        except RequestException:
            pass
        time.sleep(0.05)
    return -1.0


def run_ssh_switch_trial(trial_id: int) -> dict | None:
    """Deploy SSH blueprint, trigger one switch, measure all three latency stages."""
    session_id = f"vsync_ssh_{trial_id:03d}"
    sess_dir = BASE / "running" / session_id
    if sess_dir.exists():
        shutil.rmtree(sess_dir)

    rec = {
        "trial": trial_id,
        "blueprint": "ssh",
        "switch": "expose_fake_backup",
        "template_build_ms": None,
        "volume_sync_ms": None,
        "attacker_observable_ms": None,
        "error": None,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

    try:
        dep = mgr("deploy", "--blueprint", "ssh_bruteforce", "--session", session_id)
        ssh_port = int(dep.get("host_ports", {}).get("22", 2222))

        if not wait_port("localhost", ssh_port, timeout=40):
            rec["error"] = "Cowrie did not start"
            return rec

        # Trigger switch and read latency from the JSON output
        sw = mgr("behavior", "--session", session_id, "--mode", "expose_fake_backup")
        lat = sw.get("latency", {})
        rec["template_build_ms"] = lat.get("template_build_ms")
        rec["volume_sync_ms"] = lat.get("volume_sync_ms")

        # Measure attacker-observable latency from scratch (file was already written;
        # this measures connection + cat round-trip after file is in volume)
        t_obs = measure_attacker_observable_ssh(session_id, ssh_port)
        rec["attacker_observable_ms"] = round(t_obs, 2) if t_obs >= 0 else None

        print(f"  trial={trial_id}  "
              f"template={rec['template_build_ms']}ms  "
              f"sync={rec['volume_sync_ms']}ms  "
              f"observable={rec['attacker_observable_ms']}ms")

    except Exception as e:
        rec["error"] = str(e)[:200]
        print(f"  trial={trial_id} ERROR: {e}")
    finally:
        try:
            mgr("stop", "--session", session_id)
        except Exception:
            pass
        if sess_dir.exists():
            shutil.rmtree(sess_dir, ignore_errors=True)

    return rec


def run_web_switch_trial(trial_id: int) -> dict | None:
    """Deploy web blueprint, trigger one switch, measure all three stages."""
    session_id = f"vsync_web_{trial_id:03d}"
    sess_dir = BASE / "running" / session_id
    if sess_dir.exists():
        shutil.rmtree(sess_dir)

    rec = {
        "trial": trial_id,
        "blueprint": "web",
        "switch": "expose_fake_config",
        "template_build_ms": None,
        "volume_sync_ms": None,
        "attacker_observable_ms": None,
        "error": None,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

    try:
        dep = mgr("deploy", "--blueprint", "web_attack", "--session", session_id)
        web_port = int(dep.get("host_ports", {}).get("80", 8080))

        if not wait_port("localhost", web_port, timeout=25):
            rec["error"] = "Flask did not start"
            return rec

        sw = mgr("behavior", "--session", session_id, "--mode", "expose_fake_config")
        lat = sw.get("latency", {})
        rec["template_build_ms"] = lat.get("template_build_ms")
        rec["volume_sync_ms"] = lat.get("volume_sync_ms")

        t_obs = measure_attacker_observable_web(web_port, "/.env")
        rec["attacker_observable_ms"] = round(t_obs, 2) if t_obs >= 0 else None

        print(f"  trial={trial_id}  "
              f"template={rec['template_build_ms']}ms  "
              f"sync={rec['volume_sync_ms']}ms  "
              f"observable={rec['attacker_observable_ms']}ms")

    except Exception as e:
        rec["error"] = str(e)[:200]
        print(f"  trial={trial_id} ERROR: {e}")
    finally:
        try:
            mgr("stop", "--session", session_id)
        except Exception:
            pass
        if sess_dir.exists():
            shutil.rmtree(sess_dir, ignore_errors=True)

    return rec


def stats(values: list[float]) -> dict:
    vals = [v for v in values if v is not None and v >= 0]
    if not vals:
        return {"n": 0, "mean": None, "p50": None, "p95": None, "max": None}
    vals.sort()
    n = len(vals)
    p50_idx = int(n * 0.50)
    p95_idx = int(n * 0.95)
    return {
        "n": n,
        "mean": round(statistics.mean(vals), 2),
        "p50": round(vals[p50_idx], 2),
        "p95": round(vals[min(p95_idx, n-1)], 2),
        "max": round(vals[-1], 2),
    }


def main():
    parser = argparse.ArgumentParser(prog="volume_sync.py")
    parser.add_argument("--switches", type=int, default=30,
                        help="Total switch trials to run (default: 30)")
    parser.add_argument("--blueprint", choices=["ssh", "web", "both"], default="both")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    all_rows = []

    per_bp = args.switches // 2 if args.blueprint == "both" else args.switches

    for bp in ["ssh", "web"]:
        if args.blueprint not in (bp, "both"):
            continue
        print(f"\n{'='*60}")
        print(f"Volume sync latency: blueprint={bp}  trials={per_bp}")
        print("="*60)
        for i in range(1, per_bp + 1):
            print(f"\n  [{i}/{per_bp}]", end=" ")
            if bp == "ssh":
                row = run_ssh_switch_trial(i)
            else:
                row = run_web_switch_trial(i)
            if row:
                all_rows.append(row)
            time.sleep(1)

    # Write CSV
    if all_rows:
        out_path = RESULTS_DIR / "volume_sync_latency.csv"
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\nResults written: {out_path}")

    # Print statistics table
    print(f"\n{'='*60}")
    print("VOLUME SYNC LATENCY STATISTICS (ms)")
    print("="*60)
    for bp in ["ssh", "web"]:
        rows = [r for r in all_rows if r["blueprint"] == bp]
        if not rows:
            continue
        print(f"\n  Blueprint: {bp}")
        for field in ["template_build_ms", "volume_sync_ms", "attacker_observable_ms"]:
            s = stats([r.get(field) for r in rows])
            print(f"    {field:<28} n={s['n']}  "
                  f"mean={s['mean']}  p50={s['p50']}  p95={s['p95']}  max={s['max']}")


if __name__ == "__main__":
    main()
