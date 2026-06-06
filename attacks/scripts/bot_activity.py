#!/usr/bin/env python3
"""
bot_activity.py — Simulated bot traffic: random UA rotation, rapid GET/POST bursts.
Usage: python3 bot_activity.py <host> <port>
"""
import sys, time, random, requests
from requests.exceptions import RequestException

host = sys.argv[1]
port = int(sys.argv[2])
base = f"http://{host}:{port}"

UAS = [
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "curl/7.68.0",
    "python-requests/2.25.1",
    "masscan/1.0",
    "zgrab/0.x",
    "Go-http-client/1.1",
    "libwww-perl/6.43",
    "Mozilla/5.0 (compatible; Baiduspider/2.0)",
    "Mozilla/5.0 (compatible; DotBot/1.1)",
    "Mozilla/5.0 (compatible; SemrushBot/7)",
]

PATHS_GET = [
    "/", "/admin", "/login", "/dashboard", "/.env", "/config",
    "/backup", "/config.php.bak", "/backup/db.sql", "/wp-admin",
    "/phpmyadmin", "/admin/users", "/admin/dashboard",
    "/robots.txt", "/sitemap.xml", "/.git/config",
]

PATHS_POST = ["/login", "/admin"]

def req(method, path, data=None):
    try:
        s = requests.Session()
        s.headers["User-Agent"] = random.choice(UAS)
        if method == "POST":
            r = s.post(base + path, data=data, timeout=4)
        else:
            r = s.get(base + path, timeout=4)
        print(f"[bot] {method:4s} {path} → {r.status_code}")
    except RequestException as e:
        print(f"[bot] {method:4s} {path} → ERR")

# 3 rounds of mixed traffic
for _ in range(3):
    for path in random.sample(PATHS_GET, min(8, len(PATHS_GET))):
        req("GET", path)
        time.sleep(random.uniform(0.1, 0.4))
    for path in PATHS_POST:
        req("POST", path, {"username": "admin", "password": random.choice(["admin", "password", "123456"])})
        time.sleep(0.2)
