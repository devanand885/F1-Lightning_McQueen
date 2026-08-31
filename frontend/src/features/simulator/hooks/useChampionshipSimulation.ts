import { useQuery } from "@tanstack/react-query";

import { getChampionshipSimulation } from "../api/simulator.api";

export function useChampionshipSimulation(season?: number) {
  return useQuery({
    queryKey: ["simulator-championship", season],
    queryFn: () => getChampionshipSimulation(season),
  });
}
