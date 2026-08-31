interface PanelProps {
  children: React.ReactNode;
  className?: string;
}

export default function Panel({ children, className = "" }: PanelProps) {
  return (
    <div
      className={`
        bg-bg-card
        border
        border-border
        rounded-lg
        p-4
        ${className}
      `}
    >
      {children}
    </div>
  );
}
