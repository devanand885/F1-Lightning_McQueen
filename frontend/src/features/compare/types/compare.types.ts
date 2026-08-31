export type CompareEntityType = "driver" | "constructor";

export interface CompareEntity {
  id: number;
  label: string;
  colour: string | null;
}

export interface CompareMetric {
  key: string;
  label: string;
  unit: string | null;
  values: (number | string | null)[];
}

export interface ComparisonResponse {
  entity_type: CompareEntityType;
  season: number;
  entities: CompareEntity[];
  metrics: CompareMetric[];
  analytics?: CompareMetric[] | null;
}
