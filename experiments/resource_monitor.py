#!/usr/bin/env python3
"""
resource_monitor.py — CPU / RAM / I-O / container-count sampler  (#6).

Can run standalone or as a context manager from other experiments:

  from experiments.resource_monitor import ResourceMonitor
  with ResourceMonitor(label="switching", csv_path="results/resource_by_phase.csv") as rm:
      <code under test>

Standalone:
  python3 experiments/resource_monitor.py --label idle --duration 30 --interval 2

Uses `docker stats --no-stream` + psutil for host metrics.
No Python Docker SDK required.
"""

import argparse
import csv
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent.resolve()
RESULTS_DIR = BASE / "results"

try:
    import psutil
except ImportError:
    print("psutil required: pip install psutil", file=sys.stderr)
    sys.exit(1)


def sample_docker_stats() -> list[dict]:
    """Return per-container CPU%/mem from docker stats --no-stream."""
    result = subprocess.run(
        ["docker", "stats", "--no-stream",
         "--format", "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"],
        capture_output=True, text=True, timeout=10
    )
    containers = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        name, cpu, mem, net, blk = parts
        containers.append({
            "name": name,
            "cpu_pct": cpu.strip("%").strip(),
            "mem": mem,
            "net_io": net,
            "block_io": blk,
        })
    return containers


def sample_host() -> dict:
    """Sample host-level resource usage via psutil."""
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_io_counters()
    return {
        "host_cpu_pct": round(cpu, 2),
        "host_mem_pct": round(mem.percent, 2),
        "host_mem_used_mb": round(mem.used / 1e6, 1),
        "host_disk_read_mb": round(disk.read_bytes / 1e6, 1) if disk else 0,
        "host_disk_write_mb": round(disk.write_bytes / 1e6, 1) if disk else 0,
    }


class ResourceMonitor:
    """
    Context manager that samples resource usage at `interval` seconds
    and writes rows to `csv_path`.  Call .mark_phase(label) to annotate
    a phase change mid-run.
    """

    def __init__(self, label: str = "run",
                 csv_path: str | None = None,
                 interval: float = 2.0):
        self.label = label
        self.csv_path = csv_path or str(RESULTS_DIR / "resource_by_phase.csv")
        self.interval = interval
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._current_phase = label
        self._rows: list[dict] = []

    def mark_phase(self, phase: str):
        self._current_phase = phase

    def _run(self):
        # Warm up psutil CPU measurement
        psutil.cpu_percent(interval=None)
        time.sleep(0.5)
        while not self._stop.is_set():
            ts = datetime.now(timezone.utc).isoformat()
            host = sample_host()
            containers = sample_docker_stats()
            container_count = len(containers)
            avg_container_cpu = 0.0
            if containers:
                try:
                    avg_container_cpu = sum(
                        float(c["cpu_pct"].replace(",", "."))
                        for c in containers
                        if c["cpu_pct"] not in ("--", "")
                    ) / container_count
                except ValueError:
                    avg_container_cpu = 0.0

            row = {
                "ts": ts,
                "phase": self._current_phase,
                "container_count": container_count,
                "avg_container_cpu_pct": round(avg_container_cpu, 2),
                **host,
            }
            self._rows.append(row)
            self._stop.wait(self.interval)

    def start(self):
        # Warm up psutil
        psutil.cpu_percent(interval=None)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        self._flush()

    def _flush(self):
        if not self._rows:
            return
        RESULTS_DIR.mkdir(exist_ok=True)
        out_path = Path(self.csv_path)
        write_header = not out_path.exists()
        with open(out_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(self._rows[0].keys()))
            if write_header:
                writer.writeheader()
            writer.writerows(self._rows)
        self._rows.clear()

    def summary(self) -> dict:
        if not self._rows:
            return {}
        avg_cpu = sum(r["host_cpu_pct"] for r in self._rows) / len(self._rows)
        max_cpu = max(r["host_cpu_pct"] for r in self._rows)
        avg_mem = sum(r["host_mem_pct"] for r in self._rows) / len(self._rows)
        max_cnt = max(r["container_count"] for r in self._rows)
        return {
            "samples": len(self._rows),
            "phase": self.label,
            "avg_host_cpu_pct": round(avg_cpu, 2),
            "max_host_cpu_pct": round(max_cpu, 2),
            "avg_host_mem_pct": round(avg_mem, 2),
            "max_containers": max_cnt,
        }

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()
        s = self.summary()
        if s:
            print(f"[resource] phase={s['phase']}  "
                  f"avg_cpu={s['avg_host_cpu_pct']}%  max_cpu={s['max_host_cpu_pct']}%  "
                  f"avg_mem={s['avg_host_mem_pct']}%  max_containers={s['max_containers']}")


def main():
    parser = argparse.ArgumentParser(prog="resource_monitor.py")
    parser.add_argument("--label", default="idle")
    parser.add_argument("--duration", type=float, default=30.0, help="seconds to sample")
    parser.add_argument("--interval", type=float, default=2.0, help="sample interval (s)")
    parser.add_argument("--csv", default=str(RESULTS_DIR / "resource_by_phase.csv"))
    args = parser.parse_args()

    print(f"Sampling resources for {args.duration}s (interval={args.interval}s, label={args.label})")
    monitor = ResourceMonitor(label=args.label, csv_path=args.csv, interval=args.interval)
    with monitor:
        time.sleep(args.duration)
    s = monitor.summary()
    for k, v in s.items():
        print(f"  {k}: {v}")
    print(f"Rows written to: {args.csv}")


if __name__ == "__main__":
    main()
