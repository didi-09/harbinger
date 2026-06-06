#!/usr/bin/env python3
"""
session_continuity.py — Prove that runtime switching does not drop attacker sessions  (#4).

For each trial:
  1. Deploy an SSH or web honeypot
  2. Open a persistent connection (paramiko SSH channel / requests.Session)
  3. Trigger a behavior switch via honeypot_manager behavior
  4. Assert on the SAME connection:
       - socket still alive
       - SSH channel still executable (runs a command) / HTTP session still responds
       - new decoy file is now visible (cat / GET)
  5. Record: preserved | dropped | decoy_visible | connection_id

Usage:
  python3 experiments/session_continuity.py --n 20 [--blueprint ssh|web]

Output:
  results/session_continuity.csv
"""

import argparse
import csv
import json
import shutil
import socket
import subprocess
import sys
import time
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


def run_ssh_trial(trial_id: int, session_id: str) -> dict:
    """Open persistent SSH channel, trigger switch, assert continuity."""
    try:
        import paramiko
    except ImportError:
        return {"trial": trial_id, "blueprint": "ssh", "error": "paramiko missing"}

    rec = {
        "trial": trial_id,
        "blueprint": "ssh",
        "session_id": session_id,
        "connection_preserved": False,
        "channel_still_executes": False,
        "decoy_visible_after_switch": False,
        "session_id_preserved": None,
        "switch_latency_ms": None,
        "error": None,
    }

    try:
        dep = mgr("deploy", "--blueprint", "ssh_bruteforce", "--session", session_id)
        host_ports = dep.get("host_ports", {})
        ssh_port = int(host_ports.get("22", 2222))

        print(f"  [ssh-{trial_id}] deployed  port={ssh_port}")
        if not wait_port("localhost", ssh_port, timeout=60):
            rec["error"] = "Cowrie did not start in 60s"
            return rec
        time.sleep(4)  # let Cowrie finish writing SSH banner after port opens

        # Open persistent SSH connection using invoke_shell — Cowrie requires
        # interactive shell channels; exec_command channels are rejected
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            "localhost", port=ssh_port,
            username="root", password="password",
            timeout=8, banner_timeout=12, auth_timeout=8,
            look_for_keys=False, allow_agent=False
        )
        transport = client.get_transport()
        rec["session_id_preserved"] = str(id(transport))

        shell = client.invoke_shell()
        time.sleep(1.0)
        shell.recv(4096)  # drain banner / prompt

        shell.send("id\n")
        time.sleep(0.8)
        out_before = shell.recv(1024).decode(errors="replace").strip()
        print(f"  [ssh-{trial_id}] connected  pre-switch id={out_before!r}")

        # Trigger behavior switch mid-connection
        sw = mgr("behavior", "--session", session_id, "--mode", "expose_fake_backup")
        rec["switch_latency_ms"] = sw.get("latency", {}).get("total_ms")
        time.sleep(0.5)

        # Assert same shell is still alive after switch
        rec["connection_preserved"] = (
            transport.is_active() and not shell.closed
        )

        if rec["connection_preserved"]:
            shell.send("ls /home/admin\n")
            time.sleep(0.8)
            out_after = shell.recv(1024).decode(errors="replace").strip()
            rec["channel_still_executes"] = bool(out_after)
            print(f"  [ssh-{trial_id}] post-switch ls={out_after!r}")

            shell.send("test -f /home/admin/credentials.txt && echo YES || echo NO\n")
            time.sleep(0.8)
            vis_raw = shell.recv(1024).decode(errors="replace")
            rec["decoy_visible_after_switch"] = ("YES" in vis_raw)
            print(f"  [ssh-{trial_id}] decoy visible={'YES' if rec['decoy_visible_after_switch'] else 'NO'}")

        shell.close()
        client.close()

    except Exception as e:
        rec["error"] = str(e)[:200]
        print(f"  [ssh-{trial_id}] ERROR: {e}")
    finally:
        try:
            mgr("stop", "--session", session_id)
        except Exception:
            pass
        sess_dir = BASE / "running" / session_id
        if sess_dir.exists():
            shutil.rmtree(sess_dir, ignore_errors=True)

    return rec


def run_web_trial(trial_id: int, session_id: str) -> dict:
    """Open persistent HTTP session, trigger switch, assert continuity."""
    try:
        import requests
        from requests.exceptions import RequestException
    except ImportError:
        return {"trial": trial_id, "blueprint": "web", "error": "requests missing"}

    rec = {
        "trial": trial_id,
        "blueprint": "web",
        "session_id": session_id,
        "connection_preserved": False,
        "channel_still_executes": False,
        "decoy_visible_after_switch": False,
        "session_id_preserved": None,
        "switch_latency_ms": None,
        "error": None,
    }

    try:
        dep = mgr("deploy", "--blueprint", "web_attack", "--session", session_id)
        host_ports = dep.get("host_ports", {})
        web_port = int(host_ports.get("80", 8080))

        print(f"  [web-{trial_id}] deployed  port={web_port}")
        if not wait_port("localhost", web_port, timeout=25):
            rec["error"] = "Flask did not start in 25s"
            return rec
        time.sleep(3)  # let Flask finish startup after port opens

        base_url = f"http://localhost:{web_port}"
        sess = requests.Session()
        sess.headers["User-Agent"] = "continuity-test/1.0"
        r = sess.get(base_url + "/admin", timeout=5)
        print(f"  [web-{trial_id}] pre-switch GET /admin → {r.status_code}")

        # Record session cookie as "session_id"
        rec["session_id_preserved"] = str(dict(sess.cookies))

        # Trigger switch
        t0 = time.perf_counter()
        sw = mgr("behavior", "--session", session_id, "--mode", "expose_fake_config")
        rec["switch_latency_ms"] = sw.get("latency", {}).get("total_ms")

        # Assert same HTTP session still works
        try:
            r2 = sess.get(base_url + "/admin", timeout=5)
            rec["connection_preserved"] = True
            rec["channel_still_executes"] = (r2.status_code in (200, 401, 403, 404))
            print(f"  [web-{trial_id}] post-switch GET /admin → {r2.status_code}")
        except RequestException as e:
            rec["connection_preserved"] = False
            rec["error"] = f"POST-SWITCH request failed: {e}"

        # Check decoy file visible
        try:
            r3 = sess.get(base_url + "/.env", timeout=5)
            rec["decoy_visible_after_switch"] = (r3.status_code == 200 and len(r3.text) > 10)
            print(f"  [web-{trial_id}] /.env → {r3.status_code}  visible={rec['decoy_visible_after_switch']}")
        except RequestException:
            rec["decoy_visible_after_switch"] = False

    except Exception as e:
        rec["error"] = str(e)[:200]
        print(f"  [web-{trial_id}] ERROR: {e}")
    finally:
        try:
            mgr("stop", "--session", session_id)
        except Exception:
            pass
        sess_dir = BASE / "running" / session_id
        if sess_dir.exists():
            shutil.rmtree(sess_dir, ignore_errors=True)

    return rec


def main():
    parser = argparse.ArgumentParser(prog="session_continuity.py")
    parser.add_argument("--n", type=int, default=20, help="Number of trials per blueprint")
    parser.add_argument("--blueprint", choices=["ssh", "web", "both"], default="both")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    all_rows = []

    blueprints = []
    if args.blueprint in ("ssh", "both"):
        blueprints.append("ssh")
    if args.blueprint in ("web", "both"):
        blueprints.append("web")

    for bp in blueprints:
        print(f"\n{'='*60}")
        print(f"Session continuity: blueprint={bp}  n={args.n}")
        print("="*60)
        for i in range(1, args.n + 1):
            session_id = f"cont_{bp}_{i:03d}"
            # Ensure clean
            sess_dir = BASE / "running" / session_id
            if sess_dir.exists():
                shutil.rmtree(sess_dir, ignore_errors=True)

            print(f"\n  Trial {i}/{args.n}:", end=" ")
            if bp == "ssh":
                row = run_ssh_trial(i, session_id)
            else:
                row = run_web_trial(i, session_id)
            row["ts"] = datetime.now(timezone.utc).isoformat()
            all_rows.append(row)
            time.sleep(1)

    # Write CSV
    if all_rows:
        out_path = RESULTS_DIR / "session_continuity.csv"
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\nResults written: {out_path}")

    # Summary
    print(f"\n{'='*60}")
    print("SESSION CONTINUITY SUMMARY")
    print("="*60)
    for bp in blueprints:
        rows = [r for r in all_rows if r["blueprint"] == bp]
        total = len(rows)
        if total == 0:
            continue
        preserved = sum(1 for r in rows if r["connection_preserved"])
        executes = sum(1 for r in rows if r["channel_still_executes"])
        decoy_vis = sum(1 for r in rows if r["decoy_visible_after_switch"])
        errors = sum(1 for r in rows if r.get("error"))
        lats = [r["switch_latency_ms"] for r in rows
                if r.get("switch_latency_ms") is not None]
        avg_lat = sum(lats) / len(lats) if lats else None
        print(f"\n  Blueprint: {bp}  (n={total})")
        print(f"    Connection preserved  : {preserved}/{total}"
              f"  ({100*preserved//total}%)")
        print(f"    Channel still executes: {executes}/{total}")
        print(f"    Decoy visible after   : {decoy_vis}/{total}")
        print(f"    Errors                : {errors}/{total}")
        if avg_lat is not None:
            print(f"    Avg switch latency    : {avg_lat:.1f} ms")


if __name__ == "__main__":
    main()
