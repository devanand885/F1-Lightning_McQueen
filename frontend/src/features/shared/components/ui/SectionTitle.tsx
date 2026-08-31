interface Props {
  title: string;
  subtitle?: string;
}

export default function SectionTitle({
  title,
  subtitle,
}: Props) {
  return (
    <div>
      <h1 className="text-3xl font-bold text-text-primary">
        {title}
      </h1>

      {subtitle && (
        <p className="mt-1 text-sm text-text-secondary">
          {subtitle}
        </p>
      )}
    </div>
  );
}