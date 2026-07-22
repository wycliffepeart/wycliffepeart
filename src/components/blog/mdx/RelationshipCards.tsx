import type { ReactNode } from "react";

export function RelationshipCards({ children }: { children: ReactNode }) {
  return <div className="relationship-cards">{children}</div>;
}

export function RelationshipCard({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <details className="relationship-card">
      <summary className="relationship-card-trigger">
        <span>
          <span className="relationship-card-title">{title}</span>
          <span className="relationship-card-description">{description}</span>
        </span>
      </summary>
      <div className="relationship-detail">{children}</div>
    </details>
  );
}
