interface Props {
  seasons: number[];
  value: number | undefined;
  onChange: (year: number) => void;
}

export default function SeasonSelect({ seasons, value, onChange }: Props) {
  if (seasons.length === 0) return null;

  const selected = value ?? seasons[0];

  return (
    <select
      value={selected}
      onChange={(event) => onChange(Number(event.target.value))}
      className="h-9 border border-border bg-bg-card px-2 text-xs text-text-secondary focus:border-primary/50 focus:outline-none"
    >
      {seasons.map((year) => (
        <option key={year} value={year}>
          Season {year}
        </option>
      ))}
    </select>
  );
}
