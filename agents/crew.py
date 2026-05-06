"""Multi-agent pipeline using CrewAI with a local fallback."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import request as urllib_request

from agents.tools.abuseipdb_tool import AbuseIPDBTool
from agents.tools.history_query_tool import HistoryQueryTool
from agents.tools.log_parser_tool import LogParserTool
from agents.tools.mitre_attack_tool import MitreAttackTool
from agents.tools.pattern_match_tool import PatternMatchTool
from agents.tools.threat_pattern_tool import ThreatPatternTool
from agents.tools.virustotal_tool import VirusTotalTool

try:
    from crewai import Agent, Crew, Process, Task
except Exception:  # pragma: no cover - optional dependency
    Agent = Crew = Process = Task = None

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


@dataclass
class AgentResult:
    name: str
    output: Any


class LLMClient:
    def __init__(self, base_url: str, model_name: str, timeout: int = 20) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout = timeout

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib_request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
            parsed = json.loads(body)
            return parsed["choices"][0]["message"]["content"]
        except Exception:
            return ""


class AgentsPipeline:
    def __init__(self, vllm_base_url: str, model_name: str) -> None:
        self._client = LLMClient(base_url=vllm_base_url, model_name=model_name)
        self._prompts = {
            "classifier": self._load_prompt("security_classifier.txt"),
            "investigator": self._load_prompt("threat_investigator.txt"),
            "correlator": self._load_prompt("event_correlator.txt"),
            "playbook": self._load_prompt("playbook_generator.txt"),
        }
        self._threat_tool = ThreatPatternTool()
        self._vt_tool = VirusTotalTool(api_key=os.getenv("VIRUSTOTAL_API_KEY", ""))
        self._abuse_tool = AbuseIPDBTool(api_key=os.getenv("ABUSEIPDB_API_KEY", ""))
        self._mitre_tool = MitreAttackTool()
        self._history_tool = HistoryQueryTool(database_url=os.getenv("DATABASE_URL", ""))
        self._pattern_tool = PatternMatchTool()
        self._use_crewai = os.getenv("USE_CREWAI", "false").lower() == "true" and Agent is not None
        self._crew = self._build_crewai() if self._use_crewai else None

    def _load_prompt(self, name: str) -> str:
        path = PROMPT_DIR / name
        return path.read_text(encoding="utf-8")

    def _build_crewai(self) -> Optional[Any]:
        if Agent is None:
            return None
        classifier = Agent(
            role="Threat Detection Engineer",
            goal="Detect and classify threats from raw logs with MITRE mapping and severity scoring",
        )
        investigator = Agent(role="Threat Intelligence Analyst", goal="Research attacker identity, reputation and known techniques")
        correlator = Agent(role="Security Operations Analyst", goal="Correlate current incident with historical events to detect patterns")
        playbook = Agent(
            role="Incident Response Commander",
            goal="Generate a specific, actionable security incident response playbook",
        )

        tasks = [
            Task(description=self._prompts["classifier"], agent=classifier),
            Task(description=self._prompts["investigator"], agent=investigator),
            Task(description=self._prompts["correlator"], agent=correlator),
            Task(description=self._prompts["playbook"], agent=playbook),
        ]
        return Crew(agents=[classifier, investigator, correlator, playbook], tasks=tasks, process=Process.sequential)

    def run(self, event: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        start_time = time.time()
        raw_log = event.get("raw", "")
        parser = LogParserTool()
        parsed = parser.parse(raw_log)

        classification_hint = self._threat_tool.detect(raw_log, parsed)
        classification = self._agent_json(
            self._prompts["classifier"],
            {
                "raw_log": raw_log,
                "parsed": parsed,
                "heuristic": classification_hint,
            },
            fallback=classification_hint,
        )

        indicator = (
            classification.get("source_ip")
            or parsed.get("source_ip")
            or event.get("metadata", {}).get("source_ip")
            or ""
        )
        intel_tools = {
            "virustotal": self._vt_tool.lookup(indicator),
            "abuseipdb": self._abuse_tool.lookup(indicator),
            "mitre": self._mitre_tool.map_attack(classification.get("attack_type", "unknown")),
        }
        threat_intel = self._agent_json(
            self._prompts["investigator"],
            {
                "indicator": indicator,
                "tool_results": intel_tools,
                "attack_type": classification.get("attack_type"),
            },
            fallback=intel_tools,
        )

        history_from_db = self._history_tool.query_recent(days=7)
        history_pool = history or history_from_db
        correlation_hint = self._pattern_tool.analyze(classification, history_pool)
        correlation = self._agent_json(
            self._prompts["correlator"],
            {
                "incident": classification,
                "history": history_pool,
                "heuristic": correlation_hint,
            },
            fallback=correlation_hint,
        )

        playbook_markdown = self._agent_markdown(
            self._prompts["playbook"],
            {
                "classification": classification,
                "threat_intel": threat_intel,
                "correlation": correlation,
            },
            fallback=self._playbook_fallback(classification, threat_intel, correlation),
        )

        created_at = datetime.now(timezone.utc)
        pipeline_seconds = time.time() - start_time

        incident = {
            "id": str(uuid.uuid4()),
            "created_at": created_at,
            "updated_at": created_at,
            "severity": classification.get("severity", "LOW"),
            "attack_type": classification.get("attack_type", "unknown"),
            "source_ip": classification.get("source_ip") or parsed.get("source_ip"),
            "user": classification.get("user") or parsed.get("user"),
            "resource": classification.get("resource") or parsed.get("resource"),
            "raw_log": raw_log,
            "classification": classification,
            "threat_intel": threat_intel,
            "correlation": correlation,
            "playbook_markdown": playbook_markdown,
            "pipeline_status": "COMPLETE",
            "risk_score": int(correlation.get("risk_score", 0)),
            "pipeline_seconds": pipeline_seconds,
            "timeline": [
                {"ts": created_at.isoformat(), "event": "Log ingested"},
                {"ts": created_at.isoformat(), "event": "Classification complete"},
                {"ts": created_at.isoformat(), "event": "Threat intel complete"},
                {"ts": created_at.isoformat(), "event": "Correlation complete"},
                {"ts": created_at.isoformat(), "event": "Playbook generated"},
            ],
            "approved": False,
        }
        return incident

    def _agent_json(self, prompt: str, payload: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = json.dumps(payload, ensure_ascii=True, indent=2)
        response = self._client.chat(system_prompt=prompt, user_prompt=user_prompt)
        parsed = self._safe_json(response)
        return parsed or fallback

    def _agent_markdown(self, prompt: str, payload: Dict[str, Any], fallback: str) -> str:
        user_prompt = json.dumps(payload, ensure_ascii=True, indent=2)
        response = self._client.chat(system_prompt=prompt, user_prompt=user_prompt)
        return response.strip() or fallback

    def _safe_json(self, text: str) -> Dict[str, Any]:
        if not text:
            return {}
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {}

    def _playbook_fallback(
        self, classification: Dict[str, Any], intel: Dict[str, Any], correlation: Dict[str, Any]
    ) -> str:
        severity = classification.get("severity", "LOW")
        attack_type = classification.get("attack_type", "unknown")
        source_ip = classification.get("source_ip", "unknown")
        risk = correlation.get("risk_score", 0)
        return (
            "# Playbook de respuesta\n\n"
            "## Acciones inmediatas\n"
            f"- Bloquear IP {source_ip}\n"
            f"- Aislar sistemas afectados por {attack_type}\n"
            "- Rotar credenciales comprometidas\n\n"
            "## Evidencia forense\n"
            "- Preservar logs y snapshots de disco\n"
            "- Guardar hashes de archivos sospechosos\n\n"
            "## Notificaciones\n"
            f"- Escalar a IR Lead (severidad {severity})\n"
            "- Notificar SOC y TI\n\n"
            "## Remediacion\n"
            "- Aplicar parches y hardening\n"
            "- Revisar reglas de firewall\n\n"
            "## Resumen ejecutivo\n"
            f"Ataque {attack_type} detectado desde {source_ip}. Riesgo {risk}/100."
        )
