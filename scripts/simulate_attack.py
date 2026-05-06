"""Simulate a full attack chain for the demo."""

import argparse
import json
import time
from datetime import datetime, timezone
from typing import Callable
from urllib import request as urllib_request


def rfc5424(timestamp: datetime, host: str, app: str, message: str) -> str:
    ts = timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return f"<134>1 {ts} {host} {app} - - - {message}"


def post_log(base_url: str, raw: str) -> None:
    payload = json.dumps({"raw": raw, "source": "syslog"}).encode("utf-8")
    url = f"{base_url.rstrip('/')}/api/logs/ingest"
    req = urllib_request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib_request.urlopen(req, timeout=5) as resp:
        resp.read()


def run_phase(name: str, duration: int, count: int, send_fn: Callable[[int], None], fast: bool) -> None:
    print(f"[+] {name} started ({count} logs)")
    start = time.time()
    for i in range(count):
        send_fn(i)
        if fast:
            continue
        elapsed = time.time() - start
        remaining = max(0.0, duration - elapsed)
        remaining_attempts = max(1, count - i - 1)
        time.sleep(remaining / remaining_attempts)
    print(f"[+] {name} completed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--fast", action="store_true", help="Skip sleeps for quick runs")
    args = parser.parse_args()

    source_ip = "185.220.101.45"
    host = "sentinelops-edge"

    def send_port_scan(index: int) -> None:
        msg = f"Port scan detected from {source_ip} to 10.0.0.5 port {20 + (index % 100)}"
        log = rfc5424(datetime.now(timezone.utc), host, "scan", msg)
        post_log(args.base_url, log)

    def send_bruteforce(index: int) -> None:
        port = 50000 + index
        msg = f"Failed password for root from {source_ip} port {port} ssh2"
        log = rfc5424(datetime.now(timezone.utc), host, "sshd", msg)
        post_log(args.base_url, log)

    def send_escalation(index: int) -> None:
        msg = "Accepted password for root from 185.220.101.45 port 50123 ssh2"
        log = rfc5424(datetime.now(timezone.utc), host, "sshd", msg)
        post_log(args.base_url, log)
        if index % 3 == 0:
            sudo_msg = "Privilege escalation detected via sudo to root"
            sudo_log = rfc5424(datetime.now(timezone.utc), host, "sudo", sudo_msg)
            post_log(args.base_url, sudo_log)

    def send_lateral(index: int) -> None:
        target = f"10.0.2.{10 + (index % 3)}"
        msg = f"Lateral movement attempt from 10.0.0.5 to {target} via WMI"
        log = rfc5424(datetime.now(timezone.utc), host, "lateral", msg)
        post_log(args.base_url, log)

    def send_exfil(index: int) -> None:
        bytes_sent = 5000000 + index * 120000
        msg = f"Data exfiltration suspected: outbound transfer to {source_ip} bytes={bytes_sent}"
        log = rfc5424(datetime.now(timezone.utc), host, "exfil", msg)
        post_log(args.base_url, log)

    run_phase("Phase 1 - Port scanning", 10, 40, send_port_scan, args.fast)
    run_phase("Phase 2 - Brute force SSH", 15, 847, send_bruteforce, args.fast)
    run_phase("Phase 3 - Privilege escalation", 15, 20, send_escalation, args.fast)
    run_phase("Phase 4 - Lateral movement", 20, 30, send_lateral, args.fast)
    run_phase("Phase 5 - Data exfiltration", 30, 25, send_exfil, args.fast)


if __name__ == "__main__":
    main()
