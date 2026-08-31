interface Row {
  position: number;
  name: string;
  points: number;
}

interface Props {
  rows: Row[];
}

export default function StandingsTable({
  rows,
}: Props) {
  return (
    <table className="w-full">
      <thead>
        <tr className="text-left text-xs text-text-muted border-b border-border">
          <th className="py-2">POS</th>
          <th>NAME</th>
          <th>PTS</th>
        </tr>
      </thead>

      <tbody>
        {rows.map((row) => (
          <tr
            key={row.position}
            className="border-b border-border"
          >
            <td className="py-3 text-text-secondary">
              {row.position}
            </td>

            <td className="text-text-primary">
              {row.name}
            </td>

            <td className="text-text-primary">
              {row.points}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}