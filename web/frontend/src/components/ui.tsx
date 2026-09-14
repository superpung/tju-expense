import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from "react";
import { getTheme, setTheme, type Theme } from "../lib/theme";
import { useEffect, useState } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "primary" | "ghost";
  loading?: boolean;
};

export function Button({ variant = "default", loading, children, className = "", disabled, ...rest }: ButtonProps) {
  const cls = `btn ${variant === "primary" ? "btn-primary" : variant === "ghost" ? "btn-ghost" : ""} ${className}`;
  return (
    <button className={cls} disabled={disabled || loading} {...rest}>
      {loading && <span className="spinner" />}
      {children}
    </button>
  );
}

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input className="input" {...props} />;
}

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="field">
      <span className="label">{label}</span>
      {children}
    </label>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`card ${className}`}>{children}</div>;
}

export function Spinner() {
  return <span className="spinner" />;
}

const ICONS: Record<Theme, string> = { light: "☀", dark: "☾", system: "◑" };
const NEXT: Record<Theme, Theme> = { light: "dark", dark: "system", system: "light" };

export function ThemeToggle() {
  const [theme, setThemeState] = useState<Theme>(getTheme());
  useEffect(() => setTheme(theme), [theme]);
  return (
    <button
      className="btn btn-icon btn-ghost"
      title={`主题：${theme}`}
      aria-label="切换主题"
      onClick={() => setThemeState((t) => NEXT[t])}
    >
      {ICONS[theme]}
    </button>
  );
}
