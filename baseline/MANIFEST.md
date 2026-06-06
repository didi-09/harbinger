# Baseline Asset Manifest  (#2)

This document enumerates the **identical decoy asset set** shared by both
the adaptive and static honeypot deployments, establishing that the baseline
comparison is fair: the only variable is **runtime adaptation**, not asset inventory.

---

## SSH Blueprint (`ssh_bruteforce`) — Decoy Assets

Both adaptive (after all switches) and static (at deploy time) contain exactly
the following files in the shared honeyfs volume:

| File Path (container-relative) | Template | Description |
|---|---|---|
| `home/admin/credentials.txt` | `decoys/credentials.txt.j2` | Fake admin credentials file |
| `var/backups/customer_db.sql` | `decoys/db_backup.sql.j2` | Fake database backup |
| `opt/scripts/backup_mysql.sh` | `decoys/backup_script.sh.j2` | Fake backup script with embedded creds |
| `home/admin/.bash_history` | `decoys/bash_history.j2` | Fake shell history with sensitive commands |
| `home/admin/.ssh/authorized_keys` | `decoys/authorized_keys.j2` | Fake authorized_keys with comment creds |
| `root/deploy.sh` | `decoys/deploy_script.j2` | Fake deployment script with API tokens |

**Adaptive deployment:** files written incrementally as attack behavior is observed
(expose_fake_backup mode: first 3 files; fake_admin_success mode: last 3 files).

**Static deployment:** all 6 files written at `deploy` time via `--static` flag.
`cmd_behavior` returns a no-op for the duration of the session.

---

## Web Blueprint (`web_attack`) — Decoy Assets

| File Path (container-relative) | Template | Description |
|---|---|---|
| `www/.env` | `decoys/env.j2` | Fake .env with DB credentials and API keys |
| `www/config.php.bak` | `decoys/config_php_bak.j2` | Fake PHP config backup with DB creds |
| `www/admin/dashboard.html` | `decoys/admin_dashboard.html.j2` | Fake admin dashboard HTML |
| `www/admin/users.json` | `decoys/admin_users.json.j2` | Fake user table with hashed passwords |

**Adaptive deployment:** expose_fake_config mode → .env + config.php.bak;
fake_admin_panel mode → dashboard.html + users.json.

**Static deployment:** all 4 files written at `deploy` time.

---

## Services (identical in both modes)

| Blueprint | Service | Image | Container port | Host port |
|---|---|---|---|---|
| `ssh_bruteforce` | Cowrie SSH | `cowrie/cowrie:latest` | 2222 | dynamic (from `host_ports["22"]`) |
| `web_attack` | Flask honeypot | `honeypot-flask:latest` | 5000 | dynamic (from `host_ports["80"]`) |

Both deployments use the same Docker image, same Jinja2-rendered templates, and same
dynamic port allocation.  The `--static` flag exclusively controls *when* decoy files are
written (deploy time vs. runtime), not *what* is written or *how* services behave.

---

## mtime Backdating

Both adaptive and static deployments apply random 3–30 day mtime/atime backdating
(`os.utime`) to all written decoy files so neither has a fingerprinting advantage from
timestamps.  See `honeypot_manager._write_behavior_files()`.
