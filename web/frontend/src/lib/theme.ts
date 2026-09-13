// Theme is one of: "light" | "dark" | "system". Persisted per-browser.
export type Theme = "light" | "dark" | "system";
const KEY = "tju-theme";

export function getTheme(): Theme {
  try {
    return (localStorage.getItem(KEY) as Theme) || "system";
  } catch {
    return "system";
  }
}

export function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  if (theme === "system") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", theme);
}

export function setTheme(theme: Theme): void {
  try {
    localStorage.setItem(KEY, theme);
  } catch {
    /* ignore */
  }
  applyTheme(theme);
}

export function initTheme(): void {
  applyTheme(getTheme());
}
