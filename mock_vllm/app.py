"""Mock vLLM OpenAI-compatible server for local development."""

import hashlib
import json
import time
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="mock-vllm")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: float | None = 0.2


def choose_variant(seed_text: str, variants: List[Dict[str, Any]]) -> Dict[str, Any]:
    digest = hashlib.md5(seed_text.encode("utf-8")).hexdigest()
    seed = int(digest[:8], 16)
    index = seed % len(variants)
    return variants[index]


def detect_agent(text: str) -> str:
    lower = text.lower()
    if "reputacion" in lower or "virustotal" in lower:
        return "investigator"
    if "correlacion" in lower or "risk_score" in lower:
        return "correlator"
    if "playbook" in lower or "remediacion" in lower:
        return "playbook"
    return "classifier"


def build_classifier(text: str) -> str:
    variants = [
        {
            "threat": True,
            "attack_type": "brute_force",
            "severity": "HIGH",
            "source_ip": "185.220.101.45",
            "user": "root",
            "resource": "ssh"
        },
        {
            "threat": True,
            "attack_type": "sql_injection",
            "severity": "MEDIUM",
            "source_ip": "203.0.113.10",
            "user": "webapp",
            "resource": "/login"
        },
        {
            "threat": True,
            "attack_type": "lateral_movement",
            "severity": "HIGH",
            "source_ip": "10.0.0.5",
            "user": "svc-backup",
            "resource": "10.0.2.12"
        }
    ]
    return json.dumps(choose_variant(text, variants))


def build_investigator(text: str) -> str:
    variants = [
        {
            "indicator": "185.220.101.45",
            "reputation": "malicious",
            "apt_group": "APT-Exfil",
            "mitre": {"id": "T1020", "name": "Automated Exfiltration", "description": "Automated data exfil"},
            "cves": ["CVE-2024-9999"]
        },
        {
            "indicator": "203.0.113.10",
            "reputation": "suspicious",
            "apt_group": "",
            "mitre": {"id": "T1190", "name": "Exploit Public-Facing Application", "description": "Injection"},
            "cves": []
        }
    ]
    return json.dumps(choose_variant(text, variants))


def build_correlator(text: str) -> str:
    variants = [
        {"previous_activity": True, "repeated_pattern": True, "campaign": True, "risk_score": 91},
        {"previous_activity": False, "repeated_pattern": False, "campaign": False, "risk_score": 35},
        {"previous_activity": True, "repeated_pattern": False, "campaign": False, "risk_score": 62}
    ]
    return json.dumps(choose_variant(text, variants))


def build_playbook(text: str) -> str:
    variants = [
        "# Playbook de respuesta\n\n## Acciones inmediatas\n- Bloquear IP maliciosa\n- Aislar servidor afectado\n\n## Evidencia forense\n- Preservar logs y snapshots\n\n## Notificaciones\n- Escalar a IR Lead\n\n## Remediacion\n- Rotar credenciales\n\n## Resumen ejecutivo\nAtaque critico detectado. Accion inmediata requerida.",
        "# Playbook de respuesta\n\n## Acciones inmediatas\n- Activar WAF\n- Bloquear IP\n\n## Evidencia forense\n- Guardar logs de aplicacion\n\n## Notificaciones\n- Notificar AppSec\n\n## Remediacion\n- Revisar validaciones\n\n## Resumen ejecutivo\nSQL injection aislado. Riesgo medio."
    ]
    return choose_variant(text, [{"content": variants[0]}, {"content": variants[1]}])["content"]


@app.post("/v1/chat/completions")
def chat(request: ChatRequest) -> Dict[str, Any]:
    user_text = ""
    for message in reversed(request.messages):
        if message.role == "user":
            user_text = message.content
            break

    agent_type = detect_agent(user_text)
    if agent_type == "investigator":
        content = build_investigator(user_text)
    elif agent_type == "correlator":
        content = build_correlator(user_text)
    elif agent_type == "playbook":
        content = build_playbook(user_text)
    else:
        content = build_classifier(user_text)

    return {
        "id": f"mock-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop"
            }
        ]
    }
