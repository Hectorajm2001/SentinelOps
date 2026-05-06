export const demoIncidents = [
  {
    id: "inc-001",
    created_at: "2026-05-05T10:12:34Z",
    updated_at: "2026-05-05T10:12:50Z",
    severity: "CRITICAL",
    attack_type: "exfiltration",
    source_ip: "185.220.101.45",
    user: "root",
    resource: "/srv/finance/export.csv",
    classification: {
      threat: true,
      attack_type: "exfiltration",
      severity: "CRITICAL",
      source_ip: "185.220.101.45",
      user: "root",
      resource: "/srv/finance/export.csv"
    },
    threat_intel: {
      indicator: "185.220.101.45",
      reputation: "malicious",
      apt_group: "APT-Exfil",
      mitre: { id: "T1020", name: "Automated Exfiltration" },
      cves: ["CVE-2024-9999"]
    },
    correlation: {
      previous_activity: true,
      repeated_pattern: true,
      campaign: true,
      risk_score: 92
    },
    playbook_markdown:
      "# Playbook de respuesta\n\n## Acciones inmediatas\n- Bloquear IP 185.220.101.45\n- Aislar servidor de finanzas\n\n## Evidencia forense\n- Preservar logs y snapshots\n\n## Notificaciones\n- Escalar a IR Lead con urgencia\n\n## Remediacion\n- Rotar credenciales\n- Revisar reglas de firewall\n\n## Resumen ejecutivo\nExfiltracion critica detectada. Riesgo 92/100. Accion inmediata requerida.",
    pipeline_status: "COMPLETE",
    risk_score: 92,
    activity_series: [
      { time: "-6h", value: 2 },
      { time: "-4h", value: 5 },
      { time: "-2h", value: 9 },
      { time: "-1h", value: 16 },
      { time: "now", value: 24 }
    ],
    timeline: [
      { ts: "2026-05-05T10:12:34Z", event: "Log ingested" },
      { ts: "2026-05-05T10:12:38Z", event: "Classification complete" },
      { ts: "2026-05-05T10:12:42Z", event: "Threat intel complete" },
      { ts: "2026-05-05T10:12:46Z", event: "Correlation complete" },
      { ts: "2026-05-05T10:12:50Z", event: "Playbook generated" }
    ],
    approved: false
  },
  {
    id: "inc-002",
    created_at: "2026-05-05T09:48:12Z",
    updated_at: "2026-05-05T09:48:28Z",
    severity: "HIGH",
    attack_type: "brute_force",
    source_ip: "103.21.244.12",
    user: "admin",
    resource: "ssh",
    classification: {
      threat: true,
      attack_type: "brute_force",
      severity: "HIGH",
      source_ip: "103.21.244.12",
      user: "admin",
      resource: "ssh"
    },
    threat_intel: {
      indicator: "103.21.244.12",
      reputation: "suspicious",
      apt_group: "",
      mitre: { id: "T1110", name: "Brute Force" },
      cves: []
    },
    correlation: {
      previous_activity: true,
      repeated_pattern: true,
      campaign: false,
      risk_score: 68
    },
    playbook_markdown:
      "# Playbook de respuesta\n\n## Acciones inmediatas\n- Bloquear IP 103.21.244.12\n- Forzar MFA para admin\n\n## Evidencia forense\n- Preservar logs SSH\n\n## Notificaciones\n- Notificar SOC\n\n## Remediacion\n- Revisar listas de acceso\n\n## Resumen ejecutivo\nBrute force sostenido detectado. Riesgo 68/100.",
    pipeline_status: "COMPLETE",
    risk_score: 68,
    activity_series: [
      { time: "-6h", value: 1 },
      { time: "-4h", value: 3 },
      { time: "-2h", value: 6 },
      { time: "-1h", value: 10 },
      { time: "now", value: 14 }
    ],
    timeline: [
      { ts: "2026-05-05T09:48:12Z", event: "Log ingested" },
      { ts: "2026-05-05T09:48:18Z", event: "Classification complete" },
      { ts: "2026-05-05T09:48:24Z", event: "Threat intel complete" },
      { ts: "2026-05-05T09:48:28Z", event: "Playbook generated" }
    ],
    approved: true
  },
  {
    id: "inc-003",
    created_at: "2026-05-05T08:11:44Z",
    updated_at: "2026-05-05T08:12:02Z",
    severity: "MEDIUM",
    attack_type: "sql_injection",
    source_ip: "45.76.22.11",
    user: "webapp",
    resource: "/login",
    classification: {
      threat: true,
      attack_type: "sql_injection",
      severity: "MEDIUM",
      source_ip: "45.76.22.11",
      user: "webapp",
      resource: "/login"
    },
    threat_intel: {
      indicator: "45.76.22.11",
      reputation: "suspicious",
      apt_group: "",
      mitre: { id: "T1190", name: "Exploit Public-Facing Application" },
      cves: []
    },
    correlation: {
      previous_activity: false,
      repeated_pattern: false,
      campaign: false,
      risk_score: 42
    },
    playbook_markdown:
      "# Playbook de respuesta\n\n## Acciones inmediatas\n- Bloquear IP 45.76.22.11\n- Activar WAF en /login\n\n## Evidencia forense\n- Preservar logs Apache\n\n## Notificaciones\n- Notificar a AppSec\n\n## Remediacion\n- Revisar validacion de entradas\n\n## Resumen ejecutivo\nSQL injection aislado detectado. Riesgo 42/100.",
    pipeline_status: "COMPLETE",
    risk_score: 42,
    activity_series: [
      { time: "-6h", value: 0 },
      { time: "-4h", value: 1 },
      { time: "-2h", value: 2 },
      { time: "-1h", value: 3 },
      { time: "now", value: 4 }
    ],
    timeline: [
      { ts: "2026-05-05T08:11:44Z", event: "Log ingested" },
      { ts: "2026-05-05T08:11:50Z", event: "Classification complete" },
      { ts: "2026-05-05T08:11:56Z", event: "Threat intel complete" },
      { ts: "2026-05-05T08:12:02Z", event: "Playbook generated" }
    ],
    approved: false
  }
];
