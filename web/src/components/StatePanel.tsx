"use client";

export default function StatePanel({ status }: { status: "loading" | "empty" | "error" | "success" }) {
  const content = {
    loading: "Distilling source notes into Product Brief sections...",
    empty: "No dossier selected. Open a sample seed to begin.",
    error: "Could not distill this pass. Check constraints and retry.",
    success: "Distilled successfully. Select a section to reveal source traces."
  }[status];

  return (
    <section className="rounded-lg border border-border bg-card p-5 shadow-card">
      <h3 className="text-xl">Workflow Rail: Intake · Distill · Review · Save</h3>
      <p className="mt-3 text-sm">{content}</p>
      <div className="mt-4 rounded-md border border-border bg-muted p-3 text-sm">Status stamp: {status.toUpperCase()}</div>
    </section>
  );
}
