import type { ReactNode } from "react";

type Props = { children: ReactNode; className?: string };

function joinClasses(...classNames: Array<string | undefined>): string {
  return classNames.filter(Boolean).join(" ");
}

export function PageContainer({ children, className }: Props) {
  return <section className={joinClasses("page-container", className)}>{children}</section>;
}
