import type { ReactNode } from "react";

type Props = {
  title: string;
  description?: string;
  actions?: ReactNode;
};

export function PageTitle({ title, description, actions }: Props) {
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
