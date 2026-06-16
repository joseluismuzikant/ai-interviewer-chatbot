import type { ReactNode } from "react";

type CardProps = {
  children: ReactNode;
  className?: string;
};

function joinClasses(...classNames: Array<string | undefined>): string {
  return classNames.filter(Boolean).join(" ");
}

export function Card({ children, className }: CardProps) {
  return <div className={joinClasses("card", className)}>{children}</div>;
}
