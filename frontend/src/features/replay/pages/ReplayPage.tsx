"use client";

import { useState } from "react";

import PlaceholderPanel from "@/features/shared/components/ui/PlaceholderPanel";
import { useReplayRaces } from "../hooks/useReplayRaces";
import RaceSelector from "../components/RaceSelector";
import ReplaySession from "../components/ReplaySession";

export default function ReplayPage() {
  const racesQuery = useReplayRaces();
  const [sessionKey, setSessionKey] = useState<number | null>(null);

  return (
    <div className="space-y-3">
      <RaceSelector races={racesQuery.data?.items ?? []} onLoad={setSessionKey} />

      {sessionKey === null && (
        <PlaceholderPanel
          title="No race loaded"
          description="Choose a season and race above, then click Load Replay."
        />
      )}

      {sessionKey !== null && <ReplaySession key={sessionKey} sessionKey={sessionKey} />}
    </div>
  );
}
