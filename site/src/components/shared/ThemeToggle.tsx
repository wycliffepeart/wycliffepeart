"use client";

import { useEffect, useState } from "react";
import { applyTheme, getCurrentTheme, type Theme } from "@/lib/theme";

export default function ThemeToggle() {
  const [theme, setThemeState] = useState<Theme>("light");

  useEffect(() => {
    // Reads document.documentElement's theme attribute, which the no-FOUC
    // inline script (see src/lib/theme.ts) sets before hydration. This value
    // doesn't exist during the server/static render, so it can only be read
    // here, after mount.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setThemeState(getCurrentTheme());
  }, []);

  const isDark = theme === "dark";

  const toggleTheme = () => {
    const nextTheme: Theme = isDark ? "light" : "dark";
    applyTheme(nextTheme);
    setThemeState(nextTheme);
  };

  return (
    <button
      className="theme-toggle"
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${isDark ? "light" : "dark"} theme`}
      aria-pressed={isDark}
    >
      <span className="theme-toggle-icon" aria-hidden="true" />
      <span>{isDark ? "Light" : "Dark"}</span>
    </button>
  );
}
