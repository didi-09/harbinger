#!/usr/bin/env python3
"""
evaluate.py — Score OpenClaw's performance against ground truth  (#8, #14).

Extended from the original to support:
  - All sessions in ground_truth.json (including real-tool sessions)
  - Artifact assertions: verify expected decoy files exist in honeyfs  (#8)
  - Switch confusion matrix: correct / false-positive / wrong / missed  (#14)
  - Machine-readable output to results/evaluation_summary.csv

Usage:
  python3 evaluation/evaluate.py [--csv] [--artifacts]
"""

import argparse
import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
GT_PATH = BASE / "attack_logs" / "ground_truth.json"
RUNNING = BASE / "running"
REPORTS = BASE / "reports"
BLUEPRINTS = BASE / "blueprints"
RESULTS_DIR = BASE / "results"

METRIC_HEADERS = [
    "Log ID", "Correct Type", "Correct Blueprint",
    "Switches Triggered", "Switches Correct",
    "Score After Switch", "Report Generated", "Steps",
]


def load_ground_truth():
    with open(GT_PATH) as f:
        return json.load(f)


def session_id_for_log(log_id: str) -> str:
    return f"hp_{log_id}"


def get_expected_decoy_paths(blueprint: str, expected_modes: list[str]) -> list[str]:
    """
    Return the set of relative paths (within honeyfs) that should exist
    if all expected_modes were triggered for this blueprint.
    """
    paths = []
    bp_profiles = BLUEPRINTS / blueprint / "behavior_profiles.json"
    if not bp_profiles.exists():
        return paths
    with open(bp_profiles) as f:
        profiles = json.load(f)
    for mode in expected_modes:
        mode_def = profiles.get("modes", {}).get(mode, {})
        for file_spec in mode_def.get("files", []):
            paths.append(file_spec["path"])
    return paths


def check_artifacts(session_id: str, blueprint: str,
                    expected_modes: list[str]) -> dict:
    """
    For a switched session, verify that expected decoy files exist in honeyfs  (#8).
    Returns {expected, present, missing, artifact_accuracy_pct}.
    """
    expected_paths = get_expected_decoy_paths(blueprint, expected_modes)
    if not expected_paths:
        return {"expected": 0, "present": 0, "missing": [], "artifact_accuracy_pct": 100.0}

    honeyfs = RUNNING / session_id / "honeyfs"
    present = []
    missing = []
    for rel in expected_paths:
        full = honeyfs / rel
        if full.exists():
            present.append(rel)
        else:
            missing.append(rel)

    pct = round(100 * len(present) / len(expected_paths), 1) if expected_paths else 100.0
    return {
        "expected": len(expected_paths),
        "present": len(present),
        "missing": missing,
        "artifact_accuracy_pct": pct,
    }


def switch_confusion(session: dict, gt: dict) -> dict:
    """
    Classify each triggered switch as: correct | false_positive | wrong | missed  (#14).

    correct       — switch in expected_modes and was triggered
    false_positive — switch triggered but NOT in expected_modes
    wrong          — switch triggered but to a mode not valid for this blueprint
    missed         — expected switch NOT triggered
    """
    expected_switches = set(gt.get("expected_behavior_switches", []))
    mode_history = session.get("mode_history", [])
    actual_switches = set(sw["to"] for sw in mode_history)

    valid_modes = {
        "ssh_bruteforce": {"expose_fake_backup", "fake_admin_success"},
        "web_attack":     {"fake_admin_panel", "expose_fake_config"},
        "monitor_only":   set(),
    }
    blueprint = session.get("blueprint", "")
    valid = valid_modes.get(blueprint, set())

    correct = actual_switches & expected_switches
    false_positive = (actual_switches - expected_switches) & valid
    wrong = actual_switches - valid
    missed = expected_switches - actual_switches

    return {
        "correct": len(correct),
        "correct_modes": sorted(correct),
        "false_positive": len(false_positive),
        "fp_modes": sorted(false_positive),
        "wrong": len(wrong),
        "wrong_modes": sorted(wrong),
        "missed": len(missed),
        "missed_modes": sorted(missed),
    }


def evaluate_session(log_id: str, gt: dict, session: dict,
                     had_report: bool,
                     check_artifacts_flag: bool) -> dict:
    result = {
        "log_id": log_id,
        "correct_type": False,
        "correct_blueprint": False,
        "switches_triggered": 0,
        "switches_correct": 0,
        "score_after_switch": None,
        "report_generated": had_report,
        "steps": session.get("step_count", 0),
        "events_total": len(session.get("events_seen", [])),
        "engagement_score": session.get("engagement_score", 0),
        # Switch confusion  (#14)
        "switch_correct": 0,
        "switch_false_positive": 0,
        "switch_wrong": 0,
        "switch_missed": 0,
        # Artifact accuracy  (#8)
        "artifact_expected": 0,
        "artifact_present": 0,
        "artifact_accuracy_pct": None,
    }

    expected_bp = gt.get("blueprint", "")
    actual_bp = session.get("blueprint", "")
    result["correct_blueprint"] = (expected_bp == actual_bp)
    result["correct_type"] = result["correct_blueprint"]

    # Switch accuracy (original metric)
    expected_switches = set(gt.get("expected_behavior_switches", []))
    mode_history = session.get("mode_history", [])
    actual_switches = set(sw["to"] for sw in mode_history)
    valid_modes = {
        "ssh_bruteforce": {"expose_fake_backup", "fake_admin_success"},
        "web_attack":     {"fake_admin_panel", "expose_fake_config"},
        "monitor_only":   set(),
    }
    valid = valid_modes.get(actual_bp, set())
    correctly_triggered = actual_switches & valid
    result["switches_triggered"] = len(actual_switches)
    result["switches_correct"] = len(correctly_triggered)

    if mode_history:
        result["score_after_switch"] = mode_history[0].get("at_score", None)
        end_score = session.get("engagement_score", 0)
        switch_score = mode_history[0].get("at_score", end_score)
        result["score_delta_after_switch"] = end_score - switch_score
    else:
        result["score_delta_after_switch"] = 0

    # Switch confusion matrix  (#14)
    confusion = switch_confusion(session, gt)
    result["switch_correct"] = confusion["correct"]
    result["switch_false_positive"] = confusion["false_positive"]
    result["switch_wrong"] = confusion["wrong"]
    result["switch_missed"] = confusion["missed"]

    # Artifact assertions  (#8)
    if check_artifacts_flag and mode_history:
        art = check_artifacts(
            f"hp_{log_id}", actual_bp,
            gt.get("expected_behavior_switches", [])
        )
        result["artifact_expected"] = art["expected"]
        result["artifact_present"] = art["present"]
        result["artifact_accuracy_pct"] = art["artifact_accuracy_pct"]
        if art["missing"]:
            result["artifact_missing"] = ",".join(art["missing"])

    return result


def print_table(results: list[dict]):
    cols = [
        ("Log ID",       "log_id",              14),
        ("Type OK",      "correct_type",          7),
        ("BP OK",        "correct_blueprint",     6),
        ("SW✓",          "switch_correct",        4),
        ("SW×FP",        "switch_false_positive", 6),
        ("SW×WR",        "switch_wrong",          6),
        ("SW✗",          "switch_missed",         5),
        ("Art%",         "artifact_accuracy_pct", 5),
        ("ΔScore@SW",    "score_delta_after_switch", 10),
        ("Report",       "report_generated",      7),
        ("Steps",        "steps",                 5),
    ]

    header = "  ".join(f"{h:<{w}}" for h, _, w in cols)
    sep    = "  ".join("-" * w for _, _, w in cols)
    print(header)
    print(sep)
    for r in results:
        row = "  ".join(
            f"{str(r.get(k, '—')):<{w}}"
            for _, k, w in cols
        )
        print(row)

    print()
    total = len(results)
    if total == 0:
        return

    correct_type = sum(1 for r in results if r["correct_type"])
    correct_bp   = sum(1 for r in results if r["correct_blueprint"])
    reports      = sum(1 for r in results if r["report_generated"])
    avg_steps    = sum(r["steps"] for r in results) / total
    avg_events   = sum(r["events_total"] for r in results) / total

    sw_sessions    = [r for r in results if r["switches_triggered"] > 0]
    total_switched = len(sw_sessions)
    total_correct  = sum(r["switches_correct"] for r in sw_sessions)
    total_triggered= sum(r["switches_triggered"] for r in sw_sessions)
    sw_accuracy    = total_correct / total_triggered if total_triggered else 0

    total_sw_correct = sum(r["switch_correct"] for r in results)
    total_sw_fp      = sum(r["switch_false_positive"] for r in results)
    total_sw_wrong   = sum(r["switch_wrong"] for r in results)
    total_sw_missed  = sum(r["switch_missed"] for r in results)

    art_rows = [r for r in results if r.get("artifact_accuracy_pct") is not None]
    avg_art  = (sum(r["artifact_accuracy_pct"] for r in art_rows) / len(art_rows)
                if art_rows else None)

    delta_sessions = [r for r in results if r.get("score_delta_after_switch", 0) > 0]
    avg_delta_sw   = (sum(r["score_delta_after_switch"] for r in delta_sessions)
                      / len(delta_sessions) if delta_sessions else 0)

    print("=" * 80)
    print(f"Classification Accuracy:        {correct_type}/{total} ({100*correct_type//total}%)")
    print(f"Blueprint Selection Accuracy:   {correct_bp}/{total} ({100*correct_bp//total}%)")
    print(f"Report Generation Success:      {reports}/{total} ({100*reports//total}%)")
    print(f"Sessions with Behavior Switch:  {total_switched}/{total}")
    print(f"Switch Correctness:             {total_correct}/{total_triggered} ({sw_accuracy*100:.0f}%)")
    print()
    print("Switch Confusion Matrix (#14):")
    print(f"  Correct switches    : {total_sw_correct}")
    print(f"  False-positive sw.  : {total_sw_fp}  (triggered but not expected)")
    print(f"  Wrong switches      : {total_sw_wrong}  (invalid mode)")
    print(f"  Missed switches     : {total_sw_missed}  (expected but not triggered)")
    if avg_art is not None:
        print()
        print(f"Artifact Accuracy (#8): {avg_art:.1f}% avg across switched sessions")
    print()
    print(f"Avg Score Δ (switching sessions): {avg_delta_sw:.1f}")
    print(f"Avg Steps per Session:            {avg_steps:.1f}")
    print(f"Avg Events per Session:           {avg_events:.1f}")


def main():
    parser = argparse.ArgumentParser(prog="evaluate.py")
    parser.add_argument("--csv", action="store_true", help="Write results/evaluation_summary.csv")
    parser.add_argument("--artifacts", action="store_true",
                        help="Check artifact presence in honeyfs (#8)")
    args = parser.parse_args()

    gt = load_ground_truth()
    results = []

    for log_id, gt_entry in gt.items():
        # Support both hp_<id> (standard) and static_<id> (baseline)
        for prefix in ("hp_", ""):
            session_id = f"{prefix}{log_id}"
            session_path = RUNNING / session_id / "session.json"
            if session_path.exists():
                break
        else:
            print(f"[SKIP] No session found for {log_id}")
            continue

        with open(session_path) as f:
            session = json.load(f)

        had_report = (REPORTS / f"{session_id}_report.md").exists()
        result = evaluate_session(log_id, gt_entry, session, had_report,
                                  check_artifacts_flag=args.artifacts)
        results.append(result)

    if not results:
        print("No completed sessions found. Run the attack pipeline first.")
        return

    print(f"\n{'='*80}")
    print(f"  OPENCLAW HONEYPOT EVALUATION — {len(results)} sessions")
    print(f"{'='*80}\n")
    print_table(results)

    if args.csv or True:   # always write CSV
        RESULTS_DIR.mkdir(exist_ok=True)
        out_path = RESULTS_DIR / "evaluation_summary.csv"
        with open(out_path, "w", newline="") as f:
            fieldnames = [k for k in results[0].keys() if k != "artifact_missing"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)
        print(f"\nResults written: {out_path}")


if __name__ == "__main__":
    main()
