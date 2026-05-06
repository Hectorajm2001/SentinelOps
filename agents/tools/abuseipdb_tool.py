"""AbuseIPDB API v2 integration."""

import json
from typing import Any, Dict
from urllib import parse as urllib_parse
from urllib import request as urllib_request


class AbuseIPDBTool:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def lookup(self, indicator: str) -> Dict[str, Any]:
        if not indicator or not self.api_key:
            return {"source": "abuseipdb", "found": False, "score": 0}
        query = urllib_parse.urlencode({"ipAddress": indicator, "maxAgeInDays": 90})
        url = f"https://api.abuseipdb.com/api/v2/check?{query}"
        req = urllib_request.Request(
            url,
            headers={"Key": self.api_key, "Accept": "application/json"},
        )
        try:
            with urllib_request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
            data = json.loads(body)
            return {"source": "abuseipdb", "found": True, "raw": data}
        except Exception:
            return {"source": "abuseipdb", "found": False, "score": 0}
