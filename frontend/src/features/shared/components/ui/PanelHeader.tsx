interface Props {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export default function PanelHeader({ title, subtitle, action }: Props) {
  return (
    <div className="flex items-start justify-between mb-4">
      <div>
        <h3
          className="
            text-[11px]
            uppercase
            tracking-[0.18em]

            text-primary
            font-semibold
          "
        >
          {title}
        </h3>

        {subtitle && <p className="text-xs text-text-muted mt-1">{subtitle}</p>}
      </div>

      {action}
    </div>
  );
}
