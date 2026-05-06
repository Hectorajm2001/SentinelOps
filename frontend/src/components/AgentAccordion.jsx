import { useState } from "react";

export default function AgentAccordion({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="rounded-xl border border-white/10 bg-white/5">
      <button
        className="flex w-full items-center justify-between px-4 py-3 text-left"
        onClick={() => setOpen((value) => !value)}
      >
        <span className="text-sm font-semibold text-slate-100">{title}</span>
        <span className="text-xs text-slate-400">{open ? "-" : "+"}</span>
      </button>
      {open && <div className="border-t border-white/10 px-4 py-3 text-xs">{children}</div>}
    </div>
  );
}
