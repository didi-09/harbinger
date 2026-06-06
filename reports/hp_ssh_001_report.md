# Honeypot Incident Report — hp_ssh_001

**Generated:** 2026-05-12 00:41:25 UTC
**Blueprint:** ssh_bruteforce
**Session Start:** 2026-05-12T00:40:24
**Total Steps:** 8

---

## Attack Summary

| Field | Value |
|---|---|
| Session ID | hp_ssh_001 |
| Blueprint Deployed | ssh_bruteforce |
| Final Engagement Score | 269 |
| Total Events | 118 |
| Behavior Switches | 1 |

---

## Session Timeline

| # | Timestamp | Event Type | Detail | Score Δ |
|---|---|---|---|---|
| 1 | 2026-05-12T00:40:25 | connection | | 1 |
| 2 | 2026-05-12T00:40:25 | connection | | 1 |
| 3 | 2026-05-12T00:40:25 | login_attempt | user=root | 2 |
| 4 | 2026-05-12T00:40:25 | command_executed | cmd=id | 3 |
| 5 | 2026-05-12T00:40:25 | command_executed | cmd=uname -a | 3 |
| 6 | 2026-05-12T00:40:25 | command_executed | cmd=ls /home | 3 |
| 7 | 2026-05-12T00:40:26 | command_executed | cmd=ls /home/admin | 3 |
| 8 | 2026-05-12T00:40:26 | command_executed | cmd=cat /etc/passwd | 3 |
| 9 | 2026-05-12T00:40:27 | connection | | 1 |
| 10 | 2026-05-12T00:40:27 | login_attempt | user=root | 2 |
| 11 | 2026-05-12T00:40:29 | connection | | 1 |
| 12 | 2026-05-12T00:40:29 | login_attempt | user=root | 2 |
| 13 | 2026-05-12T00:40:29 | command_executed | cmd=id | 3 |
| 14 | 2026-05-12T00:40:29 | command_executed | cmd=uname -a | 3 |
| 15 | 2026-05-12T00:40:29 | command_executed | cmd=ls /home | 3 |
| 16 | 2026-05-12T00:40:29 | command_executed | cmd=ls /home/admin | 3 |
| 17 | 2026-05-12T00:40:29 | command_executed | cmd=cat /etc/passwd | 3 |
| 18 | 2026-05-12T00:40:30 | connection | | 1 |
| 19 | 2026-05-12T00:40:30 | login_attempt | user=root | 2 |
| 20 | 2026-05-12T00:40:30 | command_executed | cmd=id | 3 |
| 21 | 2026-05-12T00:40:30 | command_executed | cmd=uname -a | 3 |
| 22 | 2026-05-12T00:40:30 | command_executed | cmd=ls /home | 3 |
| 23 | 2026-05-12T00:40:30 | command_executed | cmd=ls /home/admin | 3 |
| 24 | 2026-05-12T00:40:30 | command_executed | cmd=cat /etc/passwd | 3 |
| 25 | 2026-05-12T00:40:31 | connection | | 1 |
| 26 | 2026-05-12T00:40:31 | login_attempt | user=root | 2 |
| 27 | 2026-05-12T00:40:31 | command_executed | cmd=id | 3 |
| 28 | 2026-05-12T00:40:31 | command_executed | cmd=uname -a | 3 |
| 29 | 2026-05-12T00:40:31 | command_executed | cmd=ls /home | 3 |
| 30 | 2026-05-12T00:40:31 | command_executed | cmd=ls /home/admin | 3 |
| 31 | 2026-05-12T00:40:32 | command_executed | cmd=cat /etc/passwd | 3 |
| 32 | 2026-05-12T00:40:33 | connection | | 1 |
| 33 | 2026-05-12T00:40:33 | login_attempt | user=root | 2 |
| 34 | 2026-05-12T00:40:33 | command_executed | cmd=id | 3 |
| 35 | 2026-05-12T00:40:33 | command_executed | cmd=uname -a | 3 |
| 36 | 2026-05-12T00:40:33 | command_executed | cmd=ls /home | 3 |
| 37 | 2026-05-12T00:40:33 | command_executed | cmd=ls /home/admin | 3 |
| 38 | 2026-05-12T00:40:33 | command_executed | cmd=cat /etc/passwd | 3 |
| 39 | 2026-05-12T00:40:34 | login_attempt | user=root | 2 |
| 40 | 2026-05-12T00:40:36 | connection | | 1 |
| 41 | 2026-05-12T00:40:36 | login_attempt | user=root | 2 |
| 42 | 2026-05-12T00:40:36 | command_executed | cmd=id | 3 |
| 43 | 2026-05-12T00:40:36 | command_executed | cmd=uname -a | 3 |
| 44 | 2026-05-12T00:40:36 | command_executed | cmd=ls /home | 3 |
| 45 | 2026-05-12T00:40:36 | command_executed | cmd=ls /home/admin | 3 |
| 46 | 2026-05-12T00:40:36 | command_executed | cmd=cat /etc/passwd | 3 |
| 47 | 2026-05-12T00:40:37 | connection | | 1 |
| 48 | 2026-05-12T00:40:37 | login_attempt | user=root | 2 |
| 49 | 2026-05-12T00:40:37 | command_executed | cmd=id | 3 |
| 50 | 2026-05-12T00:40:37 | command_executed | cmd=uname -a | 3 |
| 51 | 2026-05-12T00:40:37 | command_executed | cmd=ls /home | 3 |
| 52 | 2026-05-12T00:40:37 | command_executed | cmd=ls /home/admin | 3 |
| 53 | 2026-05-12T00:40:37 | command_executed | cmd=cat /etc/passwd | 3 |
| 54 | 2026-05-12T00:40:38 | connection | | 1 |
| 55 | 2026-05-12T00:40:39 | login_attempt | user=root | 2 |
| 56 | 2026-05-12T00:40:39 | command_executed | cmd=id | 3 |
| 57 | 2026-05-12T00:40:39 | command_executed | cmd=uname -a | 3 |
| 58 | 2026-05-12T00:40:39 | command_executed | cmd=ls /home | 3 |
| 59 | 2026-05-12T00:40:39 | command_executed | cmd=ls /home/admin | 3 |
| 60 | 2026-05-12T00:40:39 | command_executed | cmd=cat /etc/passwd | 3 |
| 61 | 2026-05-12T00:40:40 | connection | | 1 |
| 62 | 2026-05-12T00:40:40 | login_attempt | user=root | 2 |
| 63 | 2026-05-12T00:40:40 | command_executed | cmd=id | 3 |
| 64 | 2026-05-12T00:40:40 | command_executed | cmd=uname -a | 3 |
| 65 | 2026-05-12T00:40:40 | command_executed | cmd=ls /home | 3 |
| 66 | 2026-05-12T00:40:40 | command_executed | cmd=ls /home/admin | 3 |
| 67 | 2026-05-12T00:40:40 | command_executed | cmd=cat /etc/passwd | 3 |
| 68 | 2026-05-12T00:40:41 | connection | | 1 |
| 69 | 2026-05-12T00:40:41 | login_attempt | user=root | 2 |
| 70 | 2026-05-12T00:40:43 | connection | | 1 |
| 71 | 2026-05-12T00:40:43 | login_attempt | user=root | 2 |
| 72 | 2026-05-12T00:40:43 | command_executed | cmd=id | 3 |
| 73 | 2026-05-12T00:40:43 | command_executed | cmd=uname -a | 3 |
| 74 | 2026-05-12T00:40:43 | command_executed | cmd=ls /home | 3 |
| 75 | 2026-05-12T00:40:43 | command_executed | cmd=ls /home/admin | 3 |
| 76 | 2026-05-12T00:40:43 | command_executed | cmd=cat /etc/passwd | 3 |
| 77 | 2026-05-12T00:40:44 | connection | | 1 |
| 78 | 2026-05-12T00:40:44 | login_attempt | user=root | 2 |
| 79 | 2026-05-12T00:40:44 | command_executed | cmd=id | 3 |
| 80 | 2026-05-12T00:40:45 | command_executed | cmd=uname -a | 3 |
| 81 | 2026-05-12T00:40:45 | command_executed | cmd=ls /home | 3 |
| 82 | 2026-05-12T00:40:45 | command_executed | cmd=ls /home/admin | 3 |
| 83 | 2026-05-12T00:40:45 | command_executed | cmd=cat /etc/passwd | 3 |
| 84 | 2026-05-12T00:40:46 | connection | | 1 |
| 85 | 2026-05-12T00:40:46 | login_attempt | user=root | 2 |
| 86 | 2026-05-12T00:40:46 | command_executed | cmd=id | 3 |
| 87 | 2026-05-12T00:40:46 | command_executed | cmd=uname -a | 3 |
| 88 | 2026-05-12T00:40:46 | command_executed | cmd=ls /home | 3 |
| 89 | 2026-05-12T00:40:46 | command_executed | cmd=ls /home/admin | 3 |
| 90 | 2026-05-12T00:40:46 | command_executed | cmd=cat /etc/passwd | 3 |
| 91 | 2026-05-12T00:40:47 | connection | | 1 |
| 92 | 2026-05-12T00:40:47 | login_attempt | user=admin | 2 |
| 93 | 2026-05-12T00:40:49 | connection | | 1 |
| 94 | 2026-05-12T00:40:49 | login_attempt | user=admin | 2 |
| 95 | 2026-05-12T00:40:51 | connection | | 1 |
| 96 | 2026-05-12T00:40:51 | login_attempt | user=admin | 2 |
| 97 | 2026-05-12T00:40:53 | connection | | 1 |
| 98 | 2026-05-12T00:40:53 | login_attempt | user=admin | 2 |
| 99 | 2026-05-12T00:40:55 | connection | | 1 |
| 100 | 2026-05-12T00:40:55 | login_attempt | user=admin | 2 |
| 101 | 2026-05-12T00:40:57 | connection | | 1 |
| 102 | 2026-05-12T00:40:57 | login_attempt | user=admin | 2 |
| 103 | 2026-05-12T00:40:59 | connection | | 1 |
| 104 | 2026-05-12T00:40:59 | login_attempt | user=admin | 2 |
| 105 | 2026-05-12T00:41:01 | login_attempt | user=admin | 2 |
| 106 | 2026-05-12T00:41:03 | connection | | 1 |
| 107 | 2026-05-12T00:41:03 | login_attempt | user=admin | 2 |
| 108 | 2026-05-12T00:41:05 | login_attempt | user=admin | 2 |
| 109 | 2026-05-12T00:41:07 | connection | | 1 |
| 110 | 2026-05-12T00:41:08 | login_attempt | user=admin | 2 |
| 111 | 2026-05-12T00:41:10 | connection | | 1 |
| 112 | 2026-05-12T00:41:10 | login_attempt | user=admin | 2 |
| 113 | 2026-05-12T00:41:12 | login_attempt | user=admin | 2 |
| 114 | 2026-05-12T00:41:14 | connection | | 1 |
| 115 | 2026-05-12T00:41:14 | login_attempt | user=admin | 2 |
| 116 | 2026-05-12T00:41:16 | login_attempt | user=admin | 2 |
| 117 | 2026-05-12T00:41:18 | connection | | 1 |
| 118 | 2026-05-12T00:41:18 | login_attempt | user=backup | 2 |

---

## Behavior Switches

| When | Transition | Score at Switch | Timestamp |
|---|---|---|---|
| Step 1 | default → fake_admin_success | Score=94 | 2026-05-12T00:40:41 |

---

## Engagement Analysis

- **Final Score:** 269
- **Peak Engagement:** 269 (final)
- **Steps Monitored:** 8
- **Behavior Switches:** 1

---

## Collected Intelligence

**Usernames attempted:** root, admin, backup



---

## Deception Assessment

### Decoys Accessed

- None recorded

---

## Recommendation

HIGH engagement detected. Attacker deeply interacted with decoys. Recommend: collect all forensic artifacts, block source IP at perimeter, escalate to threat intel team.

---

*Generated by honeypot_manager.py — OpenClaw Honeypot Orchestration System*
