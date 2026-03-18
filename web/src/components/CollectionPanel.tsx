"use client";

const artifacts = [
  { id: "a1", title: "Campus TaskMate Dossier", status: "Saved", time: "2 min ago" },
  { id: "a2", title: "FocusFlow Brief v2", status: "Distilled", time: "11 min ago" },
  { id: "a3", title: "LabSync Planner", status: "Ready", time: "26 min ago" }
];

export default function CollectionPanel({ activeArtifactId, setActiveArtifactId }: { activeArtifactId: string | null; setActiveArtifactId: (id: string) => void }) {
  return (
    <section className="mt-4 rounded-lg border border-border bg-card p-4 shadow-soft">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-lg font-semibold">Artifact Shelf · Saved Project Dossiers</h3>
        <span className="text-xs uppercase tracking-wider text-slate-500">Pinned board view</span>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        {artifacts.map((a) => (
          <button key={a.id} onClick={() => setActiveArtifactId(a.id)} className={`rounded-lg border p-3 text-left transition ${activeArtifactId===a.id?'border-primary':'border-border'} bg-muted/40 hover:bg-muted`}>
            <p className="font-semibold">{a.title}</p>
            <p className="text-xs text-slate-600 mt-1">{a.time}</p>
            <span className="mt-2 inline-block rounded-full border border-border px-2 py-0.5 text-xs">{a.status}</span>
          </button>
        ))}
      </div>
    </section>
  );
}