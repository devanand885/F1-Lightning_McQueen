export interface Driver {
  season: number;
  position: number | null;
  driver_number: number;
  full_name: string;
  name_acronym: string | null;
  headshot_url: string | null;
  country_code: string | null;
  team_id: number | null;
  team_name: string | null;
  team_colour: string | null;
  points: number;
  wins: number;
  podiums: number;
  avg_finish: number | null;
  dnf_rate: number | null;
}

export interface DriverDetail extends Driver {
  first_name: string | null;
  last_name: string | null;
  broadcast_name: string | null;
}

export interface DriverResult {
  session_key: number;
  session_name: string;
  session_type: string;
  meeting_name: string;
  date_start: string | null;
  position: number | null;
  points: number | null;
  dnf: boolean | null;
  dns: boolean | null;
  dsq: boolean | null;
}
