import { CircuitSummary } from "../types/circuit.types";
import CircuitCard from "./CircuitCard";

interface Props {
  circuits: CircuitSummary[];
}

export default function CircuitsGrid({ circuits }: Props) {
  const sorted = [...circuits].sort((a, b) => a.circuit_short_name.localeCompare(b.circuit_short_name));

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {sorted.map((circuit) => (
        <CircuitCard key={circuit.circuit_id} circuit={circuit} />
      ))}
    </div>
  );
}
