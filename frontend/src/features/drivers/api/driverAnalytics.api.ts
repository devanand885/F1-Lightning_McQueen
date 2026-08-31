import { apiGet } from "@/lib/api/client";
import { DriverAnalytics } from "../types/driverAnalytics.types";

export function getDriverAnalytics(driverNumber: number | string) {
  return apiGet<DriverAnalytics>(`/drivers/${driverNumber}/analytics`);
}
