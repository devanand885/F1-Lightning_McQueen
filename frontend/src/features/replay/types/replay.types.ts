export interface RaceOption {
  session_key: number;
  season: number;
  meeting_name: string;
  circuit_short_name: string | null;
  date_start: string | null;
}

export interface RaceListResponse {
  items: RaceOption[];
}

export interface ReplayBounds {
  min_x: number;
  max_x: number;
  min_y: number;
  max_y: number;
  span: number;
  space: number;
}

export interface DriverFrames {
  driver_number: number;
  full_name: string;
  name_acronym: string | null;
  constructor_name: string;
  team_colour: string | null;
  x: (number | null)[];
  y: (number | null)[];
  speed: (number | null)[];
  throttle: (number | null)[];
  brake: (number | null)[];
  gear: (number | null)[];
  drs: (number | null)[];
  lap: (number | null)[];
  position: (number | null)[];
}

export interface ReplayResponse {
  available: boolean;
  reason: string | null;
  session_key: number | null;
  meeting_name: string | null;
  season: number | null;
  date_from: string | null;
  date_to: string | null;
  grid_step_seconds: number | null;
  frame_count: number | null;
  timestamps: number[];
  total_laps: number | null;
  circuit_outline: [number, number][];
  bounds: ReplayBounds | null;
  has_car_data: boolean;
  drivers: Record<string, DriverFrames>;
}
