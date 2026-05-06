import ReactMarkdown from "react-markdown";

export default function PlaybookPanel({
  incident,
  onApprove,
  onDiscard,
  onExport,
  approvedIncidents
}) {
  if (!incident) {
    return (
      <div className="panel h-full p-6">
        <div className="text-slate-400">No hay playbook seleccionado.</div>
      </div>
    );
  }

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header">
        <span>Playbook</span>
        <span className="text-xs text-slate-500">{incident.approved ? "Aprobado" : "Pendiente"}</span>
      </div>
      <div className="flex-1 overflow-y-auto px-5 pb-6">
        <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-4 text-sm leading-relaxed">
          <ReactMarkdown>{incident.playbook_markdown || "Sin playbook"}</ReactMarkdown>
        </div>

        <div className="mt-4 flex flex-wrap gap-3">
          <button
            className="rounded-full bg-accent/20 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-accent"
            onClick={onApprove}
          >
            Aprobar Playbook
          </button>
          <button
            className="rounded-full bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-slate-300"
            onClick={onDiscard}
          >
            Descartar
          </button>
          <button
            className="rounded-full border border-white/20 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-slate-200"
            onClick={onExport}
          >
            Exportar PDF
          </button>
        </div>

        <div className="mt-6">
          <div className="mb-2 text-xs uppercase tracking-[0.2em] text-slate-400">
            Historial de playbooks aprobados
          </div>
          <div className="space-y-2">
            {approvedIncidents.length === 0 && (
              <div className="text-xs text-slate-500">Sin aprobados aun.</div>
            )}
            {approvedIncidents.map((item) => (
              <div key={item.id} className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs">
                <div className="font-semibold text-slate-200">{item.attack_type}</div>
                <div className="text-slate-500">{new Date(item.updated_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
