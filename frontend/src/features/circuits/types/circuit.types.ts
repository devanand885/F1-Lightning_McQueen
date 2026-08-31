export interface CircuitSummary {
  circuit_id: number;
  circuit_key: number;
  circuit_short_name: string;
  location: string | null;
  country_name: string | null;
  country_code: string | null;
  seasons: number[];
}

export interface CircuitMeeting {
  meeting_key: number;
  meeting_name: string;
  season: number;
  date_start: string | null;
}

export interface CircuitDetail {
  circuit_id: number;
  circuit_key: number;
  circuit_short_name: string;
  location: string | null;
  country_name: string | null;
  country_code: string | null;
  meetings: CircuitMeeting[];
  drivers: string[];
  constructors: string[];
  circuit_type: string | null;
  mean_st_speed: number | null;
  mean_field_cov: number | null;
  mean_stints_per_driver: number | null;
}
