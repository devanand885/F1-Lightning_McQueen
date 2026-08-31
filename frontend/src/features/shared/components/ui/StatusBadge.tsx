type Variant = "success" | "warning" | "danger" | "neutral";

interface Props {
  label: string;
  variant?: Variant;
}

export default function StatusBadge({ label, variant = "neutral" }: Props) {
  const styles = {
    success: "bg-success/10 text-success border-success/20",
    warning: "bg-warning/10 text-warning border-warning/20",
    danger: "bg-primary/10 text-primary border-primary/20",
    neutral: "bg-bg-surface text-text-secondary border-border",
  };

  return (
    <span
      className={`
        px-2
        py-1
        text-xs
        border
        rounded
        ${styles[variant]}
      `}
    >
      {label}
    </span>
  );
}
