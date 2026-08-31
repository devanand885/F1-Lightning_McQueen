import { apiGet } from "@/lib/api/client";
import { RaceListResponse, ReplayResponse } from "../types/replay.types";

export function getReplayRaces() {
  return apiGet<RaceListResponse>("/replay/races");
}

export function getReplay(sessionKey: number) {
  return apiGet<ReplayResponse>(`/replay/${sessionKey}`);
}
