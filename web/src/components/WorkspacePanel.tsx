"use client";

import { useState } from "react";
import { postPlan } from "@/lib/api";

const seed = "Campus TaskMate: Supervisor notes mention students missing deadlines, unclear milestone visibility, and weak feedback loops. Build a lightweight assignment planning app with weekly sprint plans, reminder nudges, and submission-readiness checkpoints.";

export default function WorkspacePanel({ selectedSection, setSelectedSection }: { selectedSection: string; setSelectedSection: (s: string) => void }) {
  const [query, setQuery] = useState(seed);
  const [preferences, setPreferences] = useState("Academic framing, final-year feasibility, MVP in 8 weeks");
  const [loading, setLoading] = useState(false);

  return (
    <section className="fade-in rounded-lg border border-border bg-card p-4 shadow-soft">
      <h2 className="text-xl font-semibold">Rough Intake Canvas</h2>
      <p className="mb-3 text-sm text-slate-700">Paste source notes and distill in one pass. Click section chips to inspect trace linkage.</p>
      <textarea value={query} onChange={(e) => setQuery(e.target.value)} className="h-44 w-full rounded-md border border-border p-3" />
      <textarea value={preferences} onChange={(e) => setPreferences(e.target.value)} className="mt-3 h-20 w-full rounded-md border border-border p-3" />
      <div className="mt-3 flex flex-wrap gap-2">
        {['problem','target_users','solution','features','workflow'].map((s) => (
          <button key={s} onClick={() => setSelectedSection(s)} className={`rounded-full border px-3 py-1 text-xs ${selectedSection===s?'border-primary text-primary':'border-border'}`}>
            {s.replace('_',' ')}
          </button>
        ))}
      </div>
      <button
        onClick={async () => {
          setLoading(true);
          try { await postPlan({ query, preferences }); } finally { setLoading(false); }
        }}
        className="mt-4 rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white"
      >
        {loading ? "Distilling..." : "Distill Into Brief"}
      </button>
    </section>
  );
}
