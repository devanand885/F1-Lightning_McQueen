import { apiGet, ListResponse } from "@/lib/api/client";
import { Driver, DriverDetail, DriverResult } from "../types/driver.types";

export function getDrivers(season?: number) {
  return apiGet<ListResponse<Driver>>("/drivers", { season });
}

export function getDriver(driverNumber: number | string, season?: number) {
  return apiGet<DriverDetail>(`/drivers/${driverNumber}`, { season });
}

export function getDriverResults(driverNumber: number | string, season?: number) {
  return apiGet<ListResponse<DriverResult>>(`/drivers/${driverNumber}/results`, { season });
}
