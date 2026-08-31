import DriverAnalyticsPage from "@/features/drivers/pages/DriversAnalyticsPage";

interface Props {
  params: Promise<{
    driverNumber: string;
  }>;
}

export default async function Page({
  params,
}: Props) {
  const { driverNumber } = await params;

  return (
    <DriverAnalyticsPage
      driverNumber={driverNumber}
    />
  );
}