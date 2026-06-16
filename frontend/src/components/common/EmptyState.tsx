type EmptyStateProps = {
  message?: string;
};

export function EmptyState({ message = "No data available." }: EmptyStateProps) {
  return <p className="muted">{message}</p>;
}
