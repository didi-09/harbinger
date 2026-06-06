#!/usr/bin/env python3
"""
Flask honeypot — serves a fake corporate web app.

Behavior is controlled entirely by files in /app/honeyfs/:
  honeyfs/www/.env              → serve on GET /.env
  honeyfs/www/config.php.bak   → serve on GET /config.php.bak
  honeyfs/www/admin/dashboard.html → serve after fake login succeeds
  honeyfs/www/admin/users.json → serve on GET /admin/users

All requests are logged as JSON to /app/logs/requests.json (one line per event).
The manager reads this file to compute engagement scores.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, request, Response, send_file

app = Flask(__name__)

HONEYFS = Path("/app/honeyfs/www")
LOG_FILE = Path("/app/logs/requests.json")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Paths that trigger "config leak" mode when they exist in honeyfs
CONFIG_PATHS = {
    "/.env": "www/.env",
    "/config.php.bak": "www/config.php.bak",
    "/backup/db.sql": "www/backup/db.sql",
}

# Paths that trigger "admin panel" mode when they exist in honeyfs
ADMIN_PATHS = {
    "/admin/dashboard": "www/admin/dashboard.html",
    "/admin/users": "www/admin/users.json",
}


def log_event(event_type: str, extra: dict = None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": request.method,
        "path": request.path,
        "remote_addr": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", ""),
        "status": extra.get("status", 200) if extra else 200,
    }
    if extra:
        entry.update(extra)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def honeyfs_file(relative: str) -> Path:
    return HONEYFS.parent / relative


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    log_event("connection", {"status": 200})
    return "<html><body><h1>Corp Internal Portal</h1><a href='/login'>Login</a></body></html>", 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        log_event("login_attempt", {"status": 401, "username": request.form.get("username", "")})
        # Check if fake_admin_panel mode is active
        dashboard = honeyfs_file("www/admin/dashboard.html")
        if dashboard.exists():
            log_event("login_attempt", {"status": 302, "success": True})
            return Response(
                dashboard.read_text(),
                status=200,
                mimetype="text/html"
            )
        return "<html><body><h1>401 Unauthorized</h1></body></html>", 401
    log_event("connection", {"status": 200})
    return """<html><body>
<h1>Login</h1>
<form method=POST>
Username: <input name=username><br>
Password: <input name=password type=password><br>
<input type=submit value=Login>
</form></body></html>""", 200


@app.route("/admin", methods=["GET", "POST"])
def admin():
    log_event("login_attempt", {"status": 401})
    dashboard = honeyfs_file("www/admin/dashboard.html")
    if dashboard.exists():
        log_event("login_attempt", {"status": 200, "success": True})
        return Response(dashboard.read_text(), status=200, mimetype="text/html")
    return "<html><body><h1>403 Forbidden</h1></body></html>", 403


@app.route("/admin/dashboard")
def admin_dashboard():
    f = honeyfs_file("www/admin/dashboard.html")
    if f.exists():
        log_event("file_read", {"status": 200, "file_read": str(f)})
        return Response(f.read_text(), status=200, mimetype="text/html")
    log_event("connection", {"status": 404})
    return "Not Found", 404


@app.route("/admin/users")
def admin_users():
    f = honeyfs_file("www/admin/users.json")
    if f.exists():
        log_event("file_read", {"status": 200, "file_read": str(f)})
        return Response(f.read_text(), status=200, mimetype="application/json")
    log_event("connection", {"status": 404})
    return "Not Found", 404


@app.route("/.env")
def env_file():
    f = honeyfs_file("www/.env")
    if f.exists():
        log_event("file_read", {"status": 200, "file_read": str(f)})
        return Response(f.read_text(), status=200, mimetype="text/plain")
    log_event("connection", {"status": 404})
    return "Not Found", 404


@app.route("/config.php.bak")
def config_bak():
    f = honeyfs_file("www/config.php.bak")
    if f.exists():
        log_event("file_read", {"status": 200, "file_read": str(f)})
        return Response(f.read_text(), status=200, mimetype="text/plain")
    log_event("connection", {"status": 404})
    return "Not Found", 404


@app.route("/backup/db.sql")
def db_backup():
    f = honeyfs_file("www/backup/db.sql")
    if f.exists():
        log_event("file_download", {"status": 200, "file_download": str(f)})
        return Response(f.read_text(), status=200, mimetype="text/plain")
    log_event("connection", {"status": 404})
    return "Not Found", 404


@app.route("/wp-admin")
@app.route("/phpmyadmin")
@app.route("/config")
@app.route("/backup")
def common_probe():
    log_event("connection", {"status": 404})
    return "Not Found", 404


# Catch all other paths
@app.errorhandler(404)
def not_found(e):
    log_event("connection", {"status": 404})
    return "Not Found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
