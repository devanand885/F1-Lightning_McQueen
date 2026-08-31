export interface ArchetypeDriver {
  driver_id: number;
  full_name: string;
  pca_x: number;
  pca_y: number;
}

export interface ArchetypeCluster {
  cluster: number;
  name: string;
  size: number;
  centroid: Record<string, number>;
  drivers: ArchetypeDriver[];
}

export interface ExcludedDriver {
  driver_id: number;
  full_name: string;
  race_sessions: number;
  usable_race_laps: number;
  race_stints: number;
}

export interface ArchetypesResponse {
  available: boolean;
  reason: string | null;
  run_id: string | null;
  features: string[] | null;
  silhouette: number | null;
  pca_explained_variance_ratio: number[] | null;
  n_eligible: number | null;
  n_population: number | null;
  clusters: ArchetypeCluster[];
  excluded_drivers: ExcludedDriver[];
}
