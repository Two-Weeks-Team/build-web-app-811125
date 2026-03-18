export type PlanRequest = {
  query: string;
  preferences: string;
};

export type PlanResponse = {
  summary: string;
  items: Array<{ section: string; content: string; traces: string[] }>;
  score: number;
};

export type InsightsRequest = {
  selection: string;
  context: string;
};

export type InsightsResponse = {
  insights: string[];
  next_actions: string[];
  highlights: string[];
};

export async function postPlan(payload: PlanRequest): Promise<PlanResponse> {
  const res = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to distill brief");
  return res.json();
}

export async function postInsights(payload: InsightsRequest): Promise<InsightsResponse> {
  const res = await fetch("/api/insights", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to fetch insights");
  return res.json();
}
