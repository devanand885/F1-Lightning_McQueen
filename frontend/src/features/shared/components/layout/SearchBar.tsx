import { Search } from "lucide-react";

interface Props {
  onOpen: () => void;
}

export default function SearchBar({ onOpen }: Props) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="
  flex
  items-center
  gap-2

  h-10

  w-full
  lg:w-[340px]

  px-3

  rounded-lg

  bg-bg-card
  border
  border-border

  hover:bg-bg-hover
  transition-colors
"
    >
      <Search size={14} className="text-text-muted" />

      <span className="text-sm text-text-muted">
        Search drivers, teams, circuits...
      </span>

      <kbd
        className="
          ml-auto

          px-1.5
          py-0.5

          text-[10px]

          rounded

          bg-bg-surface
          border
          border-border

          text-text-muted
        "
      >
        ⌘K
      </kbd>
    </button>
  );
}
