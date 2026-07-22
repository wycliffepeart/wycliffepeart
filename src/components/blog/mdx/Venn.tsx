import type { ReactNode } from "react";

type Shade = "inner" | "left" | "right" | "full";

export function Venn({ shade, labels }: { shade: Shade; labels: [string, string] }) {
  return (
    <figure className="venn-card" aria-label={`${shade} join Venn diagram`}>
      <div className={`venn shade-${shade}`}>
        <span className="circle left" />
        <span className="circle right" />
      </div>
      <figcaption className="venn-labels">
        <span>{labels[0]}</span>
        <span>{labels[1]}</span>
      </figcaption>
    </figure>
  );
}

export function DiagramAndCopy({ children }: { children: ReactNode }) {
  return <div className="diagram-and-copy">{children}</div>;
}
