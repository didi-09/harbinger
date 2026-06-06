# Honeypot Incident Report — hp_real_ssh_hydra_backup

**Generated:** 2026-06-01 17:00:59 UTC
**Blueprint:** ssh_bruteforce
**Mode:** ADAPTIVE
**Session Start:** 2026-06-01T16:59:13
**Total Steps:** 10
**Host Ports:** {"22": "41665"}

---

## Attack Summary

| Field | Value |
|---|---|
| Session ID | hp_real_ssh_hydra_backup |
| Blueprint Deployed | ssh_bruteforce |
| Mode | ADAPTIVE |
| Final Engagement Score | 189 |
| Total Events | 106 |
| Behavior Switches | 1 |

---

## Session Timeline

| # | Timestamp | Event Type | Detail | Score Δ |
|---|---|---|---|---|
| 1 | 2026-06-01T16:59:17 | connection | | 1 |
| 2 | 2026-06-01T16:59:17 | connection | | 1 |
| 3 | 2026-06-01T16:59:17 | connection | | 1 |
| 4 | 2026-06-01T16:59:17 | connection | | 1 |
| 5 | 2026-06-01T16:59:17 | connection | | 1 |
| 6 | 2026-06-01T16:59:17 | login_attempt | user=backup | 2 |
| 7 | 2026-06-01T16:59:17 | login_attempt | user=backup | 2 |
| 8 | 2026-06-01T16:59:17 | login_attempt | user=backup | 2 |
| 9 | 2026-06-01T16:59:17 | login_attempt | user=backup | 2 |
| 10 | 2026-06-01T16:59:18 | login_attempt | user=backup | 2 |
| 11 | 2026-06-01T16:59:18 | login_attempt | user=backup | 2 |
| 12 | 2026-06-01T16:59:18 | login_attempt | user=backup | 2 |
| 13 | 2026-06-01T16:59:18 | login_attempt | user=backup | 2 |
| 14 | 2026-06-01T16:59:19 | login_attempt | user=backup | 2 |
| 15 | 2026-06-01T16:59:19 | login_attempt | user=backup | 2 |
| 16 | 2026-06-01T16:59:19 | login_attempt | user=backup | 2 |
| 17 | 2026-06-01T16:59:19 | login_attempt | user=backup | 2 |
| 18 | 2026-06-01T16:59:20 | login_attempt | user=backup | 2 |
| 19 | 2026-06-01T16:59:20 | login_attempt | user=backup | 2 |
| 20 | 2026-06-01T16:59:20 | login_attempt | user=backup | 2 |
| 21 | 2026-06-01T16:59:20 | login_attempt | user=backup | 2 |
| 22 | 2026-06-01T16:59:21 | login_attempt | user=backup | 2 |
| 23 | 2026-06-01T16:59:21 | login_attempt | user=backup | 2 |
| 24 | 2026-06-01T16:59:21 | login_attempt | user=backup | 2 |
| 25 | 2026-06-01T16:59:21 | login_attempt | user=backup | 2 |
| 26 | 2026-06-01T16:59:22 | login_attempt | user=backup | 2 |
| 27 | 2026-06-01T16:59:22 | login_attempt | user=backup | 2 |
| 28 | 2026-06-01T16:59:22 | login_attempt | user=backup | 2 |
| 29 | 2026-06-01T16:59:22 | login_attempt | user=backup | 2 |
| 30 | 2026-06-01T16:59:23 | login_attempt | user=backup | 2 |
| 31 | 2026-06-01T16:59:23 | login_attempt | user=backup | 2 |
| 32 | 2026-06-01T16:59:23 | login_attempt | user=backup | 2 |
| 33 | 2026-06-01T16:59:23 | login_attempt | user=backup | 2 |
| 34 | 2026-06-01T16:59:24 | login_attempt | user=backup | 2 |
| 35 | 2026-06-01T16:59:24 | login_attempt | user=backup | 2 |
| 36 | 2026-06-01T16:59:24 | login_attempt | user=backup | 2 |
| 37 | 2026-06-01T16:59:24 | login_attempt | user=backup | 2 |
| 38 | 2026-06-01T16:59:25 | login_attempt | user=backup | 2 |
| 39 | 2026-06-01T16:59:25 | login_attempt | user=backup | 2 |
| 40 | 2026-06-01T16:59:25 | login_attempt | user=backup | 2 |
| 41 | 2026-06-01T16:59:25 | login_attempt | user=backup | 2 |
| 42 | 2026-06-01T16:59:26 | login_attempt | user=backup | 2 |
| 43 | 2026-06-01T16:59:26 | login_attempt | user=backup | 2 |
| 44 | 2026-06-01T16:59:26 | login_attempt | user=backup | 2 |
| 45 | 2026-06-01T16:59:26 | login_attempt | user=backup | 2 |
| 46 | 2026-06-01T16:59:27 | login_attempt | user=backup | 2 |
| 47 | 2026-06-01T16:59:27 | login_attempt | user=backup | 2 |
| 48 | 2026-06-01T16:59:27 | login_attempt | user=backup | 2 |
| 49 | 2026-06-01T16:59:27 | login_attempt | user=backup | 2 |
| 50 | 2026-06-01T16:59:28 | login_attempt | user=backup | 2 |
| 51 | 2026-06-01T16:59:28 | login_attempt | user=backup | 2 |
| 52 | 2026-06-01T16:59:28 | login_attempt | user=backup | 2 |
| 53 | 2026-06-01T16:59:28 | login_attempt | user=backup | 2 |
| 54 | 2026-06-01T16:59:29 | login_attempt | user=backup | 2 |
| 55 | 2026-06-01T16:59:29 | login_attempt | user=backup | 2 |
| 56 | 2026-06-01T16:59:29 | login_attempt | user=backup | 2 |
| 57 | 2026-06-01T16:59:29 | login_attempt | user=backup | 2 |
| 58 | 2026-06-01T16:59:30 | login_attempt | user=backup | 2 |
| 59 | 2026-06-01T16:59:30 | login_attempt | user=backup | 2 |
| 60 | 2026-06-01T16:59:30 | login_attempt | user=backup | 2 |
| 61 | 2026-06-01T16:59:30 | login_attempt | user=backup | 2 |
| 62 | 2026-06-01T16:59:31 | login_attempt | user=backup | 2 |
| 63 | 2026-06-01T16:59:31 | login_attempt | user=backup | 2 |
| 64 | 2026-06-01T16:59:31 | login_attempt | user=backup | 2 |
| 65 | 2026-06-01T16:59:31 | login_attempt | user=backup | 2 |
| 66 | 2026-06-01T16:59:32 | login_attempt | user=backup | 2 |
| 67 | 2026-06-01T16:59:32 | login_attempt | user=backup | 2 |
| 68 | 2026-06-01T16:59:32 | login_attempt | user=backup | 2 |
| 69 | 2026-06-01T16:59:32 | login_attempt | user=backup | 2 |
| 70 | 2026-06-01T16:59:33 | login_attempt | user=backup | 2 |
| 71 | 2026-06-01T16:59:33 | login_attempt | user=backup | 2 |
| 72 | 2026-06-01T16:59:33 | login_attempt | user=backup | 2 |
| 73 | 2026-06-01T16:59:33 | login_attempt | user=backup | 2 |
| 74 | 2026-06-01T16:59:34 | login_attempt | user=backup | 2 |
| 75 | 2026-06-01T16:59:34 | login_attempt | user=backup | 2 |
| 76 | 2026-06-01T16:59:34 | login_attempt | user=backup | 2 |
| 77 | 2026-06-01T16:59:34 | login_attempt | user=backup | 2 |
| 78 | 2026-06-01T16:59:35 | login_attempt | user=backup | 2 |
| 79 | 2026-06-01T16:59:35 | login_attempt | user=backup | 2 |
| 80 | 2026-06-01T16:59:35 | login_attempt | user=backup | 2 |
| 81 | 2026-06-01T16:59:35 | login_attempt | user=backup | 2 |
| 82 | 2026-06-01T16:59:36 | login_attempt | user=backup | 2 |
| 83 | 2026-06-01T16:59:36 | login_attempt | user=backup | 2 |
| 84 | 2026-06-01T16:59:36 | login_attempt | user=backup | 2 |
| 85 | 2026-06-01T16:59:36 | login_attempt | user=backup | 2 |
| 86 | 2026-06-01T16:59:37 | login_attempt | user=backup | 2 |
| 87 | 2026-06-01T16:59:37 | login_attempt | user=backup | 2 |
| 88 | 2026-06-01T16:59:37 | login_attempt | user=backup | 2 |
| 89 | 2026-06-01T16:59:37 | login_attempt | user=backup | 2 |
| 90 | 2026-06-01T16:59:38 | connection | | 1 |
| 91 | 2026-06-01T16:59:38 | connection | | 1 |
| 92 | 2026-06-01T16:59:38 | connection | | 1 |
| 93 | 2026-06-01T16:59:38 | connection | | 1 |
| 94 | 2026-06-01T16:59:38 | login_attempt | user=backup | 2 |
| 95 | 2026-06-01T16:59:39 | login_attempt | user=backup | 2 |
| 96 | 2026-06-01T16:59:39 | login_attempt | user=backup | 2 |
| 97 | 2026-06-01T16:59:39 | login_attempt | user=backup | 2 |
| 98 | 2026-06-01T16:59:39 | login_attempt | user=backup | 2 |
| 99 | 2026-06-01T16:59:40 | login_attempt | user=backup | 2 |
| 100 | 2026-06-01T16:59:40 | login_attempt | user=backup | 2 |
| 101 | 2026-06-01T16:59:40 | login_attempt | user=backup | 2 |
| 102 | 2026-06-01T16:59:40 | login_attempt | user=backup | 2 |
| 103 | 2026-06-01T16:59:41 | login_attempt | user=backup | 2 |
| 104 | 2026-06-01T16:59:41 | login_attempt | user=backup | 2 |
| 105 | 2026-06-01T16:59:41 | login_attempt | user=backup | 2 |
| 106 | 2026-06-01T16:59:41 | login_attempt | user=backup | 2 |

---

## Behavior Switches

| When | Transition | Score at Switch | Latency | Timestamp |
|---|---|---|---|---|
| Step 1 | default → expose_fake_backup | Score=53 | total=5047.34ms | 2026-06-01T16:59:28 |

---

## Engagement Analysis

- **Final Score:** 189
- **Peak Engagement:** 189 (final)
- **Steps Monitored:** 10
- **Behavior Switches:** 1

---

## Collected Intelligence

**Usernames attempted:** backup



---

## Deception Assessment

### Decoys Accessed

- None recorded

---

## Recommendation

HIGH engagement detected. Attacker deeply interacted with decoys. Recommend: collect all forensic artifacts, block source IP at perimeter, escalate to threat intel team.

---

*Generated by honeypot_manager.py — OpenClaw Honeypot Orchestration System*
