import { apiGet } from "@/lib/api/client";
import { ArchetypesResponse } from "../types/archetype.types";

export function getArchetypes() {
  return apiGet<ArchetypesResponse>("/archetypes");
}
