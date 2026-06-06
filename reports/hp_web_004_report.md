# Honeypot Incident Report — hp_web_004

**Generated:** 2026-05-12 01:01:05 UTC
**Blueprint:** web_attack
**Session Start:** 2026-05-12T01:00:24
**Total Steps:** 8

---

## Attack Summary

| Field | Value |
|---|---|
| Session ID | hp_web_004 |
| Blueprint Deployed | web_attack |
| Final Engagement Score | 69 |
| Total Events | 60 |
| Behavior Switches | 2 |

---

## Session Timeline

| # | Timestamp | Event Type | Detail | Score Δ |
|---|---|---|---|---|
| 1 | 2026-05-12T01:00:26 | connection | path=/.env | 1 |
| 2 | 2026-05-12T01:00:26 | connection | path=/config.php.bak | 1 |
| 3 | 2026-05-12T01:00:26 | connection | path=/backup/db.sql | 1 |
| 4 | 2026-05-12T01:00:27 | login_attempt | path=/admin | 2 |
| 5 | 2026-05-12T01:00:27 | login_attempt | path=/login | 2 |
| 6 | 2026-05-12T01:00:27 | connection | path=/admin/users | 1 |
| 7 | 2026-05-12T01:00:27 | connection | path=/admin/dashboard | 1 |
| 8 | 2026-05-12T01:00:28 | connection | path=/wp-admin | 1 |
| 9 | 2026-05-12T01:00:28 | connection | path=/phpmyadmin | 1 |
| 10 | 2026-05-12T01:00:28 | connection | path=/.git/config | 1 |
| 11 | 2026-05-12T01:00:29 | connection | path=/backup | 1 |
| 12 | 2026-05-12T01:00:29 | connection | path=/config | 1 |
| 13 | 2026-05-12T01:00:29 | connection | path=/.env | 1 |
| 14 | 2026-05-12T01:00:30 | connection | path=/config.php.bak | 1 |
| 15 | 2026-05-12T01:00:30 | connection | path=/backup/db.sql | 1 |
| 16 | 2026-05-12T01:00:30 | login_attempt | path=/admin | 2 |
| 17 | 2026-05-12T01:00:30 | login_attempt | path=/login | 2 |
| 18 | 2026-05-12T01:00:31 | connection | path=/admin/users | 1 |
| 19 | 2026-05-12T01:00:31 | connection | path=/admin/dashboard | 1 |
| 20 | 2026-05-12T01:00:31 | connection | path=/wp-admin | 1 |
| 21 | 2026-05-12T01:00:32 | connection | path=/phpmyadmin | 1 |
| 22 | 2026-05-12T01:00:32 | connection | path=/.git/config | 1 |
| 23 | 2026-05-12T01:00:32 | connection | path=/backup | 1 |
| 24 | 2026-05-12T01:00:33 | connection | path=/config | 1 |
| 25 | 2026-05-12T01:00:33 | connection | path=/.env | 1 |
| 26 | 2026-05-12T01:00:33 | connection | path=/config.php.bak | 1 |
| 27 | 2026-05-12T01:00:33 | connection | path=/backup/db.sql | 1 |
| 28 | 2026-05-12T01:00:34 | login_attempt | path=/admin | 2 |
| 29 | 2026-05-12T01:00:34 | login_attempt | path=/login | 2 |
| 30 | 2026-05-12T01:00:34 | connection | path=/admin/users | 1 |
| 31 | 2026-05-12T01:00:35 | connection | path=/admin/dashboard | 1 |
| 32 | 2026-05-12T01:00:35 | connection | path=/wp-admin | 1 |
| 33 | 2026-05-12T01:00:35 | connection | path=/phpmyadmin | 1 |
| 34 | 2026-05-12T01:00:36 | connection | path=/.git/config | 1 |
| 35 | 2026-05-12T01:00:36 | connection | path=/backup | 1 |
| 36 | 2026-05-12T01:00:36 | connection | path=/config | 1 |
| 37 | 2026-05-12T01:00:37 | connection | path=/.env | 1 |
| 38 | 2026-05-12T01:00:37 | file_read | path=/config.php.bak | 4 |
| 39 | 2026-05-12T01:00:37 | connection | path=/backup/db.sql | 1 |
| 40 | 2026-05-12T01:00:37 | login_attempt | path=/admin | 2 |
| 41 | 2026-05-12T01:00:38 | login_attempt | path=/login | 2 |
| 42 | 2026-05-12T01:00:38 | connection | path=/admin/users | 1 |
| 43 | 2026-05-12T01:00:38 | connection | path=/admin/dashboard | 1 |
| 44 | 2026-05-12T01:00:39 | connection | path=/wp-admin | 1 |
| 45 | 2026-05-12T01:00:39 | connection | path=/phpmyadmin | 1 |
| 46 | 2026-05-12T01:00:39 | connection | path=/.git/config | 1 |
| 47 | 2026-05-12T01:00:40 | connection | path=/backup | 1 |
| 48 | 2026-05-12T01:00:40 | connection | path=/config | 1 |
| 49 | 2026-05-12T01:00:40 | file_read | path=/.env | 4 |
| 50 | 2026-05-12T01:00:40 | file_read | path=/config.php.bak | 4 |
| 51 | 2026-05-12T01:00:41 | connection | path=/backup/db.sql | 1 |
| 52 | 2026-05-12T01:00:41 | login_attempt | path=/admin | 2 |
| 53 | 2026-05-12T01:00:41 | login_attempt | path=/login | 2 |
| 54 | 2026-05-12T01:00:42 | connection | path=/admin/users | 1 |
| 55 | 2026-05-12T01:00:42 | connection | path=/admin/dashboard | 1 |
| 56 | 2026-05-12T01:00:42 | connection | path=/wp-admin | 1 |
| 57 | 2026-05-12T01:00:43 | connection | path=/phpmyadmin | 1 |
| 58 | 2026-05-12T01:00:43 | connection | path=/.git/config | 1 |
| 59 | 2026-05-12T01:00:43 | connection | path=/backup | 1 |
| 60 | 2026-05-12T01:00:43 | connection | path=/config | 1 |

---

## Behavior Switches

| When | Transition | Score at Switch | Timestamp |
|---|---|---|---|
| Step 1 | default → expose_fake_config | Score=12 | 2026-05-12T01:00:37 |
| Step 2 | expose_fake_config → fake_admin_panel | Score=68 | 2026-05-12T01:00:48 |

---

## Engagement Analysis

- **Final Score:** 69
- **Peak Engagement:** 69 (final)
- **Steps Monitored:** 8
- **Behavior Switches:** 2

---

## Collected Intelligence

**Paths probed (top 5):**
- /.env: 5 hits
- /config.php.bak: 5 hits
- /backup/db.sql: 5 hits
- /admin: 5 hits
- /login: 5 hits

---

## Deception Assessment

### Decoys Accessed

- /config.php.bak (file_read)
- /.env (file_read)
- /config.php.bak (file_read)

---

## Recommendation

HIGH engagement detected. Attacker deeply interacted with decoys. Recommend: collect all forensic artifacts, block source IP at perimeter, escalate to threat intel team.

---

*Generated by honeypot_manager.py — OpenClaw Honeypot Orchestration System*
