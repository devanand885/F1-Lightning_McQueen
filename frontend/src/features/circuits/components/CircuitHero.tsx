import { CircuitDetail } from "../types/circuit.types";

interface Props {
  circuit: CircuitDetail;
}

export default function CircuitHero({ circuit }: Props) {
  return (
    <section className="border border-border bg-[#0d0d0d] p-5 sm:p-7">
      <div className="text-[9px] font-semibold uppercase tracking-[0.18em] text-primary">
        Circuit Profile
      </div>
      <h1 className="mt-2 text-3xl font-black uppercase tracking-[-0.04em] text-text-primary sm:text-5xl">
        {circuit.circuit_short_name}
      </h1>
      <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1 text-[10px] uppercase tracking-[0.14em] text-text-muted">
        {circuit.location && <span>{circuit.location}</span>}
        {circuit.country_name && <span>{circuit.country_name}</span>}
        <span>
          {circuit.meetings.length} meeting{circuit.meetings.length === 1 ? "" : "s"} on record
        </span>
        {circuit.circuit_type && (
          <span
            title="Derived from real speed-trap and field-spread data across this circuit's race sessions"
            className="rounded border border-primary/30 bg-primary/10 px-2 py-0.5 text-primary normal-case tracking-normal"
          >
            {circuit.circuit_type}
          </span>
        )}
      </div>
    </section>
  );
}
