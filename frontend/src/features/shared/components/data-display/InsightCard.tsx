interface Props {
  severity: "HIGH" | "MEDIUM" | "LOW";

  title: string;

  description: string;

  timestamp?: string;
}

export default function InsightCard({
  severity,
  title,
  description,
  timestamp,
}: Props) {
  const severityClass = {
    HIGH: "text-primary",
    MEDIUM: "text-warning",
    LOW: "text-success",
  };

  return (
    <div
      className="
        py-3

        border-b
        border-border
      "
    >
      <div
        className="
          flex
          items-center
          justify-between
          mb-2
        "
      >
        <span
          className={`
            text-[10px]
            uppercase
            tracking-[0.18em]
            font-semibold

            ${severityClass[severity]}
          `}
        >
          {severity}
        </span>

        {timestamp && (
          <span
            className="
              text-[10px]
              text-text-muted
            "
          >
            {timestamp}
          </span>
        )}
      </div>

      <h4
        className="
          text-sm
          font-semibold

          text-text-primary
        "
      >
        {title}
      </h4>

      <p
        className="
          mt-2

          text-xs
          leading-5

          text-text-secondary
        "
      >
        {description}
      </p>
    </div>
  );
}