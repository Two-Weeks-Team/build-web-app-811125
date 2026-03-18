"use client";

import { useEffect, useState } from "react";
import { postInsights } from "@/lib/api";

export default function InsightPanel({ selectedSection }: { selectedSection: string }) {
  const [state, setState] = useState<"loading"|"success"|"error">("loading");
  const [insights, setInsights] = useState<string[]>([]);

  useEffect(() => {
    let active = true;
    setState("loading");
    postInsights({ selection: selectedSection, context: "Campus TaskMate seed context" })
      .then((res) => {
        if (!active) return;
        setInsights(res.insights);
        setState("success");
      })
      .catch(() => active && setState("error"));
    return () => { active = false; };
  }, [selectedSection]);

  return (
    <section className="fade-in rounded-lg border border-border bg-card p-4 shadow-soft">
      <h2 className="text-xl font-semibold">Structured Brief Dossier</h2>
      {state === "loading" && <p className="text-sm text-slate-600">Generating section linkage and highlights...</p>}
      {state === "error" && <p className="text-sm text-red-700">Could not load insights. Retry by selecting another section.</p>}
      {state === "success" && (
        <ul className="mt-2 space-y-2">
          {insights.map((i, idx) => <li key={idx} className="rounded-md border border-border bg-muted p-2 text-sm">{i}</li>)}
        </ul>
      )}
      <div className="mt-4 rounded-md border border-dashed border-border p-3 text-xs text-slate-700">
        Source Trace View: selecting <span className="font-semibold text-primary">{selectedSection}</span> illuminates supporting phrases in intake notes.
      </div>
    </section>
  );
}
