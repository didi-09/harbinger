#!/usr/bin/env python3
"""
curl_admin_probe.py — Real web-attack traffic via requests.
Hits /admin ≥2x, /login POSTs, then probes config paths.
Usage: python3 curl_admin_probe.py <host> <port>
"""
import sys, time, requests
from requests.exceptions import RequestException

host = sys.argv[1]
port = int(sys.argv[2])
base = f"http://{host}:{port}"
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (compatible; CustomScanner/1.0)"

def get(path, **kw):
    try:
        r = s.get(base + path, timeout=5, **kw)
        print(f"[probe] GET  {path} → {r.status_code}")
    except RequestException as e:
        print(f"[probe] GET  {path} → ERR {e}")

def post(path, data, **kw):
    try:
        r = s.post(base + path, data=data, timeout=5, **kw)
        print(f"[probe] POST {path} → {r.status_code}")
    except RequestException as e:
        print(f"[probe] POST {path} → ERR {e}")

# Admin panel probing (≥2 visits to /admin to trigger fake_admin_panel)
for _ in range(3):
    get("/admin")
    time.sleep(0.3)

# Login brute (trigger fake_admin_panel via /login repeated POST)
for pw in ["admin", "password", "admin123", "letmein", "root"]:
    post("/login", {"username": "admin", "password": pw})
    time.sleep(0.2)

# Config file enumeration (trigger expose_fake_config)
for path in ["/.env", "/config.php.bak", "/backup/db.sql", "/config", "/backup"]:
    get(path)
    time.sleep(0.2)

# Dashboard access attempts
get("/admin/dashboard")
get("/admin/users")
get("/wp-admin")
get("/phpmyadmin")
