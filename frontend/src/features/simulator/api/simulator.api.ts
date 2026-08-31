import { apiGet } from "@/lib/api/client";
import { SimulationResponse } from "../types/simulator.types";

export function getChampionshipSimulation(season?: number) {
  return apiGet<SimulationResponse>("/simulator/championship", { season });
}
