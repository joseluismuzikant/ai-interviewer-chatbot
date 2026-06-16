type StatusBadgeProps = {
  status: string | null | undefined;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = (status || "UNKNOWN").toUpperCase();
  return <span className={`status-badge status-${normalized.toLowerCase()}`}>{normalized}</span>;
}
