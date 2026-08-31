import PlaceholderPanel from "@/features/shared/components/ui/PlaceholderPanel";

export default function PerformanceEfficiencyScatter() {
  return (
    <PlaceholderPanel
      title="Performance Efficiency"
      subtitle="Aero load / lap delta correlation"
      description="Needs telemetry-derived aero load estimates - part of the upcoming analytical layer."
      className="min-h-[300px]"
    />
  );
}
