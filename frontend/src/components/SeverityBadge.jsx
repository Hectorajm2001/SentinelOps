const styles = {
  CRITICAL: "bg-critical/20 text-critical border-critical/50",
  HIGH: "bg-warning/20 text-warning border-warning/50",
  MEDIUM: "bg-medium/20 text-medium border-medium/50",
  LOW: "bg-info/20 text-info border-info/50"
};

export default function SeverityBadge({ severity }) {
  const level = severity || "LOW";
  return (
    <span
      className={`rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-widest ${
        styles[level] || styles.LOW
      }`}
    >
      {level}
    </span>
  );
}
