import AgentAccordion from "./AgentAccordion.jsx";
import RiskChart from "./RiskChart.jsx";
import SeverityBadge from "./SeverityBadge.jsx";
import Timeline from "./Timeline.jsx";

export default function IncidentDetail({ incident }) {
  if (!incident) {
    return (
      <div className="panel h-full p-6">
        <div className="text-slate-400">Selecciona una alerta para ver detalles.</div>
      </div>
    );
  }

  const series = incident.activity_series || [];

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header">
        <span>Investigacion</span>
        <span className="text-xs text-slate-500">Pipeline {incident.pipeline_status}</span>
      </div>
      <div className="flex-1 overflow-y-auto px-5 pb-6">
        <div className="mt-4 flex items-start justify-between">
          <div>
            <div className="text-xl font-semibold text-slate-100">
              {incident.attack_type.replaceAll("_", " ")}
            </div>
            <div className="mt-2 text-xs text-slate-400">IP: {incident.source_ip || "n/a"}</div>
            <div className="text-xs text-slate-400">Usuario: {incident.user || "n/a"}</div>
            <div className="text-xs text-slate-400">Recurso: {incident.resource || "n/a"}</div>
          </div>
          <SeverityBadge severity={incident.severity} />
        </div>

        <div className="mt-6 grid gap-4">
          <RiskChart series={series} riskScore={incident.risk_score} />

          <div className="rounded-xl border border-white/10 bg-white/5 p-4">
            <div className="mb-3 text-xs uppercase tracking-[0.2em] text-slate-400">Timeline</div>
            <Timeline items={incident.timeline || []} />
          </div>

          <AgentAccordion title="Clasificacion" defaultOpen>
            <pre className="whitespace-pre-wrap text-xs font-mono text-slate-200">
              {JSON.stringify(incident.classification, null, 2)}
            </pre>
          </AgentAccordion>

          <AgentAccordion title="Inteligencia del atacante">
            <pre className="whitespace-pre-wrap text-xs font-mono text-slate-200">
              {JSON.stringify(incident.threat_intel, null, 2)}
            </pre>
          </AgentAccordion>

          <AgentAccordion title="Correlacion">
            <pre className="whitespace-pre-wrap text-xs font-mono text-slate-200">
              {JSON.stringify(incident.correlation, null, 2)}
            </pre>
          </AgentAccordion>
        </div>
      </div>
    </div>
  );
}
