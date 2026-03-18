"use client";

import { useState } from "react";
import { postPlan } from "@/lib/api";

export default function FeaturePanel({ setStatus }: { setStatus: (s: "loading" | "empty" | "error" | "success") => void }) {
  const [query, setQuery] = useState(
    "Campus TaskMate started from messy supervisor comments: students miss deadlines, want weekly planning, and need reminders tied to submission rubrics. We need a mobile-first workflow that converts random notes into a structured planning brief for final-year projects."
  );
  const [preferences, setPreferences] = useState("Academic framing, student audience, scoped MVP");
  const [summary, setSummary] = useState("One-pass distillation ready. Click Distill Into Brief to regenerate.");

  const run = async () => {
    try {
      setStatus("loading");
      const res = await postPlan({ query, preferences });
      setSummary(`${res.summary} (Readiness score ${res.score})`);
      setStatus("success");
    } catch {
      setStatus("error");
    }
  };

  return (
    <section className="rounded-lg border border-border bg-card p-5 shadow-card space-y-4">
      <h2 className="text-2xl">Rough Intake Canvas → Structured Brief Dossier</h2>
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="min-h-40 w-full rounded-md border border-border bg-background p-3 text-sm"
      />
      <input
        value={preferences}
        onChange={(e) => setPreferences(e.target.value)}
        className="w-full rounded-md border border-border bg-background p-3 text-sm"
      />
      <button
        onClick={run}
        className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white hover:opacity-90 transition"
      >
        Distill Into Brief
      </button>
      <p className="rounded-md border border-success/30 bg-success/10 p-3 text-sm">{summary}</p>
    </section>
  );
}
