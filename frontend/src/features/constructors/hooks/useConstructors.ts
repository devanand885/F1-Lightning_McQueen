import { useQuery } from "@tanstack/react-query";

import { getConstructors } from "../api/constructors.api";

export function useConstructors(season?: number) {
  return useQuery({
    queryKey: ["constructors", season],
    queryFn: () => getConstructors(season),
  });
}
