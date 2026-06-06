# Harbinger

An LLM-driven adaptive honeypot system built on the [OpenClaw](https://github.com/didi-09/harbinger) agent framework. Harbinger classifies incoming attacks in real time and switches deception personas without restarting containers, maximising attacker dwell time and intelligence collection.

---

## How it works

An LLM agent (Claude Sonnet) drives a constrained CLI — `honeypot_manager.py` — that exposes six commands:

| Command | Description |
|---|---|
| `classify --log <path>` | Classify an attack log and recommend a blueprint |
| `deploy --blueprint <name> --session <id>` | Spin up a honeypot container for a session |
| `logs --session <id>` | Fetch live attacker events |
| `behavior --session <id> --mode <mode>` | Switch deception mode at runtime |
| `report --session <id>` | Generate an engagement report |
| `stop --session <id>` | Tear down a session |

The agent runs a perception–action loop: classify → deploy → poll logs → switch behavior → report. Behavior switching is done by hot-swapping files over a shared Docker volume — no container restart, zero attacker-observable downtime.

---

## Blueprints

Three deception personas are available:

- **`ssh_bruteforce`** — Cowrie SSH honeypot with decoy credential files, backup scripts, and bash history. Switches to `expose_fake_backup` or `fake_admin_success` based on attacker behavior.
- **`web_attack`** — Flask web honeypot serving fake admin panels, `.env` files, and config backups. Switches to `expose_fake_config` or `fake_admin_panel` on probing.
- **`monitor_only`** — Passive monitoring fallback for unclassified traffic.

---

## Engagement scoring

Events are scored to track attacker engagement over time:

| Event | Score |
|---|---|
| Connection | +1 |
| Login attempt | +2 |
| Command executed | +3 |
| File read | +4 |
| File download | +5 |
| No new activity | −2 |

---

## Results (50-session evaluation)

| Metric | Result |
|---|---|
| Classification accuracy | 100% (50/50) |
| Blueprint selection accuracy | 100% (50/50) |
| Sessions with adaptive switches | 57.5% (23/40) |
| Switch correctness | 100% (12/12) |
| Session continuity after switch | 97.5% (39/40) |
| Engagement vs. static baseline | +307% |
| Events vs. static baseline | +405% |
| Switching pipeline latency (web) | ~7 ms attacker-observable |

---

## Project structure

```
honeypot_manager.py       constrained CLI — the only entry point the LLM calls
blueprints/               deception persona definitions and Jinja2 decoy templates
policy/                   orchestration_policy.yaml + rule-based policy engine
docker/                   Dockerfiles for honeypot containers
attacks/                  attack simulation scripts and wordlists
evaluation/               evaluation harness
experiments/              latency, concurrency, fingerprinting, and continuity tests
results/                  CSV data from the 50-session evaluation
security/                 log poisoning and API security test suites
reports/                  per-session engagement reports
```

---

## Setup

```bash
pip install -r requirements.txt
```

Docker must be running. Each blueprint spins up its own container on a dynamically allocated port.

---

## Running an evaluation

```bash
# Run all attack simulations against deployed honeypots
python attacks/run_attacks.py

# Evaluate results against ground truth
python evaluation/evaluate.py

# Run the full experiment suite (latency, concurrency, fingerprinting)
python experiments/run_all.py
```

---

## Security properties

- **Log poisoning resistance** — 100% (19/19): the rule-based policy engine is unaffected by prompt injection in attacker-controlled fields (usernames, paths, commands).
- **API security** — 100% (25/25): path traversal, unknown blueprints, oversized inputs, and replay attacks are all blocked.
- **Switch fingerprinting** — 0/10 mtime anomalies: decoy files are backdated 3–30 days via `os.utime()`.

---

## Paper

> *OpenClaw-Driven Adaptive Honeypot Orchestration with Runtime Deception Switching*  
> Submitted to IoTSec4CIS 2026 — International Workshop on IoT & Cybersecurity in Critical Infrastructure Systems.
