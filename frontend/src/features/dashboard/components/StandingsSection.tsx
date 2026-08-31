import { Driver } from "@/features/drivers/types/driver.types";
import { Constructor } from "@/features/constructors/types/constructor.types";
import DriverStandingsTable from "./DriversStandingsTable";
import ConstructorStandingsTable from "./ConstructorsStandingTable";

interface Props {
  drivers: Driver[];
  constructors: Constructor[];
}

export default function StandingsSection({ drivers, constructors }: Props) {
  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <DriverStandingsTable drivers={drivers} />
      <ConstructorStandingsTable constructors={constructors} />
    </div>
  );
}
