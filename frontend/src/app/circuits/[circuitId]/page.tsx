import CircuitDetailPage from "@/features/circuits/pages/CircuitDetailPage";

interface Props {
  params: Promise<{
    circuitId: string;
  }>;
}

export default async function Page({ params }: Props) {
  const { circuitId } = await params;

  return <CircuitDetailPage circuitId={circuitId} />;
}
