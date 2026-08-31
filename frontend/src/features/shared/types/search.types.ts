export type SearchResultType = "driver" | "constructor" | "circuit" | "meeting" | "session";

export interface SearchResult {
  type: SearchResultType;
  id: number;
  title: string;
  subtitle: string | null;
}
