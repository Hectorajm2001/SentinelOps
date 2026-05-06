/* global __DEMO_MODE__, __API_URL__, __WS_URL__ */

import { useEffect, useMemo, useState } from "react";
import AlertList from "./components/AlertList.jsx";
import IncidentDetail from "./components/IncidentDetail.jsx";
import PlaybookPanel from "./components/PlaybookPanel.jsx";
import { demoIncidents } from "./data/demoIncidents.js";
import { useWebSocket } from "./hooks/useWebSocket.js";

const demoMode = __DEMO_MODE__ === "true";
const apiBaseUrl = __API_URL__;
const wsUrl = __WS_URL__;

export default function App() {
  const [incidents, setIncidents] = useState(demoMode ? demoIncidents : []);
  const [selectedId, setSelectedId] = useState(demoMode ? demoIncidents[0]?.id : null);

  const { status } = useWebSocket({
    url: wsUrl,
    enabled: !demoMode,
    onMessage: (message) => {
      if (!message || !message.type) {
        return;
      }
      if (message.type === "incident_update") {
        setIncidents((prev) => {
          const existing = prev.find((item) => item.id === message.data.id);
          if (existing) {
            return prev.map((item) => (item.id === message.data.id ? message.data : item));
          }
          return [message.data, ...prev];
        });
      }
    }
  });

  useEffect(() => {
    if (!selectedId && incidents.length > 0) {
      setSelectedId(incidents[0].id);
    }
  }, [incidents, selectedId]);

  const selectedIncident = incidents.find((item) => item.id === selectedId) || incidents[0];

  const counts = useMemo(() => {
    return incidents.reduce(
      (acc, item) => {
        acc[item.severity] = (acc[item.severity] || 0) + 1;
        return acc;
      },
      { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 }
    );
  }, [incidents]);

  const approvedIncidents = useMemo(
    () => incidents.filter((item) => item.approved),
    [incidents]
  );

  const handleApprove = async () => {
    if (!selectedIncident) {
      return;
    }
    setIncidents((prev) =>
      prev.map((item) => (item.id === selectedIncident.id ? { ...item, approved: true } : item))
    );
    if (!demoMode) {
      await fetch(`${apiBaseUrl}/api/incidents/${selectedIncident.id}/approve`, { method: "POST" });
    }
  };

  const handleDiscard = () => {
    if (!selectedIncident) {
      return;
    }
    setIncidents((prev) =>
      prev.map((item) => (item.id === selectedIncident.id ? { ...item, approved: false } : item))
    );
  };

  const handleExport = () => {
    window.print();
  };

  const statusColor = demoMode
    ? "bg-accent"
    : status === "connected"
    ? "bg-accent"
    : status === "connecting"
    ? "bg-warning"
    : "bg-critical";

  return (
    <div className="min-h-screen px-6 pb-10 pt-6 text-slate-100">
      <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-[0.4em] text-slate-500">SentinelOps</div>
          <h1 className="text-3xl font-semibold">Autonomous Incident Response</h1>
          <p className="mt-1 text-sm text-slate-400">
            {demoMode ? "Demo mode activo" : "Tiempo real con WebSocket"}
          </p>
        </div>
        <div className="flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs">
          <span className={`h-2 w-2 rounded-full ${statusColor}`} />
          <span>{demoMode ? "DEMO" : status.toUpperCase()}</span>
        </div>
      </header>

      <main className="grid gap-6 lg:grid-cols-[0.3fr_0.4fr_0.3fr]">
        <AlertList
          incidents={incidents}
          selectedId={selectedId}
          onSelect={setSelectedId}
          counts={counts}
        />
        <IncidentDetail incident={selectedIncident} />
        <PlaybookPanel
          incident={selectedIncident}
          onApprove={handleApprove}
          onDiscard={handleDiscard}
          onExport={handleExport}
          approvedIncidents={approvedIncidents}
        />
      </main>
    </div>
  );
}
