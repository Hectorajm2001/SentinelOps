"""Heuristic threat detection patterns."""

from typing import Any, Dict


class ThreatPatternTool:
    def detect(self, raw: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        text = raw.lower()
        attack_type = "unknown"
        severity = "LOW"
        threat = False

        if "failed password" in text or "authentication failure" in text:
            attack_type = "brute_force"
            severity = "MEDIUM"
            threat = True
        elif "union select" in text or "' or 1=1" in text or "sql" in text:
            attack_type = "sql_injection"
            severity = "HIGH"
            threat = True
        elif "port scan" in text or "nmap" in text:
            attack_type = "port_scanning"
            severity = "LOW"
            threat = True
        elif "lateral" in text or "wmic" in text or "remote service" in text:
            attack_type = "lateral_movement"
            severity = "HIGH"
            threat = True
        elif "exfil" in text or "data transfer" in text:
            attack_type = "exfiltration"
            severity = "CRITICAL"
            threat = True
        elif "privilege" in text or "sudo" in text or "su root" in text:
            attack_type = "privilege_escalation"
            severity = "HIGH"
            threat = True

        return {
            "threat": threat,
            "attack_type": attack_type,
            "severity": severity,
            "source_ip": parsed.get("source_ip") or "",
            "user": parsed.get("user") or "",
            "resource": parsed.get("resource") or "",
        }
