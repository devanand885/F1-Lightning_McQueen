export interface Constructor {
  season: number;
  position: number | null;
  constructor_id: number;
  name: string;
  team_colour: string | null;
  points: number;
  wins: number;
  podiums: number;
  avg_finish: number | null;
  dnf_rate: number | null;
}

export interface ConstructorDetail extends Constructor {
  name_acronym: string | null;
}

export interface ConstructorResult {
  session_key: number;
  session_name: string;
  session_type: string;
  meeting_name: string;
  date_start: string | null;
  driver_number: number;
  driver_full_name: string;
  position: number | null;
  points: number | null;
  dnf: boolean | null;
  dns: boolean | null;
  dsq: boolean | null;
}

export interface ConstructorDriver {
  driver_number: number;
  full_name: string;
  name_acronym: string | null;
  headshot_url: string | null;
}

export interface ConstructorPitStop {
  session_key: number;
  session_type: string;
  driver_number: number;
  lap_number: number;
  date: string | null;
  pit_duration: number | null;
}
