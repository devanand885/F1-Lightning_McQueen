import { useQuery } from "@tanstack/react-query";

import { getReplay } from "../api/replay.api";

export function useReplay(sessionKey: number | null) {
  return useQuery({
    queryKey: ["replay", sessionKey],
    queryFn: () => getReplay(sessionKey as number),
    enabled: sessionKey !== null,
    staleTime: Infinity,
    // A first-time (uncached) fetch pulls tens of megabytes of raw
    // telemetry from OpenF1 and can genuinely take a minute or more - not
    // worth burning that twice on a transient failure.
    retry: 1,
  });
}
