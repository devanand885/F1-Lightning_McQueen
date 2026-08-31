import { apiGet } from "@/lib/api/client";
import { ComparisonResponse } from "../types/compare.types";

export function compareDrivers(ids: number[], season?: number) {
  return apiGet<ComparisonResponse>("/compare/drivers", { ids: ids.join(","), season });
}

export function compareConstructors(ids: number[], season?: number) {
  return apiGet<ComparisonResponse>("/compare/constructors", { ids: ids.join(","), season });
}
