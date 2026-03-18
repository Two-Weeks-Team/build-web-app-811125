"use client";

export default function StatsStrip() {
  const stats = [
    { label: "Pinned Dossiers", value: "4", tone: "text-success" },
    { label: "Trace Links", value: "27", tone: "text-primary" },
    { label: "Ready for Review", value: "2", tone: "text-warning" }
  ];

  return (
    <section className="grid gap-3 sm:grid-cols-3">
      {stats.map((s) => (
        <div key={s.label} className="rounded-md border border-border bg-card p-3 shadow-soft">
          <p className="text-xs uppercase tracking-wider text-foreground/60">{s.label}</p>
          <p className={`text-2xl font-bold ${s.tone}`}>{s.value}</p>
        </div>
      ))}
    </section>
  );
}
