import { apiGet, ListResponse } from "@/lib/api/client";
import {
  Constructor,
  ConstructorDetail,
  ConstructorDriver,
  ConstructorPitStop,
  ConstructorResult,
} from "../types/constructor.types";

export function getConstructors(season?: number) {
  return apiGet<ListResponse<Constructor>>("/constructors", { season });
}

export function getConstructor(constructorId: number | string, season?: number) {
  return apiGet<ConstructorDetail>(`/constructors/${constructorId}`, { season });
}

export function getConstructorResults(constructorId: number | string, season?: number) {
  return apiGet<ListResponse<ConstructorResult>>(`/constructors/${constructorId}/results`, { season });
}

export function getConstructorDrivers(constructorId: number | string, season?: number) {
  return apiGet<ListResponse<ConstructorDriver>>(`/constructors/${constructorId}/drivers`, { season });
}

export function getConstructorPitStops(constructorId: number | string, season?: number) {
  return apiGet<ListResponse<ConstructorPitStop>>(`/constructors/${constructorId}/pit-stops`, { season });
}
