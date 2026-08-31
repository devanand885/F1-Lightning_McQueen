import { apiGet, ListResponse } from "@/lib/api/client";
import { CircuitDetail, CircuitSummary } from "../types/circuit.types";

export function getCircuits(season?: number, location?: string) {
  return apiGet<ListResponse<CircuitSummary>>("/circuits", { season, location: location || undefined });
}

export function getCircuit(circuitId: number | string) {
  return apiGet<CircuitDetail>(`/circuits/${circuitId}`);
}
