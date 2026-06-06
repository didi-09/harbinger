#!/usr/bin/env python3
"""
msf_run.py — Wrapper to run Metasploit auxiliary modules via msfconsole resource scripts.
Usage: python3 msf_run.py <module_key> <host> <port>
Keys: ssh_login | http_dir | ssh_enum | http_login
"""
import subprocess
import sys
import tempfile
import os

host = sys.argv[2]
port = sys.argv[3]
key = sys.argv[1]

SCRIPTS = {
    "ssh_login": f"""
use auxiliary/scanner/ssh/ssh_login
set RHOSTS {host}
set RPORT {port}
set USERNAME root
set PASS_FILE /home/kali/llm-honeypot-openclaw/attacks/wordlists/top100_passwords.txt
set THREADS 4
set VERBOSE false
run
exit
""",
    "http_dir": f"""
use auxiliary/scanner/http/dir_scanner
set RHOSTS {host}
set RPORT {port}
set THREADS 10
set VERBOSE false
run
exit
""",
    "ssh_enum": f"""
use auxiliary/scanner/ssh/ssh_enumusers
set RHOSTS {host}
set RPORT {port}
set USER_FILE /home/kali/llm-honeypot-openclaw/attacks/wordlists/ssh_users.txt
set THREADS 4
set VERBOSE false
run
exit
""",
    "http_login": f"""
use auxiliary/scanner/http/http_login
set RHOSTS {host}
set RPORT {port}
set AUTH_URI /login
set REQUEST_TIMEOUT 5
set THREADS 4
set USERNAME admin
set PASS_FILE /home/kali/llm-honeypot-openclaw/attacks/wordlists/top100_passwords.txt
set VERBOSE false
run
exit
""",
}

script = SCRIPTS.get(key)
if not script:
    print(f"[msf] Unknown key: {key}", file=sys.stderr)
    sys.exit(1)

with tempfile.NamedTemporaryFile(mode="w", suffix=".rc", delete=False) as f:
    f.write(script)
    rc_path = f.name

try:
    print(f"[msf] Running module key={key} against {host}:{port}")
    subprocess.run(
        ["msfconsole", "-q", "-r", rc_path],
        timeout=300
    )
finally:
    os.unlink(rc_path)
