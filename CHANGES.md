# OpenClaw — Reviewer Response Changes

This document describes every change made to address reviewer comments.
Each item maps to a reviewer concern and the exact file(s) that implement it.

---

## Bug Fixes (required to unblock experiments)

### 1. Fixed: concurrent sessions collided on same port
**Problem:** all SSH sessions used port 2222, all web sessions used 8080 — running
two sessions at once was impossible.
**Fix:** `honeypot_manager.py` — `_alloc_free_port()` asks the OS for a free port
per session. Each deploy now records its ports in `session.json` under `host_ports`.
**Impact:** enables the concurrency experiment (reviewer #5).

### 2. Fixed: path traversal via `--session` argument
**Problem:** `--session ../../etc/passwd` would resolve to a path outside `running/`.
**Fix:** `honeypot_manager.py` — `_validate_session_id()` rejects any session ID
not matching `^[A-Za-z0-9_-]{1,64}$`. Called at the top of every command.
**Impact:** closes the security hole; also documented in the API security test.

---

## New: Formalized Policy (Reviewer #12, #13)

**Problem:** decision logic was copy-pasted in three places — `config.json`,
`skills/honeypot-master/SKILL.md`, and `run_intensive_test.py`.

**New files:**
- `policy/orchestration_policy.yaml` — single source of truth for classification
  rules, switching rules, loop-control constants, and score weights.
- `policy/policy_engine.py` — `classify(log)`, `decide_switch(blueprint, logs_result, mode)`,
  `should_stop()`. All three functions read from the YAML.
- `docs/openclaw_workflow.md` — formal pipeline diagram (Attack Event → Log Parser →
  Classifier → OpenClaw Agent → Policy Validation → Template Generation → Runtime Switch)
  with each stage annotated by the exact function and file that implements it.

**Modified:**
- `run_intensive_test.py` — removed the inline `decide_ssh_switch` / `decide_web_switch`
  / `should_stop` functions; now imports from `policy/policy_engine.py`.
- `skills/honeypot-master/SKILL.md` — added a note pointing to the YAML as authoritative.

---

## New: Switching Latency Instrumentation (Reviewer #3, #7)

**New function:** `honeypot_manager._verify_volume_sync_timed()` — polls
`docker exec <session> test -f <path>` until the file is visible in the container,
returns propagation time in milliseconds.

**Modified:** `honeypot_manager.cmd_behavior()` now records per-switch timing:
- `template_build_ms` — time to render Jinja2 templates and write files to host
- `volume_sync_ms` — time until container sees the first new file
- `total_ms` — end-to-end switch call time

Each switch appends one record to `running/<session_id>/switch_metrics.json`.
The latency dict is also returned in the `behavior` JSON output so drivers can log it.

---

## New: Static Baseline Mode (Reviewer #2)

**Modified:** `honeypot_manager.cmd_deploy()` — accepts `--static` flag.
When set: pre-writes the union of ALL non-default decoy modes at deploy time,
sets `session["static"] = true`.

**Modified:** `honeypot_manager.cmd_behavior()` — returns immediately with
`"note": "static baseline — switching disabled"` when session is static.

**New file:** `baseline/MANIFEST.md` — lists every decoy file in both adaptive
and static deployments, proving the asset inventories are identical.

**New script:** `baseline/run_baseline.py` — runs the attack catalog against
static deployments. Produces `results/adaptive_vs_static.csv`.

---

## New: mtime Backdating (Reviewer #11)

**Modified:** `honeypot_manager._write_behavior_files()` — after writing each
decoy file, calls `os.utime()` with a random 3–30 day past timestamp.
Prevents an attacker from detecting a switch by noticing freshly-created files.

---

## New: Input Sanitization (Reviewer #9)

**New function:** `honeypot_manager._sanitize_log()` — caps event count at 1000,
individual event string length at 512 characters, coerces port to int.
Called at the top of `cmd_classify()` before any rule evaluation.

---

## New: Real-Attack Dataset, 40+ Sessions (Reviewer #1, #15)

**New file:** `attacks/catalog.yaml` — 44 attack entries across 8 categories:
- SSH brute force (hydra, medusa, nmap) — 16 entries
- Web enumeration / dir fuzzing (gobuster, ffuf, nikto, nmap) — 14 entries
- SSH post-exploitation (paramiko) — 6 entries
- Credential attacks (hydra http-post-form, ffuf POST) — 4 entries
- Vulnerability scanning (nmap scripts, nikto) — 6 entries
- Bot activity (scripted mixed traffic) — 1 entry
- Unknown / monitor-only (nmap on non-honeypot ports) — 4 entries
- Metasploit modules (optional/heavy) — 4 entries

**New scripts:** `attacks/scripts/` — curl_admin_probe.py, curl_sqli.py,
bot_activity.py, postex_ssh.py, msf_run.py.

**New wordlists:** `attacks/wordlists/` — top100_passwords.txt, ssh_users.txt,
service_accounts.txt, high_value_users.txt, config_paths.txt.

**New script:** `attacks/run_attacks.py` — deploys each catalog entry, runs the
real tool against a live container, drives the monitor loop via policy_engine,
generates a report, and appends results to `attack_logs/ground_truth.json` and
`results/dataset_manifest.csv`.

---

## New: Measurement Harnesses (Reviewer #4, #5, #6, #7)

### Session Continuity (#4)
**New script:** `experiments/session_continuity.py`
Opens a persistent paramiko SSH channel (or requests.Session for web), triggers
a behavior switch, then asserts on the same connection: socket alive, channel
still executes, new decoy file is visible.
Output: `results/session_continuity.csv` — connection_preserved, channel_still_executes,
decoy_visible_after_switch, switch_latency_ms per trial.

### Volume Sync Latency (#7)
**New script:** `experiments/volume_sync.py`
Measures three stages per switch: host write time (from switch_metrics.json),
container-visible time (from _verify_volume_sync_timed), attacker-observable time
(how long until SSH cat / HTTP GET returns the file content).
Output: `results/volume_sync_latency.csv` with mean/p50/p95/max per stage.

### Concurrency Scaling (#5)
**New script:** `experiments/concurrency.py`
Spawns 1/5/10/20 sessions in parallel (possible because of the dynamic port fix),
runs lightweight attack tools against each, measures switch success rate, switch
latency, container crashes, and resource usage.
Output: `results/concurrency_scaling.csv`.

### Resource Utilization (#6)
**New script:** `experiments/resource_monitor.py`
Samples `docker stats` + psutil at 2-second intervals, tagged by phase label.
Used as a context manager by concurrency.py. Can also run standalone.
Output: `results/resource_by_phase.csv`.

### Fingerprinting (#11)
**New script:** `experiments/fingerprint.py`
From the attacker's SSH session, measures: mtime anomaly (is the decoy file's
timestamp suspiciously fresh?), directory listing delta (did new files appear?),
and response timing anomaly during the switch window.
Output: `results/fingerprint_indicators.csv`.

---

## New: Security Analysis (Reviewer #9, #10)

### Log Poisoning (#9)
**New script:** `security/log_poisoning.py`
Injects prompt-injection / fake-alert payloads into every parsed field (usernames,
event strings, HTTP paths) and asserts classification and switching decisions are
unchanged. 19 test cases — all pass (rule-based engine ignores free-text injection).
Output: `results/log_poisoning.csv`.

### API Security (#10)
**New script:** `security/api_fuzz.py`
Tests honeypot_manager.py against: path traversal (blocked by _validate_session_id),
unknown blueprints/modes (blocked by whitelists), oversized inputs (handled by
_sanitize_log), replay attacks (blocked by session-dir existence check), concurrent
command collisions (no crash). 25 test cases — all pass.
Output: `results/api_security.csv`.

---

## Extended: Evaluation at Scale (Reviewer #8, #14)

**Modified:** `evaluation/evaluate.py`
- Reads all sessions in `ground_truth.json` (not just the original 10).
- **Artifact assertions (#8):** for each switched session, checks that expected
  decoy files actually exist in `running/<id>/honeyfs/`.
- **Switch confusion matrix (#14):** classifies each switch as correct /
  false-positive (triggered but not expected) / wrong (invalid mode) /
  missed (expected but not triggered).
- Always writes `results/evaluation_summary.csv`.

---

## Master Aggregator

**New script:** `experiments/run_all.py`
Runs all experiments in order (skipping any whose CSV already exists) then reads
all CSVs and writes `results/SUMMARY.md` — a single markdown document with every
reviewer-requested table ready to reference in the paper.

---

## Already Passing Tests (run during implementation)

| Test | Result |
|---|---|
| `security/log_poisoning.py` | 19/19 PASS |
| `security/api_fuzz.py` | 25/25 PASS |
| `evaluation/evaluate.py` on original 10 sessions | 10/10 classification, 100% switch correctness |
| `policy_engine` classify on all 10 original logs | matches ground truth exactly |
| Path traversal `--session ../../etc/passwd` | rejected with error |
| Static deploy + behavior no-op | works correctly |

---

## Still Needs Running (requires Docker + time)

```bash
cd ~/llm-honeypot-openclaw

python3 attacks/run_attacks.py            # ~2 hrs  — 40 real-tool sessions
python3 baseline/run_baseline.py          # ~2 hrs  — static baseline
python3 experiments/session_continuity.py --n 20   # ~30 min
python3 experiments/volume_sync.py --switches 30   # ~20 min
python3 experiments/concurrency.py                 # ~30 min
python3 experiments/fingerprint.py --trials 10     # ~15 min
python3 experiments/run_all.py --skip-dataset --skip-baseline \
        --skip-continuity --skip-security --skip-concurrency
```

Each script prints a summary table and writes a CSV to `results/`.
`experiments/run_all.py` aggregates everything into `results/SUMMARY.md`.
