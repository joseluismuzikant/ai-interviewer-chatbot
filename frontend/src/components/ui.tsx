import { ReactNode } from "react";

type ClassNameProps = {
  children: ReactNode;
  className?: string;
};

function joinClasses(...classNames: Array<string | undefined>): string {
  return classNames.filter(Boolean).join(" ");
}

export function PageContainer({ children, className }: ClassNameProps) {
  return <section className={joinClasses("page-container", className)}>{children}</section>;
}

type PageTitleProps = {
  title: string;
  description?: string;
  actions?: ReactNode;
};

export function PageTitle({ title, description, actions }: PageTitleProps) {
  return (
    <div className="page-title-row">
      <div>
        <h2 className="page-title">{title}</h2>
        {description ? <p className="page-description">{description}</p> : null}
      </div>
      {actions ? <div className="page-title-actions">{actions}</div> : null}
    </div>
  );
}

type SectionTitleProps = {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
};

export function SectionTitle({ title, subtitle, actions }: SectionTitleProps) {
  return (
    <div className="section-title-row">
      <div>
        <h3 className="section-title">{title}</h3>
        {subtitle ? <p className="section-subtitle">{subtitle}</p> : null}
      </div>
      {actions ? <div>{actions}</div> : null}
    </div>
  );
}

export function Card({ children, className }: ClassNameProps) {
  return <div className={joinClasses("card", className)}>{children}</div>;
}

type AlertMessageProps = {
  kind?: "error" | "success" | "info";
  children: ReactNode;
};

export function AlertMessage({ kind = "info", children }: AlertMessageProps) {
  return <p className={`alert alert-${kind}`}>{children}</p>;
}

type StatusBadgeProps = {
  status: string | null | undefined;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = (status || "UNKNOWN").toUpperCase();
  const className = `status-badge status-${normalized.toLowerCase()}`;
  return <span className={className}>{normalized}</span>;
}

type MetricCardProps = {
  label: string;
  value: string | number;
  tone?: "neutral" | "accent";
};

export function MetricCard({ label, value, tone = "neutral" }: MetricCardProps) {
  return (
    <div className={`metric-card metric-${tone}`}>
      <span className="metric-label">{label}</span>
      <strong className="metric-value">{value}</strong>
    </div>
  );
}
