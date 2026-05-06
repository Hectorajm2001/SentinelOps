"""MITRE ATT&CK mapping helper."""

from typing import Any, Dict

MITRE_MAP = {
    "brute_force": {"id": "T1110", "name": "Brute Force", "description": "Repeated authentication attempts"},
    "sql_injection": {"id": "T1190", "name": "Exploit Public-Facing Application", "description": "Injection on exposed app"},
    "exfiltration": {"id": "T1020", "name": "Automated Exfiltration", "description": "Automated data exfil"},
    "lateral_movement": {"id": "T1021", "name": "Remote Services", "description": "Move laterally via services"},
    "privilege_escalation": {"id": "T1068", "name": "Exploitation for Privilege Escalation", "description": "Gain elevated rights"},
    "port_scanning": {"id": "T1046", "name": "Network Service Scanning", "description": "Discover open services"},
}


class MitreAttackTool:
    def map_attack(self, attack_type: str) -> Dict[str, Any]:
        return MITRE_MAP.get(attack_type, {"id": "T0000", "name": "Unknown", "description": "Unknown"})
