export type Theme = "light" | "dark";

export const THEME_STORAGE_KEY = "theme";

export function getStoredTheme(): Theme | null {
  try {
    return window.localStorage?.getItem(THEME_STORAGE_KEY) === "dark" ? "dark" : null;
  } catch {
    return null;
  }
}

export function getCurrentTheme(): Theme {
  return document.documentElement.dataset.theme === "dark" ? "dark" : "light";
}

export function applyTheme(theme: Theme): void {
  if (theme === "dark") {
    document.documentElement.dataset.theme = "dark";
  } else {
    document.documentElement.removeAttribute("data-theme");
  }

  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    // The visible theme still changes if storage is unavailable.
  }
}

// Ported verbatim from the original inline <head> script (app/index.html) so
// the theme is applied before first paint, avoiding a flash of the wrong
// theme. This must stay a raw script tag in the root layout's <head> -
// React can't run before its own hydration.
export const NO_FLASH_THEME_SCRIPT = `(() => {
  let savedTheme = null;

  try {
    savedTheme = window.localStorage?.getItem("theme");
  } catch {
    savedTheme = null;
  }

  if (savedTheme === "dark") {
    document.documentElement.dataset.theme = "dark";
  }
})();`;
