import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

export default function RiskChart({ series = [], riskScore = 0 }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="mb-3 text-xs uppercase tracking-[0.2em] text-slate-400">Riesgo</div>
      <div className="mb-2 text-2xl font-semibold text-accent">{riskScore}/100</div>
      <div className="h-32">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={series}>
            <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 10 }} axisLine={false} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} axisLine={false} width={30} />
            <Tooltip
              contentStyle={{ background: "#0f172a", border: "1px solid rgba(255,255,255,0.1)" }}
              labelStyle={{ color: "#94a3b8" }}
            />
            <Line type="monotone" dataKey="value" stroke="#00ff88" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
