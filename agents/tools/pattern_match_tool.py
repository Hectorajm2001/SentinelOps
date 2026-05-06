"""Basic correlation heuristics for recent incidents."""

from typing import Any, Dict, List

SEVERITY_WEIGHT = {"LOW": 5, "MEDIUM": 15, "HIGH": 30, "CRITICAL": 50}


class PatternMatchTool:
    def analyze(self, incident: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        source_ip = incident.get("source_ip")
        user = incident.get("user")
        ip_hits = sum(1 for item in history if item.get("source_ip") == source_ip)
        user_hits = sum(1 for item in history if item.get("user") == user)
        repeated = ip_hits >= 2 or user_hits >= 2
        campaign = ip_hits >= 3 or user_hits >= 3
        severity = incident.get("severity", "LOW")
        risk_score = min(100, SEVERITY_WEIGHT.get(severity, 5) + ip_hits * 10 + user_hits * 5)

        return {
            "previous_activity": ip_hits > 0 or user_hits > 0,
            "repeated_pattern": repeated,
            "campaign": campaign,
            "risk_score": risk_score,
            "ip_hits": ip_hits,
            "user_hits": user_hits,
        }
