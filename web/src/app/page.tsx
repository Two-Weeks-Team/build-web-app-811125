"use client";

import { useMemo, useState } from "react";
import Hero from "@/components/Hero";
import WorkspacePanel from "@/components/WorkspacePanel";
import InsightPanel from "@/components/InsightPanel";
import CollectionPanel from "@/components/CollectionPanel";

export default function Page() {
  const [selectedSection, setSelectedSection] = useState<string>("problem");
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);

  const stage = useMemo(() => {
    if (!activeArtifactId) return "Intake";
    return "Review";
  }, [activeArtifactId]);

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-[1400px] px-4 py-6 md:px-8">
        <Hero stage={stage} />
        <div className="mt-5 grid gap-4 lg:grid-cols-[1.1fr_1fr]">
          <WorkspacePanel selectedSection={selectedSection} setSelectedSection={setSelectedSection} />
          <InsightPanel selectedSection={selectedSection} />
        </div>
        <CollectionPanel activeArtifactId={activeArtifactId} setActiveArtifactId={setActiveArtifactId} />
      </div>
    </main>
  );
}
