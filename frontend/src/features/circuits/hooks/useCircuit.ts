import { useQuery } from "@tanstack/react-query";

import { getCircuit } from "../api/circuits.api";

export function useCircuit(circuitId: string) {
  return useQuery({
    queryKey: ["circuit", circuitId],
    queryFn: () => getCircuit(circuitId),
    enabled: !!circuitId,
  });
}
