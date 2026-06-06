# OpenClaw Orchestration Workflow  (#12)

This document formalizes the end-to-end pipeline from attack event ingestion through
adaptive honeypot switching. Every stage is annotated with the exact function and file
that implements it, so the workflow description is grounded in runnable code.

---

## Pipeline Overview

```
Attack Event
      │
      ▼
┌─────────────────┐
│  Log Parser      │  honeypot_manager._parse_cowrie_logs()  /  _parse_flask_logs()
│  (Stage 1)       │  Reads Cowrie JSON log or Flask requests.json incrementally.
│                  │  Normalizes to: {type, username/path/command, success, ts}
└────────┬────────┘
         │  normalized events list
         ▼
┌─────────────────┐
│  Behavior        │  policy_engine.classify(log)
│  Classifier      │  Rule-based scoring over ports/keywords/paths/usernames.
│  (Stage 2)       │  Produces: {suggested_blueprint, confidence, attack_type}
│                  │  Config: policy/orchestration_policy.yaml § classification
└────────┬────────┘
         │  blueprint, confidence
         ▼
┌─────────────────┐
│  OpenClaw Agent  │  skills/honeypot-master/SKILL.md
│  (Stage 3)       │  LLM reads events + decides next action.
│                  │  Decision expressed as: classify / deploy / logs / behavior
│                  │  / report / stop calls to honeypot_manager.py
└────────┬────────┘
         │  decided action
         ▼
┌─────────────────┐
│  Policy          │  policy_engine.decide_switch(blueprint, logs_result, mode)
│  Validation      │  Checks action against switching rules in orchestration_policy.yaml.
│  (Stage 4)       │  Enforces: idempotent switching, mode whitelist, rule ordering.
└────────┬────────┘
         │  validated target_mode
         ▼
┌─────────────────┐
│  Template        │  honeypot_manager._write_behavior_files()
│  Selection &     │  Selects Jinja2 templates from blueprints/<bp>/behavior_profiles.json.
│  Artifact Gen.   │  Renders decoy files with attacker-specific context
│  (Stage 5)       │  (attempted usernames, visited paths, session token).
│                  │  Applies mtime backdating to prevent fingerprinting  (#11).
└────────┬────────┘
         │  rendered files written to running/<id>/honeyfs/
         ▼
┌─────────────────┐
│  Runtime Switch  │  Docker bind-mount propagation
│  (Stage 6)       │  Host writes → shared volume → container reads with no restart.
│                  │  honeypot_manager._verify_volume_sync_timed() confirms visibility.
│                  │  Latency recorded in running/<id>/switch_metrics.json
└─────────────────┘
```

---

## Stage-by-Stage Detail

### Stage 1 — Log Parser

| Attribute | Value |
|---|---|
| Functions | `_parse_cowrie_logs()`, `_parse_cowrie_docker_logs()`, `_parse_flask_logs()` |
| File | `honeypot_manager.py` |
| Input | Cowrie JSONL (`running/<id>/logs/cowrie.json`) or Flask JSONL (`requests.json`) |
| Output | `list[dict]` — each dict has `type`, `timestamp`, and event-specific fields |
| Fallback | If Cowrie JSON log unavailable, parses `docker logs` stdout via regex |

Incremental: only new lines since last poll are returned (`log_offset` in session state).

---

### Stage 2 — Behavior Classifier

| Attribute | Value |
|---|---|
| Functions | `policy_engine.classify()`, `honeypot_manager.cmd_classify()` |
| Files | `policy/policy_engine.py`, `policy/orchestration_policy.yaml` |
| Input | Raw attack log JSON (from `attack_logs/` or captured live) |
| Output | `{suggested_blueprint, confidence, attack_type, indicators}` |
| Sanitization | `honeypot_manager._sanitize_log()` — caps event count/length before scoring (#9) |

Scoring: each blueprint accumulates a score from port match + keyword hits + path hits
+ username hits. Score is capped at 1.0. The blueprint with the highest score wins;
if it exceeds `confidence_threshold` (0.6) it is deployed, otherwise `monitor_only`.

---

### Stage 3 — OpenClaw Agent

| Attribute | Value |
|---|---|
| Specification | `skills/honeypot-master/SKILL.md` |
| Reasoning format | OBSERVE / ASSESS / DECIDE after each command result |
| Allowed tools | `honeypot_manager.py` subcommands only (classify/deploy/logs/behavior/report/stop) |
| Policy reference | Decision tables in SKILL.md reference `policy/orchestration_policy.yaml` |

The LLM agent is the sole caller of the orchestration CLI. It cannot execute arbitrary code.

---

### Stage 4 — Policy Validation

| Attribute | Value |
|---|---|
| Function | `policy_engine.decide_switch(blueprint, logs_result, current_mode)` |
| File | `policy/policy_engine.py` |
| Config | `policy/orchestration_policy.yaml` § switching |
| Guarantees | Switching is idempotent; target mode must be in `allowed_modes`; rules evaluated in order |

Rules evaluated in priority order (earlier rules take precedence). See
`policy/orchestration_policy.yaml` for the full rule set with `id`, `condition`, `target_mode`,
and human-readable `description` fields.

---

### Stage 5 — Template Selection & Artifact Generation

| Attribute | Value |
|---|---|
| Functions | `honeypot_manager._write_behavior_files()` |
| File | `honeypot_manager.py` |
| Templates | `blueprints/<bp>/decoys/*.j2` (Jinja2) |
| Context | `{attempted_usernames, paths_visited, session_id, auth_token, backup_user}` |
| Fingerprint mitigation | `os.utime()` backdates mtime/atime by 3–30 days (#11) |

---

### Stage 6 — Runtime Switch (Volume Propagation)

| Attribute | Value |
|---|---|
| Mechanism | Docker bind-mount: host `running/<id>/honeyfs/` → container honeyfs path |
| No restart | Container reads new files via VFS; SSH sessions / HTTP sessions are not interrupted |
| Validation | `honeypot_manager._verify_volume_sync_timed()` polls `docker exec test -f <path>` |
| Latency record | `running/<id>/switch_metrics.json` — per-switch `{template_build_ms, volume_sync_ms, total_ms}` |

---

## Session State Machine

```
            deploy
  [none] ─────────────→ [deploying]
                               │
                               │ container up
                               ▼
                          [running]  ←──── behavior switch (files updated,
                               │            session stays connected)
                               │
                            stop / max_steps / collapse
                               ▼
                          [stopped]
                               │
                               │ report
                               ▼
                          reports/<id>_report.md
```

State is persisted in `running/<id>/session.json` after every manager call.

---

## Adaptive vs. Static Baseline

The `--static` flag on `deploy` pre-writes **all** decoy modes at deploy time
(Stage 5 runs once for every non-default mode). Stages 3, 4, and the switching
half of Stage 6 are then no-ops: `cmd_behavior` returns immediately when
`session["static"] == true`. This produces an identical-asset environment whose
only difference from adaptive is the absence of runtime switching — a valid and
fair baseline for comparing engagement depth  (#2).
