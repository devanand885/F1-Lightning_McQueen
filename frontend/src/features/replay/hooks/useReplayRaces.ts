import { useQuery } from "@tanstack/react-query";

import { getReplayRaces } from "../api/replay.api";

export function useReplayRaces() {
  return useQuery({
    queryKey: ["replay-races"],
    queryFn: getReplayRaces,
    staleTime: 5 * 60 * 1000,
  });
}
