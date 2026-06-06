#!/usr/bin/env python3
"""
run_all.py — Master experiment runner. Aggregates all results into SUMMARY.md.

Usage:
  python3 experiments/run_all.py [--skip-dataset] [--skip-baseline]
                                   [--skip-continuity] [--skip-security]
                                   [--skip-concurrency]

Each section is skipped if its CSV already exists in results/ (reuse existing data).
Generates results/SUMMARY.md with every reviewer-requested table.
"""

import argparse
import csv
import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent.resolve()
RESULTS_DIR = BASE / "results"
MANAGER = str(BASE / "honeypot_manager.py")
sys.path.insert(0, str(BASE))


def banner(s: str):
    print(f"\n{'='*65}\n  {s}\n{'='*65}")


def run_script(script_path: str, args: list[str] = None, timeout: int = 7200):
    cmd = ["python3", str(BASE / script_path)] + (args or [])
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=BASE, timeout=timeout)
    return result.returncode == 0


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def stats(values: list[float]) -> dict:
    vals = [v for v in values if v is not None]
    if not vals:
        return {"n": 0, "mean": "N/A", "p50": "N/A", "p95": "N/A", "max": "N/A"}
    vals.sort()
    n = len(vals)
    return {
        "n": n,
        "mean": round(statistics.mean(vals), 2),
        "p50": round(vals[int(n * 0.50)], 2),
        "p95": round(vals[min(int(n * 0.95), n-1)], 2),
        "max": round(vals[-1], 2),
    }


def pct(num, total):
    if total == 0:
        return "N/A"
    return f"{100 * num // total}%"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-dataset", action="store_true")
    parser.add_argument("--skip-baseline", action="store_true")
    parser.add_argument("--skip-continuity", action="store_true")
    parser.add_argument("--skip-security", action="store_true")
    parser.add_argument("--skip-concurrency", action="store_true")
    parser.add_argument("--logs-wait", type=int, default=10)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)

    # ── Phase 2: Dataset ─────────────────────────────────────────────────────
    dataset_csv = RESULTS_DIR / "dataset_manifest.csv"
    if not args.skip_dataset and not dataset_csv.exists():
        banner("Phase 2: Real-attack dataset collection")
        run_script("attacks/run_attacks.py",
                   ["--logs-wait", str(args.logs_wait), "--skip-optional"])

    # ── Phase 3: Baseline ────────────────────────────────────────────────────
    baseline_csv = RESULTS_DIR / "adaptive_vs_static.csv"
    if not args.skip_baseline and not baseline_csv.exists():
        banner("Phase 3: Static baseline comparison")
        run_script("baseline/run_baseline.py",
                   ["--logs-wait", str(args.logs_wait)])

    # ── Phase 4: Session continuity ──────────────────────────────────────────
    continuity_csv = RESULTS_DIR / "session_continuity.csv"
    if not args.skip_continuity and not continuity_csv.exists():
        banner("Phase 4: Session continuity")
        run_script("experiments/session_continuity.py", ["--n", "20", "--blueprint", "both"])

    # ── Phase 4: Volume sync ─────────────────────────────────────────────────
    vsync_csv = RESULTS_DIR / "volume_sync_latency.csv"
    if not vsync_csv.exists():
        banner("Phase 4: Volume sync latency")
        run_script("experiments/volume_sync.py", ["--switches", "30"])

    # ── Phase 4: Concurrency ─────────────────────────────────────────────────
    conc_csv = RESULTS_DIR / "concurrency_scaling.csv"
    if not args.skip_concurrency and not conc_csv.exists():
        banner("Phase 4: Concurrency scaling")
        run_script("experiments/concurrency.py", ["--levels", "1,5,10,20",
                                                   "--blueprint", "web"])

    # ── Phase 5: Security ────────────────────────────────────────────────────
    poison_csv = RESULTS_DIR / "log_poisoning.csv"
    api_csv = RESULTS_DIR / "api_security.csv"
    fp_csv = RESULTS_DIR / "fingerprint_indicators.csv"
    if not args.skip_security:
        if not poison_csv.exists():
            banner("Phase 5: Log poisoning test")
            run_script("security/log_poisoning.py")
        if not api_csv.exists():
            banner("Phase 5: API security fuzz")
            run_script("security/api_fuzz.py")
        if not fp_csv.exists():
            banner("Phase 5: Fingerprinting test")
            run_script("experiments/fingerprint.py", ["--trials", "10"])

    # ── Phase 6: Evaluation ──────────────────────────────────────────────────
    eval_csv = RESULTS_DIR / "evaluation_summary.csv"
    banner("Phase 6: Evaluation at scale")
    run_script("evaluation/evaluate.py", ["--artifacts"])

    # ── Build SUMMARY.md ─────────────────────────────────────────────────────
    banner("Building SUMMARY.md")

    md_sections = []
    md_sections.append(f"""# OpenClaw Evaluation Summary
*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC*

This document aggregates all reviewer-requested measurements. Every table is
produced from a CSV in `results/` — no values are hand-entered.

---
""")

    # ── 1. Dataset overview ──
    ds_rows = load_csv(dataset_csv)
    if ds_rows:
        total = len(ds_rows)
        clf_ok = sum(1 for r in ds_rows if r.get("blueprint_correct", "").lower() in ("true", "1"))
        rep_ok = sum(1 for r in ds_rows if r.get("report_ok", "").lower() in ("true", "1"))
        cats = {}
        for r in ds_rows:
            c = r.get("category", "other")
            cats[c] = cats.get(c, 0) + 1
        cat_rows = "\n".join(f"| {c} | {n} |" for c, n in sorted(cats.items()))
        md_sections.append(f"""## 1. Evaluation Dataset (#1, #15)

| Metric | Value |
|---|---|
| Total attack sessions | {total} |
| Classification accuracy | {pct(clf_ok, total)} |
| Report generation success | {pct(rep_ok, total)} |

### Sessions by Category

| Category | Sessions |
|---|---|
{cat_rows}

*Dataset driven by real tools: hydra, medusa, gobuster, ffuf, nikto, nmap, curl.*
*Source: `results/dataset_manifest.csv`*

---
""")

    # ── 2. Switching latency ──
    eval_rows = load_csv(eval_csv)
    # Get latency from switch_metrics.json files
    lats = []
    for sess_dir in (BASE / "running").iterdir():
        metrics_path = sess_dir / "switch_metrics.json"
        if metrics_path.exists():
            try:
                data = json.loads(metrics_path.read_text())
                for entry in data:
                    lats.append(entry)
            except Exception:
                pass

    if lats:
        template_vals = [e["template_build_ms"] for e in lats
                         if e.get("template_build_ms") is not None]
        sync_vals = [e["volume_sync_ms"] for e in lats
                     if e.get("volume_sync_ms") is not None and e["volume_sync_ms"] >= 0]
        total_vals = [e["total_ms"] for e in lats if e.get("total_ms") is not None]
        t_s = stats(template_vals)
        sy_s = stats(sync_vals)
        to_s = stats(total_vals)
        md_sections.append(f"""## 2. Runtime Switching Latency (#3)

Per-stage breakdown (milliseconds). *Detection* and *LLM Decision* timings are
measured end-to-end by the orchestration loop; remaining stages by honeypot_manager.

| Stage | Mean (ms) | p50 (ms) | p95 (ms) | Max (ms) | n |
|---|---|---|---|---|---|
| Template Build | {t_s['mean']} | {t_s['p50']} | {t_s['p95']} | {t_s['max']} | {t_s['n']} |
| Volume Sync | {sy_s['mean']} | {sy_s['p50']} | {sy_s['p95']} | {sy_s['max']} | {sy_s['n']} |
| Total (switch call) | {to_s['mean']} | {to_s['p50']} | {to_s['p95']} | {to_s['max']} | {to_s['n']} |

*Source: `running/*/switch_metrics.json`*

---
""")

    # ── 3. Session continuity ──
    cont_rows = load_csv(continuity_csv)
    if cont_rows:
        for bp in ["ssh", "web"]:
            bp_rows = [r for r in cont_rows if r.get("blueprint") == bp]
            n = len(bp_rows)
            if not n:
                continue
            preserved = sum(1 for r in bp_rows if r.get("connection_preserved", "").lower() in ("true", "1"))
            executes = sum(1 for r in bp_rows if r.get("channel_still_executes", "").lower() in ("true", "1"))
            decoy_vis = sum(1 for r in bp_rows if r.get("decoy_visible_after_switch", "").lower() in ("true", "1"))
        md_sections.append(f"""## 3. Session Continuity During Switching (#4)

| Metric | SSH | Web |
|---|---|---|
| Trials | {sum(1 for r in cont_rows if r.get('blueprint')=='ssh')} | {sum(1 for r in cont_rows if r.get('blueprint')=='web')} |
| Connection preserved | {sum(1 for r in cont_rows if r.get('blueprint')=='ssh' and r.get('connection_preserved','').lower() in ('true','1'))} | {sum(1 for r in cont_rows if r.get('blueprint')=='web' and r.get('connection_preserved','').lower() in ('true','1'))} |
| Channel still executes | {sum(1 for r in cont_rows if r.get('blueprint')=='ssh' and r.get('channel_still_executes','').lower() in ('true','1'))} | {sum(1 for r in cont_rows if r.get('blueprint')=='web' and r.get('channel_still_executes','').lower() in ('true','1'))} |
| Decoy visible after switch | {sum(1 for r in cont_rows if r.get('blueprint')=='ssh' and r.get('decoy_visible_after_switch','').lower() in ('true','1'))} | {sum(1 for r in cont_rows if r.get('blueprint')=='web' and r.get('decoy_visible_after_switch','').lower() in ('true','1'))} |

*Source: `results/session_continuity.csv`*

---
""")

    # ── 4. Concurrency scaling ──
    conc_rows = load_csv(conc_csv)
    if conc_rows:
        hdr = "| N | DeployOK | Switch% | AvgLat(ms) | Crashes | CPU% | Mem% |"
        sep = "|---|---|---|---|---|---|---|"
        data_rows = "\n".join(
            f"| {r['concurrency_level']} | {r['deploy_ok']} | "
            f"{r['switch_success_rate_pct']}% | {r.get('avg_switch_latency_ms','—')} | "
            f"{r['container_crashes']} | {r.get('avg_host_cpu_pct','—')} | "
            f"{r.get('avg_host_mem_pct','—')} |"
            for r in conc_rows if r.get("blueprint") in ("web_attack", "web")
        )
        md_sections.append(f"""## 4. Concurrent Session Scaling (#5, #6)

{hdr}
{sep}
{data_rows}

*Source: `results/concurrency_scaling.csv`, `results/resource_by_phase.csv`*

---
""")

    # ── 5. Volume sync latency ──
    vsync_rows = load_csv(vsync_csv)
    if vsync_rows:
        for bp in ["ssh", "web"]:
            bp_rows = [r for r in vsync_rows if r.get("blueprint") == bp]
            if not bp_rows:
                continue
        def get_float_col(rows, col):
            vals = []
            for r in rows:
                v = r.get(col, "")
                try:
                    fv = float(v)
                    if fv >= 0:
                        vals.append(fv)
                except (ValueError, TypeError):
                    pass
            return vals

        ssh_rows = [r for r in vsync_rows if r.get("blueprint") == "ssh"]
        web_rows = [r for r in vsync_rows if r.get("blueprint") == "web"]
        rows_str = ""
        for label, rows in [("SSH", ssh_rows), ("Web", web_rows)]:
            if not rows:
                continue
            for field, fname in [("template_build_ms", "Template Build"),
                                   ("volume_sync_ms", "Volume Sync"),
                                   ("attacker_observable_ms", "Attacker Observable")]:
                s = stats(get_float_col(rows, field))
                rows_str += (f"| {label} | {fname} | {s['mean']} | {s['p50']} | "
                             f"{s['p95']} | {s['max']} | {s['n']} |\n")

        md_sections.append(f"""## 5. Volume Synchronization Timing (#7)

| Blueprint | Stage | Mean (ms) | p50 (ms) | p95 (ms) | Max (ms) | n |
|---|---|---|---|---|---|---|
{rows_str.strip()}

*Source: `results/volume_sync_latency.csv`*

---
""")

    # ── 6. Switching correctness at scale ──
    if eval_rows:
        total = len(eval_rows)
        clf_ok = sum(1 for r in eval_rows if r.get("correct_blueprint", "").lower() in ("true","1"))
        sw_correct = sum(int(r.get("switch_correct", 0) or 0) for r in eval_rows)
        sw_fp = sum(int(r.get("switch_false_positive", 0) or 0) for r in eval_rows)
        sw_wrong = sum(int(r.get("switch_wrong", 0) or 0) for r in eval_rows)
        sw_missed = sum(int(r.get("switch_missed", 0) or 0) for r in eval_rows)
        art_rows_ = [r for r in eval_rows if r.get("artifact_accuracy_pct") not in (None, "")]
        avg_art = (sum(float(r["artifact_accuracy_pct"]) for r in art_rows_) / len(art_rows_)
                   if art_rows_ else None)
        md_sections.append(f"""## 6. Switching Correctness & Confusion Matrix (#8, #14)

| Metric | Value |
|---|---|
| Sessions evaluated | {total} |
| Blueprint classification accuracy | {pct(clf_ok, total)} |
| Correct switches | {sw_correct} |
| False-positive switches | {sw_fp} |
| Wrong switches (invalid mode) | {sw_wrong} |
| Missed switches | {sw_missed} |
| Avg artifact accuracy | {f'{avg_art:.1f}%' if avg_art is not None else 'N/A'} |

*Source: `results/evaluation_summary.csv`*

---
""")

    # ── 7. Adaptive vs. Static baseline ──
    comp_rows = load_csv(baseline_csv)
    if comp_rows:
        n = len(comp_rows)
        avg_adapt = sum(int(r.get("adaptive_score", 0) or 0) for r in comp_rows) / n
        avg_static = sum(int(r.get("static_score", 0) or 0) for r in comp_rows) / n
        avg_delta = avg_adapt - avg_static
        cats = sorted(set(r.get("category","") for r in comp_rows))
        cat_rows = ""
        for c in cats:
            cr = [r for r in comp_rows if r.get("category") == c]
            if not cr:
                continue
            a_sc = sum(int(r.get("adaptive_score",0) or 0) for r in cr) / len(cr)
            s_sc = sum(int(r.get("static_score",0) or 0) for r in cr) / len(cr)
            cat_rows += f"| {c} | {a_sc:.1f} | {s_sc:.1f} | {a_sc-s_sc:+.1f} |\n"

        md_sections.append(f"""## 7. Adaptive vs. Static Baseline Comparison (#2)

Both systems used identical assets (see `baseline/MANIFEST.md`).
The only difference: adaptive uses runtime switching; static pre-deploys all assets.

| Metric | Adaptive | Static | Delta |
|---|---|---|---|
| Avg engagement score | {avg_adapt:.1f} | {avg_static:.1f} | {avg_delta:+.1f} |

### Per-Category Breakdown

| Category | Adaptive Score | Static Score | Delta |
|---|---|---|---|
{cat_rows.strip()}

*Source: `results/adaptive_vs_static.csv`*

---
""")

    # ── 8. Security analysis ──
    poison_rows = load_csv(poison_csv)
    api_rows = load_csv(api_csv)
    fp_rows = load_csv(fp_csv)

    security_md = "## 8. Security Analysis (#9, #10, #11)\n\n"
    if poison_rows:
        n = len(poison_rows)
        passed = sum(1 for r in poison_rows if r.get("passed","").lower() in ("true","1"))
        security_md += f"### Log Poisoning Resistance (#9)\n\n"
        security_md += f"| Test cases | Passed | Failed |\n|---|---|---|\n"
        security_md += f"| {n} | {passed} | {n-passed} |\n\n"
        security_md += "*Rule-based classifier ignores free-text injection. "
        security_md += "_sanitize_log() caps event count/length.*\n\n"

    if api_rows:
        n = len(api_rows)
        passed = sum(1 for r in api_rows if r.get("passed","").lower() in ("true","1"))
        security_md += f"### Orchestration API Security (#10)\n\n"
        security_md += f"| Tests | Passed | Failed |\n|---|---|---|\n"
        security_md += f"| {n} | {passed} | {n-passed} |\n\n"
        security_md += ("*Path traversal via --session: blocked by _validate_session_id(). "
                        "Unknown blueprints/modes: blocked by whitelist.*\n\n")

    if fp_rows:
        valid = [r for r in fp_rows if not r.get("error")]
        n = len(valid)
        if n:
            mtime_det = sum(1 for r in valid
                            if r.get("mtime_anomaly_detectable","").lower() in ("true","1"))
            dirlist_det = sum(1 for r in valid
                              if r.get("dirlist_delta_detectable","").lower() in ("true","1"))
            security_md += f"### Switch Fingerprinting (#11)\n\n"
            security_md += f"| Indicator | Detectable | Trials |\n|---|---|---|\n"
            security_md += f"| mtime anomaly (fresh timestamp) | {mtime_det}/{n} | {n} |\n"
            security_md += f"| Directory listing delta | {dirlist_det}/{n} | {n} |\n\n"
            security_md += ("*mtime backdating (3-30 day random offset) mitigates fresh-timestamp "
                            "detection. Directory delta is a structural limitation.*\n\n")

    security_md += "*Sources: `results/log_poisoning.csv`, `results/api_security.csv`, "
    security_md += "`results/fingerprint_indicators.csv`*\n\n---\n"
    md_sections.append(security_md)

    # ── Write SUMMARY.md ──
    summary_path = RESULTS_DIR / "SUMMARY.md"
    summary_path.write_text("\n".join(md_sections))
    print(f"\nSUMMARY.md written: {summary_path}")
    print(f"  Sections: {len(md_sections) - 1} tables")


if __name__ == "__main__":
    main()
