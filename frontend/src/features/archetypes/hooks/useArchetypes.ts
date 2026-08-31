import { useQuery } from "@tanstack/react-query";

import { getArchetypes } from "../api/archetypes.api";

export function useArchetypes() {
  return useQuery({
    queryKey: ["archetypes"],
    queryFn: getArchetypes,
  });
}
