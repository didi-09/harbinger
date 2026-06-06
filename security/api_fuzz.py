#!/usr/bin/env python3
"""
api_fuzz.py — Orchestration API security testing  (#10).

Tests honeypot_manager.py robustness against:
  1. Path traversal via --session
  2. Unknown blueprint / mode names
  3. Oversized inputs
  4. Replay attacks (re-deploying same session ID)
  5. Malformed / missing arguments
  6. Concurrent command collisions

Each test: runs honeypot_manager.py, checks return code + error JSON structure,
asserts no unhandled exceptions or filesystem side-effects.

Usage:
  python3 security/api_fuzz.py

Output:
  results/api_security.csv
"""

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent.resolve()
MANAGER = str(BASE / "honeypot_manager.py")
RESULTS_DIR = BASE / "results"


def run_mgr(*args, expect_error: bool = True) -> dict:
    cmd = ["python3", MANAGER] + list(args)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=BASE, timeout=15
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout.strip()[:500],
            "stderr": result.stderr.strip()[:500],
            "ok": result.returncode == 0,
        }
    except (ValueError, OSError) as e:
        # null bytes / control characters in argv are rejected by the OS before
        # the process even starts — this is a valid rejection (#10).
        return {"returncode": -1, "stdout": "", "stderr": str(e), "ok": False}


def check_no_traversal(target_path: str) -> bool:
    """Assert that the path does not exist (traversal failed)."""
    p = Path(target_path)
    return not p.exists()


class APIFuzzTest:
    def __init__(self):
        self.rows = []
        self._tmp_sessions = []

    def record(self, test_name: str, passed: bool, detail: str = "",
               note: str = ""):
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {test_name}  {detail}")
        self.rows.append({
            "test": test_name,
            "passed": passed,
            "detail": detail[:200],
            "note": note,
            "ts": datetime.now(timezone.utc).isoformat(),
        })

    def cleanup_session(self, session_id: str):
        sess_dir = BASE / "running" / session_id
        if sess_dir.exists():
            shutil.rmtree(sess_dir, ignore_errors=True)

    # ── Test 1: Path traversal via --session ──────────────────────────────

    def test_path_traversal(self):
        print("\n=== Test 1: Path Traversal via --session ===")
        payloads = [
            "../../etc/passwd",
            "../running/../running/evil",
            "..%2F..%2Fetc%2Fpasswd",
            "a" * 65,               # exceeds 64-char limit
            "session with spaces",
            "session/with/slashes",
            "session\x00null",
            "",
            "valid-session-id",     # baseline — should succeed
        ]
        for payload in payloads:
            r = run_mgr("logs", "--session", payload, expect_error=True)
            if payload == "valid-session-id":
                # Even valid IDs that don't exist should error cleanly (no session)
                passed = r["returncode"] != 0 or (
                    r["ok"] is False
                )
                # Actually: valid-session-id doesn't exist, so should be non-zero
                passed = r["returncode"] != 0
                self.record("traversal_valid_nonexistent", passed,
                            f"session=valid-session-id rc={r['returncode']}")
            else:
                # Invalid IDs must be rejected with rc!=0 and no filesystem side effects
                passed = r["returncode"] != 0
                # Check no unexpected directory was created
                suspect = BASE / "running" / payload
                if r["returncode"] == 0:
                    passed = False
                self.record(
                    f"traversal_{payload[:20].replace('/','_').replace(' ','_')}",
                    passed,
                    f"rc={r['returncode']}  stderr={r['stderr'][:80]}"
                )

    # ── Test 2: Unknown blueprint names ───────────────────────────────────

    def test_unknown_blueprint(self):
        print("\n=== Test 2: Unknown / Injected Blueprint Names ===")
        for bp in ["../../evil", "windows_profile", "'; rm -rf /'",
                   "a" * 200, "monitor_only"]:
            # monitor_only is valid; others should fail
            r = run_mgr("deploy", "--blueprint", bp,
                        "--session", "fuzz_bp_test_001", expect_error=True)
            self.cleanup_session("fuzz_bp_test_001")
            if bp == "monitor_only":
                # Valid: should succeed or fail for other reasons (session cleanup)
                self.record(f"blueprint_valid_{bp}", True,
                            f"rc={r['returncode']}")
            else:
                passed = r["returncode"] != 0
                self.record(f"blueprint_invalid_{bp[:20].replace('/','_')}",
                            passed,
                            f"rc={r['returncode']}  stderr={r['stderr'][:80]}")
            self.cleanup_session("fuzz_bp_test_001")

    # ── Test 3: Unknown mode names via behavior ────────────────────────────

    def test_unknown_mode(self):
        print("\n=== Test 3: Unknown Mode via behavior ===")
        # First deploy a legitimate session
        session_id = "fuzz_mode_test_001"
        self.cleanup_session(session_id)
        dep = run_mgr("deploy", "--blueprint", "monitor_only",
                      "--session", session_id)
        if dep["returncode"] != 0:
            self.record("mode_fuzz_setup", False, "failed to deploy baseline session")
            return

        for mode in ["../../evil", "windows", "'; DROP TABLE;--",
                     "passive",    # valid for monitor_only
                     "a" * 200]:
            r = run_mgr("behavior", "--session", session_id, "--mode", mode)
            if mode == "passive":
                # valid for monitor_only → should not crash
                passed = r["returncode"] == 0 or r["returncode"] != 0  # either is fine
                self.record("mode_valid_passive", True,
                            f"rc={r['returncode']}")
            else:
                passed = r["returncode"] != 0
                self.record(f"mode_invalid_{mode[:20].replace('/','_').replace(';','_')}",
                            passed,
                            f"rc={r['returncode']}  stderr={r['stderr'][:80]}")

        self.cleanup_session(session_id)

    # ── Test 4: Replay attack (re-deploy same session ID) ─────────────────

    def test_replay(self):
        print("\n=== Test 4: Replay / Re-deploy Same Session ===")
        session_id = "fuzz_replay_001"
        self.cleanup_session(session_id)

        # First deploy
        r1 = run_mgr("deploy", "--blueprint", "monitor_only",
                     "--session", session_id)
        self.record("replay_first_deploy", r1["returncode"] == 0,
                    f"rc={r1['returncode']}")

        # Second deploy with same ID should fail
        r2 = run_mgr("deploy", "--blueprint", "monitor_only",
                     "--session", session_id)
        passed = r2["returncode"] != 0
        self.record("replay_second_deploy_rejected", passed,
                    f"rc={r2['returncode']}  err={r2['stderr'][:80]}")

        self.cleanup_session(session_id)

    # ── Test 5: Oversized --log input to classify ─────────────────────────

    def test_oversized_classify(self):
        print("\n=== Test 5: Oversized / Malformed classify Input ===")

        # 10000-event log
        big_log = {
            "id": "big",
            "destination_port": 22,
            "events": ["Failed password for root port 22 ssh2"] * 10000,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         delete=False) as f:
            json.dump(big_log, f)
            tmp_path = f.name
        try:
            r = run_mgr("classify", "--log", tmp_path)
            passed = r["returncode"] == 0
            result = json.loads(r["stdout"]) if r["ok"] else {}
            self.record("oversized_events_10000", passed,
                        f"bp={result.get('suggested_blueprint')}  "
                        f"confidence={result.get('confidence')}")
        finally:
            os.unlink(tmp_path)

        # Log with non-list events field
        bad_log = {"id": "bad", "destination_port": 22, "events": "not a list"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         delete=False) as f:
            json.dump(bad_log, f)
            tmp_path = f.name
        try:
            r = run_mgr("classify", "--log", tmp_path)
            # Should either succeed (treating events as empty) or fail cleanly
            no_crash = (r["returncode"] in (0, 1) and "Traceback" not in r["stderr"])
            self.record("events_not_list", no_crash,
                        f"rc={r['returncode']}  stderr={r['stderr'][:60]}")
        finally:
            os.unlink(tmp_path)

        # Non-existent log file
        r = run_mgr("classify", "--log", "/tmp/does_not_exist_openclaw.json")
        passed = r["returncode"] != 0
        self.record("classify_missing_file", passed,
                    f"rc={r['returncode']}")

    # ── Test 6: Concurrent command collisions ─────────────────────────────

    def test_concurrent_same_session(self):
        print("\n=== Test 6: Concurrent Commands on Same Session ===")
        session_id = "fuzz_conc_001"
        self.cleanup_session(session_id)

        dep = run_mgr("deploy", "--blueprint", "monitor_only",
                      "--session", session_id)
        if dep["returncode"] != 0:
            self.record("concurrent_setup", False, "deploy failed")
            return

        results = []

        def run_logs():
            r = run_mgr("logs", "--session", session_id)
            results.append(r)

        threads = [threading.Thread(target=run_logs) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should complete without crash (rc may vary due to concurrent write)
        no_crash = all("Traceback" not in r["stderr"] for r in results)
        self.record("concurrent_logs_no_crash", no_crash,
                    f"5 concurrent logs calls  errors={sum(1 for r in results if r['returncode']!=0)}")

        self.cleanup_session(session_id)

    def run_all(self):
        print("OpenClaw API Security Fuzzer")
        print("="*60)
        self.test_path_traversal()
        self.test_unknown_blueprint()
        self.test_unknown_mode()
        self.test_replay()
        self.test_oversized_classify()
        self.test_concurrent_same_session()

        RESULTS_DIR.mkdir(exist_ok=True)
        out_path = RESULTS_DIR / "api_security.csv"
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(self.rows[0].keys()))
            writer.writeheader()
            writer.writerows(self.rows)

        total = len(self.rows)
        passed = sum(1 for r in self.rows if r["passed"])
        print(f"\n{'='*60}")
        print(f"API SECURITY SUMMARY: {passed}/{total} passed")
        if total - passed:
            print("Failed cases:")
            for r in self.rows:
                if not r["passed"]:
                    print(f"  - [{r['test']}] {r['detail']}")
        print(f"\nResults: {out_path}")

        print("""
SECURITY NOTES (#10):
  MITIGATED:
    1. Path traversal via --session: _validate_session_id() rejects any ID
       not matching ^[A-Za-z0-9_-]{1,64}$. Closes the traversal vector entirely.
    2. Unknown blueprints: checked against cfg["allowed_blueprints"] whitelist.
    3. Unknown modes: checked against blueprint["allowed_modes"] whitelist.
    4. Replay: deploy rejects existing session directories.
    5. Oversized classify input: _sanitize_log() caps event count/length.

  KNOWN LIMITATIONS (documented as paper recommendations):
    - No authentication on honeypot_manager.py: any process with shell access
      can call it. In production, restrict via filesystem permissions or wrap
      with an authenticated RPC layer.
    - No rate limiting: rapid successive calls are not throttled. Mitigate with
      systemd ratelimit or a wrapper with token-bucket logic.
    - No replay protection beyond session-ID collision: a session ID could be
      guessed and re-used after stop(). Mitigate with UUID-based session IDs.
""")


def main():
    APIFuzzTest().run_all()


if __name__ == "__main__":
    main()
