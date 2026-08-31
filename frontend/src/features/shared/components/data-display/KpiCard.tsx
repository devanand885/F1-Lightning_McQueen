import React from "react";

interface Props {
  title: string;

  value: string;
  suffix?: string;

  footer?: string;

  trend?: string;
  positive?: boolean;

  status?: string;

  progress?: number;

  icon?: React.ReactNode;
}

export default function KpiCard({
  title,
  value,
  suffix,
  footer,
  trend,
  positive,
  status,
  progress,
  icon,
}: Props) {
  return (
    <div
      className="
        bg-bg-card
        border
        border-border

        px-3
        py-3
        sm:px-4

        min-h-[110px]
        sm:min-h-[120px]
        xl:min-h-[128px]

        flex
        flex-col
        justify-between
      "
    >
      {/* Header */}

      <div className="flex items-center justify-between">
        <span
          className="
            text-[9px]
            sm:text-[10px]

            uppercase
            tracking-[0.16em]
            font-medium

            text-primary
          "
        >
          {title}
        </span>

        <div
          className="
            text-primary
            opacity-80
            shrink-0
          "
        >
          {icon}
        </div>
      </div>

      {/* Value */}

      <div>
        <div
          className="
            flex
            items-end
            gap-1
            overflow-hidden
          "
        >
          <span
            className="
              text-[36px]
              sm:text-[42px]
              xl:text-[52px]

              leading-none
              font-light
              tracking-tight

              text-text-primary

              truncate
            "
          >
            {value}
          </span>

          {suffix && (
            <span
              className="
                text-sm
                sm:text-base
                xl:text-xl

                pb-1

                text-text-secondary

                shrink-0
              "
            >
              {suffix}
            </span>
          )}
        </div>

        {/* Progress Bar */}

        {progress !== undefined && (
          <div
            className="
              mt-3

              h-[4px]

              bg-bg-hover

              overflow-hidden
            "
          >
            <div
              className="h-full bg-primary"
              style={{
                width: `${progress}%`,
              }}
            />
          </div>
        )}
      </div>

      {/* Footer */}

      <div
        className="
          flex
          flex-wrap
          items-center
          justify-between
          gap-2
        "
      >
        <div
          className="
            text-[9px]
            sm:text-[10px]
            xl:text-[11px]

            uppercase
            tracking-wide

            text-text-secondary
          "
        >
          {footer}
        </div>

        <div className="flex items-center gap-2">
          {status && (
            <span
              className={`
                px-2
                py-[2px]

                text-[8px]
                sm:text-[9px]
                xl:text-[10px]

                font-semibold
                uppercase
                tracking-wide

                ${
                  status === "OPTIMAL"
                    ? "bg-success/15 text-success"
                    : "text-primary"
                }
              `}
            >
              {status}
            </span>
          )}

          {trend && (
            <span
              className={`
                text-xs
                sm:text-sm

                font-medium

                ${
                  positive
                    ? "text-primary"
                    : "text-danger"
                }
              `}
            >
              ↗ {trend}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}