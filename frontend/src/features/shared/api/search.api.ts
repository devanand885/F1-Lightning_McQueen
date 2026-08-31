import { apiGet, ListResponse } from "@/lib/api/client";
import { SearchResult } from "../types/search.types";

export function search(query: string) {
  return apiGet<ListResponse<SearchResult>>("/search", { q: query });
}
