"use client";

const seeds = [
  "Campus TaskMate",
  "FocusFlow",
  "LabSync Planner",
  "PitchDraft",
  "RoutineForge"
];

export default function ReferenceShelf() {
  return (
    <section className="rounded-lg border border-border bg-card p-5 shadow-card">
      <h3 className="text-xl">Artifact Shelf · Sample Final-Year Seeds</h3>
      <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {seeds.map((seed, idx) => (
          <article key={seed} className="rounded-md border border-border bg-background p-3">
            <p className="text-sm font-semibold">{seed}</p>
            <p className="mt-2 text-xs text-foreground/70">Pinned · {idx % 2 === 0 ? "Saved" : "Ready"} · Traceable</p>
          </article>
        ))}
      </div>
    </section>
  );
}
