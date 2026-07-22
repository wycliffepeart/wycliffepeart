"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

type ResumeModalContextValue = {
  isOpen: boolean;
  open: () => void;
  close: () => void;
};

const ResumeModalContext = createContext<ResumeModalContextValue | null>(null);

function isResumeParamOpen(): boolean {
  return new URLSearchParams(window.location.search).get("resume") === "true";
}

function updateResumeParam(shouldOpen: boolean): void {
  const url = new URL(window.location.href);

  if (shouldOpen) {
    url.searchParams.set("resume", "true");
  } else {
    url.searchParams.delete("resume");
  }

  const nextUrl = `${url.pathname}${url.search}${url.hash}`;
  const currentUrl = `${window.location.pathname}${window.location.search}${window.location.hash}`;

  if (nextUrl !== currentUrl) {
    window.history.pushState(null, "", nextUrl);
  }
}

export function ResumeModalProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);

  const sync = useCallback(() => {
    setIsOpen(isResumeParamOpen());
  }, []);

  const open = useCallback(() => {
    updateResumeParam(true);
    sync();
  }, [sync]);

  const close = useCallback(() => {
    updateResumeParam(false);
    sync();
  }, [sync]);

  useEffect(() => {
    // window.location.search doesn't exist during the server/static render,
    // so the initial `?resume=true` check can only happen after mount.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    sync();
    window.addEventListener("popstate", sync);
    return () => window.removeEventListener("popstate", sync);
  }, [sync]);

  useEffect(() => {
    document.body.classList.toggle("modal-open", isOpen);
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handleKeydown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        close();
      }
    };

    document.addEventListener("keydown", handleKeydown);
    return () => document.removeEventListener("keydown", handleKeydown);
  }, [isOpen, close]);

  return <ResumeModalContext.Provider value={{ isOpen, open, close }}>{children}</ResumeModalContext.Provider>;
}

export function useResumeModal(): ResumeModalContextValue {
  const context = useContext(ResumeModalContext);

  if (!context) {
    throw new Error("useResumeModal must be used within a ResumeModalProvider");
  }

  return context;
}
