#!/usr/bin/env python3
"""
policy_engine.py — Single source of truth for OpenClaw decision logic  (#13).

Reads orchestration_policy.yaml and exposes two functions consumed by
run_intensive_test.py, attacks/run_attacks.py, and the evaluation harness:

  classify(log: dict) -> dict
      Replicates honeypot_manager.py cmd_classify scoring; returns
      {log_id, attack_type, confidence, suggested_blueprint, indicators}.

  decide_switch(blueprint: str, logs_result: dict, current_mode: str) -> str | None
      Applies switching rules from the policy YAML; returns the mode to
      switch to, or None if no rule fires.

  should_stop(logs_result: dict, post_switch_polls: int) -> bool
      Loop-exit predicate using loop_control from the policy YAML.

Previously this logic was duplicated in config.json, SKILL.md, and
run_intensive_test.py. This module is the canonical copy.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required: pip install pyyaml")

POLICY_PATH = Path(__file__).parent / "orchestration_policy.yaml"

_policy: dict | None = None


def _load_policy() -> dict:
    global _policy
    if _policy is None:
        with open(POLICY_PATH) as f:
            _policy = yaml.safe_load(f)
    return _policy


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------

def classify(log: dict) -> dict:
    """
    Rule-based attack classifier.  Mirrors honeypot_manager.cmd_classify exactly
    so that run_intensive_test.py and run_attacks.py can use this instead of
    shelling out to honeypot_manager.py just for classification.
    """
    policy = _load_policy()
    rules = policy["classification"]["blueprints"]
    threshold = policy["classification"]["confidence_threshold"]

    # Sanitize inputs (same caps as honeypot_manager._sanitize_log)
    events = log.get("events", [])
    if not isinstance(events, list):
        events = []
    events = [str(e)[:512] for e in events[:1000]]
    port = int(log.get("destination_port", 0))
    events_str = " ".join(events).lower()

    scores: dict[str, float] = {}

    for blueprint_name, rule in rules.items():
        score = 0.0
        if port in rule.get("ports", []):
            score += rule.get("port_score", 0)
        for kw in rule.get("keywords", []):
            if kw.lower() in events_str:
                score += rule.get("keyword_score", 0)
        for u in rule.get("usernames", []):
            if re.search(r'\b' + re.escape(u) + r'\b', events_str):
                score += rule.get("username_score", 0)
        for p in rule.get("paths", []):
            if p.lower() in events_str:
                score += rule.get("path_score", 0)
        scores[blueprint_name] = min(score, 1.0)

    best = max(scores, key=scores.get) if scores else "monitor_only"
    confidence = scores.get(best, 0.0)

    if confidence < threshold:
        suggested_blueprint = "monitor_only"
        attack_type = "Unknown"
        confidence = round(1.0 - confidence, 2)
    else:
        suggested_blueprint = best
        attack_type = "SSH Brute Force" if best == "ssh_bruteforce" else "Web Attack"
        confidence = round(confidence, 2)

    log_id = log.get("id", "unknown")
    return {
        "log_id": log_id,
        "attack_type": attack_type,
        "confidence": confidence,
        "suggested_blueprint": suggested_blueprint,
        "indicators": {
            "targeted_ports": [port],
            "event_count": len(events),
        }
    }


# ---------------------------------------------------------------------------
# decide_switch
# ---------------------------------------------------------------------------

def decide_switch(blueprint: str, logs_result: dict, current_mode: str) -> Optional[str]:
    """
    Evaluate switching rules for the given blueprint against the latest
    logs_result dict (as returned by honeypot_manager logs).

    Returns the mode to switch to, or None if no rule fires.
    Switching is idempotent: if the target mode equals current_mode, return None.
    """
    policy = _load_policy()
    rules = policy.get("switching", {}).get(blueprint, [])
    if not rules:
        return None

    new_events = logs_result.get("new_events", [])
    paths_visited = logs_result.get("paths_visited", {})

    for rule in rules:
        cond = rule.get("condition", {})
        target_mode = rule.get("target_mode")
        if target_mode == current_mode:
            continue  # already in this mode

        event_type = cond.get("event_type")
        field = cond.get("field")
        value = cond.get("value")        # single value
        values = cond.get("values", [])  # list of values
        min_visits = cond.get("min_visits", 1)

        if event_type == "login_attempt":
            for ev in new_events:
                if ev.get("type") != "login_attempt":
                    continue
                if field == "success" and ev.get("success") is True:
                    return target_mode
                if field == "username":
                    uname = ev.get("username", "").lower()
                    if uname in [v.lower() for v in values]:
                        return target_mode

        elif event_type == "connection":
            if field == "path":
                for path_pattern in values:
                    if paths_visited.get(path_pattern, 0) >= min_visits:
                        return target_mode
                # Also check new_events for paths not yet in paths_visited tally
                for ev in new_events:
                    if ev.get("path") in values:
                        if paths_visited.get(ev["path"], 0) >= min_visits:
                            return target_mode

    return None


# ---------------------------------------------------------------------------
# should_stop
# ---------------------------------------------------------------------------

def should_stop(logs_result: dict, post_switch_polls: int) -> bool:
    """Loop-exit predicate matching the original run_intensive_test.py logic."""
    policy = _load_policy()
    lc = policy.get("loop_control", {})
    max_steps = lc.get("max_steps", 10)
    collapse_threshold = lc.get("collapse_threshold", 0)
    collapse_min_steps = lc.get("collapse_min_steps", 3)
    min_polls = lc.get("min_polls_after_switch", 2)

    step = logs_result.get("step_count", 0)
    score = logs_result.get("engagement_score", 0)

    if step >= max_steps:
        return True
    if score <= collapse_threshold and step >= collapse_min_steps:
        return True
    if post_switch_polls >= min_polls and score < 2:
        return True
    return False


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) < 2:
        print("Usage: policy_engine.py <log.json>")
        sys.exit(1)
    with open(sys.argv[1]) as fh:
        log = json.load(fh)
    result = classify(log)
    print(json.dumps(result, indent=2))
