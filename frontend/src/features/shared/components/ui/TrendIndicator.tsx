interface Props {
  value: string;
  positive?: boolean;
}

export default function TrendIndicator({
  value,
  positive = true,
}: Props) {
  return (
    <span
      className={`
        text-xs
        font-medium
        ${
          positive
            ? "text-success"
            : "text-danger"
        }
      `}
    >
      {positive ? "▲" : "▼"} {value}
    </span>
  );
}