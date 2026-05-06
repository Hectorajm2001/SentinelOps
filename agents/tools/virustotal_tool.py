"""VirusTotal API v3 integration."""

import json
import re
from typing import Any, Dict
from urllib import request as urllib_request

IP_RE = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
HASH_RE = re.compile(r"^[a-fA-F0-9]{32,64}$")


class VirusTotalTool:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def lookup(self, indicator: str) -> Dict[str, Any]:
        if not indicator or not self.api_key:
            return {"source": "virustotal", "found": False, "score": 0}
        endpoint = self._build_endpoint(indicator)
        if not endpoint:
            return {"source": "virustotal", "found": False, "score": 0}
        req = urllib_request.Request(
            endpoint,
            headers={"x-apikey": self.api_key, "accept": "application/json"},
        )
        try:
            with urllib_request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
            data = json.loads(body)
            return {"source": "virustotal", "found": True, "raw": data}
        except Exception:
            return {"source": "virustotal", "found": False, "score": 0}

    def _build_endpoint(self, indicator: str) -> str:
        if IP_RE.match(indicator):
            return f"https://www.virustotal.com/api/v3/ip_addresses/{indicator}"
        if HASH_RE.match(indicator):
            return f"https://www.virustotal.com/api/v3/files/{indicator}"
        return ""
