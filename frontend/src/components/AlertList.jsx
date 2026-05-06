import SeverityBadge from "./SeverityBadge.jsx";

const severityOrder = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

export default function AlertList({ incidents, selectedId, onSelect, counts }) {
  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header">
        <span>Alertas activas</span>
        <span className="text-xs text-slate-500">Live</span>
      </div>
      <div className="flex flex-wrap gap-2 px-4 py-3">
        {severityOrder.map((level) => (
          <div key={level} className="flex items-center gap-2 rounded-full bg-white/5 px-3 py-1 text-xs">
            <SeverityBadge severity={level} />
            <span>{counts[level] || 0}</span>
          </div>
        ))}
      </div>
      <div className="scrollbar-thin scrollbar-thumb-slate flex-1 overflow-y-auto px-4 pb-4">
        <div className="space-y-3">
          {incidents.map((incident) => {
            const active = incident.id === selectedId;
            const timestamp = new Date(incident.created_at).toLocaleTimeString();
            return (
              <button
                key={incident.id}
                className={`w-full rounded-xl border px-3 py-3 text-left transition ${
                  active
                    ? "border-accent/60 bg-accent/10"
                    : "border-white/10 bg-white/5 hover:border-white/20"
                }`}
                onClick={() => onSelect(incident.id)}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">{timestamp}</span>
                  <SeverityBadge severity={incident.severity} />
                </div>
                <div className="mt-2 text-sm font-semibold text-slate-100">
                  {incident.attack_type.replaceAll("_", " ")}
                </div>
                <div className="mt-1 text-xs text-slate-400">IP: {incident.source_ip || "n/a"}</div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
