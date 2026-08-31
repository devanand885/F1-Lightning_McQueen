import { apiGet, ListResponse } from "@/lib/api/client";

export function getSeasons() {
  return apiGet<ListResponse<number>>("/seasons");
}
