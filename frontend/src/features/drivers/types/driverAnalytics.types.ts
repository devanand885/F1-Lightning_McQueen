export interface PaceTrendPoint {
  session_id: number;
  meeting_name: string | null;
  date_start: string | null;
  race_pace_field_relative: number | null;
  qualifying_pace_field_relative: number | null;
}

export interface CircuitTypeBreakdownEntry {
  circuit_type: string;
  race_pace_teammate_relative: number;
  n_sessions: number;
}

export interface ArchetypeAssignment {
  assigned: boolean;
  reason?: string | null;
  cluster?: number | null;
  archetype_name?: string | null;
  model_run_id?: string | null;
}

export interface DriverAnalytics {
  driver_number: number;
  full_name: string;
  eligible: boolean;
  eligibility_reason: string | null;

  race_sessions: number;
  qualifying_sessions: number;
  usable_race_laps: number;
  race_stints: number;

  race_pace_field_relative: number | null;
  qualifying_pace_field_relative: number | null;
  race_pace_teammate_relative: number | null;
  qualifying_pace_teammate_relative: number | null;

  degradation_slope: number | null;
  degradation_stints_used: number | null;

  consistency_cv: number | null;
  start_performance_delta: number | null;

  dry_laps: number;
  wet_laps: number;
  dry_pace_ratio: number | null;
  wet_pace_ratio: number | null;
  wet_sample_sufficient: boolean;
  wet_sample_threshold: number | null;

  pace_trend: PaceTrendPoint[];
  circuit_type_breakdown: CircuitTypeBreakdownEntry[];
  archetype: ArchetypeAssignment | null;
}
