const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export type ExportFormat = "csv" | "json";

export async function downloadExport(dataset: string, format: ExportFormat, season?: number): Promise<void> {
  const url = new URL(`${API_BASE_URL}/export/${dataset}`);
  url.searchParams.set("format", format);
  if (season !== undefined) url.searchParams.set("season", String(season));

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Export failed: ${response.status} ${response.statusText}`);
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = `${dataset}_${season ?? "latest"}.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}
