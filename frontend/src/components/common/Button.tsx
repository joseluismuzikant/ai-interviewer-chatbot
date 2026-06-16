import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  loading?: boolean;
  loadingText?: string;
  children: ReactNode;
};

export function Button({ loading, loadingText, disabled, children, ...rest }: ButtonProps) {
  return (
    <button type="button" disabled={disabled || loading} {...rest}>
      {loading ? loadingText || "Loading..." : children}
    </button>
  );
}
