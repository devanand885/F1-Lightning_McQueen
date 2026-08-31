interface Props {
  children: React.ReactNode;
  height?: number;
}

export default function ChartContainer({
  children,
  height = 320,
}: Props) {
  return (
    <div
      className="
        bg-bg-card
        border
        border-border
        rounded-lg
        p-4
      "
      style={{
        height,
      }}
    >
      {children}
    </div>
  );
}