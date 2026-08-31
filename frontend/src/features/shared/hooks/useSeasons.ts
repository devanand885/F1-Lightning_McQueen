import { useQuery } from "@tanstack/react-query";

import { getSeasons } from "../api/seasons.api";

export function useSeasons() {
  return useQuery({
    queryKey: ["seasons"],
    queryFn: getSeasons,
  });
}
