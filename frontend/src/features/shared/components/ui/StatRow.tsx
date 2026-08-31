interface Props {
  label: string;
  value: string;
}

export default function StatRow({
  label,
  value,
}: Props) {
  return (
    <div className="flex justify-between py-2">
      <span className="text-sm text-text-secondary">
        {label}
      </span>

      <span className="text-sm text-text-primary font-medium">
        {value}
      </span>
    </div>
  );
}