import type { ReactNode } from "react";

export function Cards({ children }: { children: ReactNode }) {
  return <div className="cards">{children}</div>;
}

export function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="card">
      <strong>{title}</strong>
      <span>{children}</span>
    </div>
  );
}
