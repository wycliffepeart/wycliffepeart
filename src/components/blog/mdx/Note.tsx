import type { ReactNode } from "react";

type NoteVariant = "default" | "amber" | "red" | "green" | "purple";

export function Note({
  variant = "default",
  children,
}: {
  variant?: NoteVariant;
  children: ReactNode;
}) {
  const className = variant === "default" ? "note" : `note ${variant}`;
  return <div className={className}>{children}</div>;
}
