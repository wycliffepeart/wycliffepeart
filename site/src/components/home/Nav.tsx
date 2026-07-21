"use client";

import { useState } from "react";
import ThemeToggle from "@/components/shared/ThemeToggle";

export default function Nav() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="site-header">
      <nav className="nav" aria-label="Primary navigation">
        <div className="nav-top">
          <a className="brand" href="#top" aria-label="Wycliffe Otaniel Peart profile home">
            <span className="brand-mark">WP</span>
            <span>Wycliffe Otaniel Peart</span>
          </a>

          <button
            className="menu-toggle"
            type="button"
            aria-expanded={isOpen}
            aria-controls="primary-menu"
            aria-label={isOpen ? "Close navigation menu" : "Open navigation menu"}
            onClick={() => setIsOpen((open) => !open)}
          >
            <span className="menu-icon" aria-hidden="true" />
          </button>
        </div>

        <div
          className={`nav-links${isOpen ? " is-open" : ""}`}
          id="primary-menu"
          onClick={(event) => {
            if ((event.target as HTMLElement).matches("a")) {
              setIsOpen(false);
            }
          }}
        >
          <a href="#work">Work</a>
          <a href="#stack">Stack</a>
          <a href="#focus">Focus</a>
          <a href="#blog">Blog</a>
          <a href="#contact">Contact</a>
          <ThemeToggle />
        </div>
      </nav>
    </header>
  );
}
