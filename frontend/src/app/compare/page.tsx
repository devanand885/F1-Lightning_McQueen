import { Suspense } from "react";

import ComparePage from "@/features/compare/pages/ComparePage";

export default function Page() {
  return (
    <Suspense
      fallback={<div className="text-xs uppercase tracking-widest text-text-muted py-8">Loading...</div>}
    >
      <ComparePage />
    </Suspense>
  );
}
