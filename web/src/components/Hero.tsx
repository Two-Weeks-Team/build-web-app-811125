"use client";

export default function Hero({ stage }: { stage: string }) {
  return (
    <header className="rounded-lg border border-border bg-card p-4 shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-primary">Idea Foundry Studio</p>
          <h1 className="text-3xl font-bold leading-tight">Build Web App</h1>
          <p className="text-sm text-slate-700">Turn rough project notes into a traceable, presentation-ready product brief.</p>
        </div>
        <div className="rounded-md border border-border bg-muted px-3 py-2 text-sm">
          Workflow Rail: <span className="font-semibold text-primary">{stage}</span> · Distill · Review · Save
        </div>
      </div>
    </header>
  );
}
