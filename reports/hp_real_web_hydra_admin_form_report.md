# Honeypot Incident Report — hp_real_web_hydra_admin_form

**Generated:** 2026-06-01 17:36:29 UTC
**Blueprint:** web_attack
**Mode:** ADAPTIVE
**Session Start:** 2026-06-01T17:34:47
**Total Steps:** 10
**Host Ports:** {"80": "37359"}

---

## Attack Summary

| Field | Value |
|---|---|
| Session ID | hp_real_web_hydra_admin_form |
| Blueprint Deployed | web_attack |
| Mode | ADAPTIVE |
| Final Engagement Score | 91 |
| Total Events | 71 |
| Behavior Switches | 1 |

---

## Session Timeline

| # | Timestamp | Event Type | Detail | Score Δ |
|---|---|---|---|---|
| 1 | 2026-06-01T17:34:52 | connection | path=/admin | 1 |
| 2 | 2026-06-01T17:34:52 | connection | path=/admin | 1 |
| 3 | 2026-06-01T17:34:52 | connection | path=/admin | 1 |
| 4 | 2026-06-01T17:34:52 | connection | path=/admin | 1 |
| 5 | 2026-06-01T17:34:53 | login_attempt | path=/admin | 2 |
| 6 | 2026-06-01T17:34:53 | login_attempt | path=/admin | 2 |
| 7 | 2026-06-01T17:34:53 | login_attempt | path=/admin | 2 |
| 8 | 2026-06-01T17:34:53 | login_attempt | path=/admin | 2 |
| 9 | 2026-06-01T17:34:53 | connection | path=/admin | 1 |
| 10 | 2026-06-01T17:34:53 | connection | path=/admin | 1 |
| 11 | 2026-06-01T17:34:53 | connection | path=/admin | 1 |
| 12 | 2026-06-01T17:34:53 | connection | path=/admin | 1 |
| 13 | 2026-06-01T17:34:53 | login_attempt | path=/admin | 2 |
| 14 | 2026-06-01T17:34:53 | login_attempt | path=/admin | 2 |
| 15 | 2026-06-01T17:34:54 | login_attempt | path=/admin | 2 |
| 16 | 2026-06-01T17:34:54 | login_attempt | path=/admin | 2 |
| 17 | 2026-06-01T17:34:54 | connection | path=/admin | 1 |
| 18 | 2026-06-01T17:34:54 | connection | path=/admin | 1 |
| 19 | 2026-06-01T17:34:54 | connection | path=/admin | 1 |
| 20 | 2026-06-01T17:34:54 | connection | path=/admin | 1 |
| 21 | 2026-06-01T17:34:54 | login_attempt | path=/admin | 2 |
| 22 | 2026-06-01T17:34:54 | login_attempt | path=/admin | 2 |
| 23 | 2026-06-01T17:34:54 | login_attempt | path=/admin | 2 |
| 24 | 2026-06-01T17:34:54 | login_attempt | path=/admin | 2 |
| 25 | 2026-06-01T17:34:55 | connection | path=/admin | 1 |
| 26 | 2026-06-01T17:34:55 | connection | path=/admin | 1 |
| 27 | 2026-06-01T17:34:55 | connection | path=/admin | 1 |
| 28 | 2026-06-01T17:34:55 | connection | path=/admin | 1 |
| 29 | 2026-06-01T17:34:55 | login_attempt | path=/admin | 2 |
| 30 | 2026-06-01T17:34:55 | login_attempt | path=/admin | 2 |
| 31 | 2026-06-01T17:34:55 | login_attempt | path=/admin | 2 |
| 32 | 2026-06-01T17:34:55 | login_attempt | path=/admin | 2 |
| 33 | 2026-06-01T17:34:55 | connection | path=/admin | 1 |
| 34 | 2026-06-01T17:34:56 | connection | path=/admin | 1 |
| 35 | 2026-06-01T17:34:56 | connection | path=/admin | 1 |
| 36 | 2026-06-01T17:34:56 | connection | path=/admin | 1 |
| 37 | 2026-06-01T17:34:56 | login_attempt | path=/admin | 2 |
| 38 | 2026-06-01T17:34:56 | login_attempt | path=/admin | 2 |
| 39 | 2026-06-01T17:34:56 | login_attempt | path=/admin | 2 |
| 40 | 2026-06-01T17:34:56 | login_attempt | path=/admin | 2 |
| 41 | 2026-06-01T17:34:56 | connection | path=/admin | 1 |
| 42 | 2026-06-01T17:34:56 | connection | path=/admin | 1 |
| 43 | 2026-06-01T17:34:56 | connection | path=/admin | 1 |
| 44 | 2026-06-01T17:34:57 | connection | path=/admin | 1 |
| 45 | 2026-06-01T17:34:57 | login_attempt | path=/admin | 2 |
| 46 | 2026-06-01T17:34:57 | login_attempt | path=/admin | 2 |
| 47 | 2026-06-01T17:34:57 | login_attempt | path=/admin | 2 |
| 48 | 2026-06-01T17:34:57 | login_attempt | path=/admin | 2 |
| 49 | 2026-06-01T17:34:57 | connection | path=/admin | 1 |
| 50 | 2026-06-01T17:34:57 | connection | path=/admin | 1 |
| 51 | 2026-06-01T17:34:57 | connection | path=/admin | 1 |
| 52 | 2026-06-01T17:34:57 | connection | path=/admin | 1 |
| 53 | 2026-06-01T17:34:58 | login_attempt | path=/admin | 2 |
| 54 | 2026-06-01T17:34:58 | login_attempt | path=/admin | 2 |
| 55 | 2026-06-01T17:34:58 | login_attempt | path=/admin | 2 |
| 56 | 2026-06-01T17:34:58 | login_attempt | path=/admin | 2 |
| 57 | 2026-06-01T17:34:58 | connection | path=/admin | 1 |
| 58 | 2026-06-01T17:34:58 | connection | path=/admin | 1 |
| 59 | 2026-06-01T17:34:58 | connection | path=/admin | 1 |
| 60 | 2026-06-01T17:34:58 | connection | path=/admin | 1 |
| 61 | 2026-06-01T17:34:58 | connection | path=/admin | 1 |
| 62 | 2026-06-01T17:34:58 | connection | path=/admin | 1 |
| 63 | 2026-06-01T17:34:58 | connection | path=/admin | 1 |
| 64 | 2026-06-01T17:34:58 | login_attempt | path=/admin | 2 |
| 65 | 2026-06-01T17:34:58 | login_attempt | path=/admin | 2 |
| 66 | 2026-06-01T17:34:58 | login_attempt | path=/admin | 2 |
| 67 | 2026-06-01T17:34:58 | login_attempt | path=/admin | 2 |
| 68 | 2026-06-01T17:34:59 | login_attempt | path=/admin | 2 |
| 69 | 2026-06-01T17:34:59 | login_attempt | path=/admin | 2 |
| 70 | 2026-06-01T17:34:59 | login_attempt | path=/admin | 2 |
| 71 | 2026-06-01T17:34:59 | login_attempt | path=/admin | 2 |

---

## Behavior Switches

| When | Transition | Score at Switch | Latency | Timestamp |
|---|---|---|---|---|
| Step 1 | default → fake_admin_panel | Score=84 | total=49.24ms | 2026-06-01T17:34:58 |

---

## Engagement Analysis

- **Final Score:** 91
- **Peak Engagement:** 91 (final)
- **Steps Monitored:** 10
- **Behavior Switches:** 1

---

## Collected Intelligence

**Paths probed (top 5):**
- /admin: 71 hits

---

## Deception Assessment

### Decoys Accessed

- None recorded

---

## Recommendation

HIGH engagement detected. Attacker deeply interacted with decoys. Recommend: collect all forensic artifacts, block source IP at perimeter, escalate to threat intel team.

---

*Generated by honeypot_manager.py — OpenClaw Honeypot Orchestration System*
