import PlaceholderPanel from "@/features/shared/components/ui/PlaceholderPanel";

export default function WindTunnelAvailabilityCard() {
  return (
    <PlaceholderPanel
      title="Wind Tunnel Availability"
      description="Wind tunnel allocation isn't sourced from OpenF1 - no data available."
      fill={false}
    />
  );
}
