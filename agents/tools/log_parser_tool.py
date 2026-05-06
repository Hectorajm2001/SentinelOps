"""Parse syslog and JSON logs into a normalized structure."""

import json
import re
from typing import Any, Dict

SYSLOG_RE = re.compile(
    r"^(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<app>\S+?)(\[(?P<procid>\d+)\])?:\s+(?P<message>.*)$"
)
IP_RE = re.compile(r"(\d+\.\d+\.\d+\.\d+)")
USER_RE = re.compile(r"(?:user\s+|for\s+)(?P<user>[a-zA-Z0-9_-]+)")


class LogParserTool:
    def parse(self, raw: str) -> Dict[str, Any]:
        raw = raw.strip()
        if raw.startswith("{"):
            try:
                data = json.loads(raw)
                return self._normalize_json(data)
            except Exception:
                return {"message": raw}
        match = SYSLOG_RE.match(raw)
        if not match:
            return {"message": raw}
        data = match.groupdict()
        message = data.get("message", "")
        return {
            "timestamp": data.get("timestamp"),
            "host": data.get("host"),
            "app": data.get("app"),
            "procid": data.get("procid"),
            "message": message,
            "source_ip": self._extract_ip(message),
            "user": self._extract_user(message),
            "resource": self._extract_resource(message),
        }

    def _normalize_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "timestamp": data.get("timestamp") or data.get("time"),
            "host": data.get("host") or data.get("hostname"),
            "app": data.get("app") or data.get("source"),
            "procid": data.get("procid"),
            "message": data.get("message") or data.get("msg"),
            "source_ip": data.get("src_ip") or data.get("ip"),
            "user": data.get("user") or data.get("account"),
            "resource": data.get("resource") or data.get("path"),
            "raw": data,
        }

    def _extract_ip(self, message: str) -> str:
        match = IP_RE.search(message)
        return match.group(1) if match else ""

    def _extract_user(self, message: str) -> str:
        match = USER_RE.search(message)
        return match.group("user") if match else ""

    def _extract_resource(self, message: str) -> str:
        if "/" in message:
            parts = [part for part in message.split() if "/" in part]
            return parts[0] if parts else ""
        return ""
