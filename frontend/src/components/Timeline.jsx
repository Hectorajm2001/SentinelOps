export default function Timeline({ items = [] }) {
  return (
    <div className="space-y-3">
      {items.map((item, index) => (
        <div key={`${item.ts}-${index}`} className="flex items-start gap-3 text-xs">
          <div className="mt-1 h-2 w-2 rounded-full bg-accent" />
          <div>
            <div className="text-slate-300">{item.event}</div>
            <div className="text-slate-500">{new Date(item.ts).toLocaleString()}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
