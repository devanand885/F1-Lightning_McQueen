export interface SimulatedDriver {
  driver_number: number;
  full_name: string;
  current_points: number;
  expected_points: number;
  expected_championship_position: number;
  championship_win_probability: number;
  championship_podium_probability: number;
  race_win_probability: number;
  race_podium_probability: number;
}

export interface SimulationResponse {
  available: boolean;
  reason: string | null;
  season: number;
  n_remaining_races: number | null;
  n_completed_races: number | null;
  n_simulations: number | null;
  seed: number | null;
  drivers: SimulatedDriver[];
}
