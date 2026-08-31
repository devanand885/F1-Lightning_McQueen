import ConstructorAnalyticsPage from "@/features/constructors/pages/ConstructorAnalyticsPage";

interface Props {
  params: Promise<{
    constructorId: string;
  }>;
}

export default async function Page({ params }: Props) {
  const { constructorId } = await params;

  return <ConstructorAnalyticsPage constructorId={constructorId} />;
}
