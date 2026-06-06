#!/usr/bin/env python3
"""
run_attacks.py — Drive the full expanded dataset of real-tool attack sessions  (#1, #15).

Usage:
  python3 attacks/run_attacks.py [--category <cat>] [--id <id>] [--skip-optional]
                                  [--logs-wait <s>] [--no-stop] [--dry-run]

Options:
  --category     Only run entries matching this category (e.g. ssh_brute_force)
  --id           Run a single catalog entry by id
  --skip-optional  Skip entries with optional: true (Metasploit modules)
  --logs-wait    Seconds between log polls (default: 10)
  --no-stop      Keep containers running after each session
  --dry-run      Print what would run without executing

Each session:
  1. Classifies a synthetic seed log built from the catalog entry
  2. Deploys the target_blueprint with a dynamic host port
  3. Runs the real attack tool against the allocated port
  4. Drives the monitor loop via policy_engine (same as run_intensive_test.py)
  5. Generates a report and stops the container
  6. Appends result to attack_logs/ground_truth.json
  7. Writes a row to results/dataset_manifest.csv

Run times: SSH brute ~90s/session; web enum ~120s/session; post-exploit ~180s/session.
Full catalog (non-optional): ~55 sessions × ~2 min avg ≈ 110 min total.
"""

import argparse
import csv
import json
import os
import shlex
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

BASE = Path(__file__).parent.parent.resolve()
CATALOG_PATH = Path(__file__).parent / "catalog.yaml"
MANAGER = str(BASE / "honeypot_manager.py")
RESULTS_DIR = BASE / "results"

sys.path.insert(0, str(BASE))
from policy.policy_engine import decide_switch, should_stop  # noqa: E402


def mgr(*args) -> dict:
    cmd = ["python3", MANAGER] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[:400])
    return json.loads(result.stdout)


def banner(text: str):
    w = 72
    print(f"\n{'=' * w}\n  {text}\n{'=' * w}")


def run_tool(command: str, timeout_s: int, dry_run: bool) -> bool:
    """Run the attack tool command string. Returns True on success."""
    if dry_run:
        print(f"  [dry-run] would execute: {command}")
        return True
    print(f"  [tool] {command}")
    try:
        subprocess.run(
            command, shell=True, timeout=timeout_s,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        return True
    except subprocess.TimeoutExpired:
        print(f"  [tool] timed out after {timeout_s}s")
        return False
    except Exception as e:
        print(f"  [tool] error: {e}")
        return False


def build_seed_log(entry: dict, host_port: str | None) -> dict:
    """
    Build a minimal attack log dict that classify() can score.
    This is used to produce the classification input — real event capture
    happens in the running container's logs.
    """
    cat = entry["category"]
    port_map = {
        "ssh_brute_force": 22, "ssh_post_exploitation": 22,
        "vulnerability_scan": entry.get("port_key") == "ssh" and 22 or 80,
        "web_enumeration": 80, "web_exploitation": 80, "credential_attack": 80,
        "bot_activity": 80, "unknown": 445,
    }
    dest_port = port_map.get(cat, 22)

    events_by_cat = {
        "ssh_brute_force":       ["Failed password for root from 10.0.0.1 port 1234 ssh2",
                                   "Failed password for admin from 10.0.0.1 port 1235 ssh2",
                                   "Invalid user backup from 10.0.0.1 port 1236"],
        "ssh_post_exploitation": ["Failed password for root from 10.0.0.1 port 1234 ssh2",
                                   "Accepted password for backup from 10.0.0.1 port 1237 ssh2"],
        "web_enumeration":       ["GET /admin HTTP/1.1 404", "GET /.env HTTP/1.1 404",
                                   "GET /backup HTTP/1.1 404", "POST /login HTTP/1.1 401"],
        "web_exploitation":      ["POST /login HTTP/1.1 401", "GET /admin HTTP/1.1 403",
                                   "POST /admin HTTP/1.1 403"],
        "credential_attack":     ["POST /login HTTP/1.1 401", "POST /login HTTP/1.1 401",
                                   "POST /login HTTP/1.1 401"],
        "bot_activity":          ["GET /admin HTTP/1.1 404", "POST /login HTTP/1.1 401",
                                   "GET /.env HTTP/1.1 404"],
        "vulnerability_scan":    ["GET /admin HTTP/1.1 404"] if dest_port == 80 else
                                  ["Failed password for root from 10.0.0.1 port 1234 ssh2"],
        "unknown":               ["SMB connection attempt", "NTLM authentication request"],
    }

    return {
        "id": entry["id"],
        "source_ip": "127.0.0.1",
        "destination_port": dest_port,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "events": events_by_cat.get(cat, ["connection attempt"]),
    }


def run_session(entry: dict, logs_wait: int, keep_running: bool,
                dry_run: bool) -> dict:
    entry_id = entry["id"]
    session_id = f"hp_{entry_id}"
    target_bp = entry.get("target_blueprint", "monitor_only")
    port_key = entry.get("port_key")
    timeout_s = entry.get("timeout_s", 120)

    result = {
        "id": entry_id,
        "session_id": session_id,
        "category": entry.get("category", ""),
        "tool": entry.get("tool", ""),
        "expected_blueprint": entry.get("expected_blueprint", ""),
        "expected_modes": entry.get("expected_modes", []),
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

    banner(f"SESSION: {entry_id}  [{entry.get('category','')}]  tool={entry.get('tool','')}")
    print(f"  {entry.get('notes','')}")

    # Clean up any leftover session dir
    session_dir = BASE / "running" / session_id
    if session_dir.exists():
        print(f"  [setup] removing leftover session: {session_id}")
        shutil.rmtree(session_dir)

    try:
        # ── Classify ────────────────────────────────────────────────────────
        seed_log = build_seed_log(entry, None)
        seed_path = BASE / "results" / f"_seed_{entry_id}.json"
        RESULTS_DIR.mkdir(exist_ok=True)
        seed_path.write_text(json.dumps(seed_log))

        clf = mgr("classify", "--log", str(seed_path))
        bp = clf["suggested_blueprint"]
        print(f"  classify → blueprint={bp}  confidence={clf['confidence']}")
        result["classify_ok"] = True
        result["blueprint"] = bp

        # Override to target_blueprint if specified (policy decides classify;
        # we still deploy the intended blueprint for the test)
        deploy_bp = target_bp if target_bp != "monitor_only" else bp

        # ── Deploy ──────────────────────────────────────────────────────────
        dep = mgr("deploy", "--blueprint", deploy_bp, "--session", session_id)
        host_ports = dep.get("host_ports", {})
        print(f"  deploy  → blueprint={deploy_bp}  ports={host_ports}")
        result["deploy_ok"] = True
        current_mode = "default"

        if deploy_bp == "monitor_only" or not port_key:
            # No tool traffic, just poll once
            time.sleep(2)
            mgr("logs", "--session", session_id)
            rpt = mgr("report", "--session", session_id)
            result["report_ok"] = True
            result["steps"] = 1
            if not keep_running and not dry_run:
                mgr("stop", "--session", session_id)
            seed_path.unlink(missing_ok=True)
            return result

        # Determine which host port the tool should target
        if port_key == "ssh":
            allocated_port = host_ports.get("22", "2222")
        else:
            allocated_port = host_ports.get("80", "8080")

        # Substitute {host}/{port}/{wordlist}/{dirlist}/{smalllist} into command
        wl_base = BASE / "attacks" / "wordlists"
        cmd = entry["command"].format(
            host="localhost",
            port=allocated_port,
            wordlist="/usr/share/wordlists/rockyou.txt",
            dirlist="/usr/share/wordlists/dirb/common.txt",
            smalllist=str(wl_base / "top100_passwords.txt"),
        )

        # ── Simulate (background) ───────────────────────────────────────────
        sim_done = threading.Event()

        def _sim():
            # Brief startup delay to let container fully initialize
            time.sleep(4)
            run_tool(cmd, timeout_s, dry_run)
            sim_done.set()

        sim_thread = threading.Thread(target=_sim, daemon=True)
        sim_thread.start()

        # ── Monitor loop ─────────────────────────────────────────────────────
        post_switch_polls = 0
        switched_modes: set = set()

        while True:
            time.sleep(logs_wait)
            lr = mgr("logs", "--session", session_id)
            step = lr["step_count"]
            score = lr["engagement_score"]
            new_ev = len(lr["new_events"])
            mode = current_mode
            print(f"  step={step}  score={score}  new_events={new_ev}  mode={mode}")

            switch_to = decide_switch(deploy_bp, lr, current_mode)
            if switch_to and switch_to not in switched_modes:
                print(f"  → switching to {switch_to}")
                sw = mgr("behavior", "--session", session_id, "--mode", switch_to)
                lat = sw.get("latency", {})
                print(f"    latency: template={lat.get('template_build_ms')}ms  "
                      f"sync={lat.get('volume_sync_ms')}ms  total={lat.get('total_ms')}ms")
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
                break
            if not sim_done.is_set():
                print(f"  [tool still running...]")

        sim_thread.join(timeout=5)

        # ── Report ───────────────────────────────────────────────────────────
        rpt = mgr("report", "--session", session_id)
        print(f"  report → score={rpt['engagement_score']}  "
              f"events={rpt['total_events']}  switches={rpt['behavior_switches']}")
        result["report_ok"] = True

        if not keep_running and not dry_run:
            mgr("stop", "--session", session_id)
            print("  [stopped]")

    except RuntimeError as e:
        print(f"  ERROR: {e}")
        result["error"] = str(e)
        try:
            mgr("stop", "--session", session_id)
        except Exception:
            pass
    finally:
        seed_path = BASE / "results" / f"_seed_{entry_id}.json"
        seed_path.unlink(missing_ok=True)

    return result


def update_ground_truth(entry: dict, run_result: dict):
    gt_path = BASE / "attack_logs" / "ground_truth.json"
    try:
        with open(gt_path) as f:
            gt = json.load(f)
    except Exception:
        gt = {}

    gt[entry["id"]] = {
        "attack_type": {"ssh_bruteforce": "SSH Brute Force",
                        "web_attack": "Web Attack"}.get(
            run_result.get("blueprint", ""), "Unknown"),
        "blueprint": run_result.get("blueprint") or entry.get("expected_blueprint"),
        "expected_behavior_switches": entry.get("expected_modes", []),
        "notes": entry.get("notes", ""),
        "category": entry.get("category", ""),
        "tool": entry.get("tool", ""),
    }

    with open(gt_path, "w") as f:
        json.dump(gt, f, indent=2)


def append_manifest_row(row: dict):
    manifest_path = RESULTS_DIR / "dataset_manifest.csv"
    RESULTS_DIR.mkdir(exist_ok=True)
    write_header = not manifest_path.exists()
    with open(manifest_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(prog="run_attacks.py")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--id", dest="entry_id", help="Run a single entry by id")
    parser.add_argument("--skip-optional", action="store_true", default=True,
                        help="Skip optional (heavy) Metasploit entries (default: True)")
    parser.add_argument("--include-optional", action="store_true",
                        help="Include optional Metasploit entries")
    parser.add_argument("--logs-wait", type=int, default=10)
    parser.add_argument("--no-stop", action="store_true")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print commands without executing")
    args = parser.parse_args()

    with open(CATALOG_PATH) as f:
        catalog = yaml.safe_load(f)

    # Filter
    entries = catalog
    if args.entry_id:
        entries = [e for e in entries if e["id"] == args.entry_id]
    if args.category:
        entries = [e for e in entries if e.get("category") == args.category]
    if not args.include_optional:
        entries = [e for e in entries if not e.get("optional")]

    print(f"\nDataset run: {len(entries)} sessions  "
          f"(logs_wait={args.logs_wait}s  dry_run={args.dry_run})")
    print("  IDs:", [e["id"] for e in entries[:10]],
          "..." if len(entries) > 10 else "")

    all_results = []
    for i, entry in enumerate(entries, 1):
        print(f"\n[{i}/{len(entries)}]", end=" ")
        r = run_session(entry, args.logs_wait, args.no_stop, args.dry_run)
        all_results.append(r)
        update_ground_truth(entry, r)
        append_manifest_row({
            "id": r["id"],
            "category": r["category"],
            "tool": r["tool"],
            "blueprint": r["blueprint"] or "",
            "expected_blueprint": entry.get("expected_blueprint", ""),
            "blueprint_correct": r["blueprint"] == entry.get("expected_blueprint"),
            "switches": ",".join(r["behavior_switches"]),
            "events_total": r["events_total"],
            "engagement_score": r["engagement_score"],
            "steps": r["steps"],
            "report_ok": r["report_ok"],
            "error": r["error"] or "",
        })
        if i < len(entries):
            time.sleep(2)

    # Summary
    total = len(all_results)
    if total:
        classify_ok = sum(1 for r in all_results if r["classify_ok"])
        deploy_ok = sum(1 for r in all_results if r["deploy_ok"])
        report_ok = sum(1 for r in all_results if r["report_ok"])
        switched = sum(1 for r in all_results if r["behavior_switches"])
        print(f"\n{'='*60}")
        print(f"Dataset complete: {total} sessions")
        print(f"  Classify OK : {classify_ok}/{total}")
        print(f"  Deploy OK   : {deploy_ok}/{total}")
        print(f"  Report OK   : {report_ok}/{total}")
        print(f"  Switched    : {switched}/{total}")
        print(f"  Results: results/dataset_manifest.csv")
        print(f"  Ground truth: attack_logs/ground_truth.json (updated)")


if __name__ == "__main__":
    main()
