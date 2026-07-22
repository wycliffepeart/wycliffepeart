import { Children, type ReactNode } from "react";

export function ExampleResult({
  title = "Result data",
  caption,
  children,
}: {
  title?: string;
  caption?: ReactNode;
  children: ReactNode;
}) {
  const isSingle = Children.count(children) < 2;

  return (
    <div className="example-result">
      <h4>{title}</h4>
      <div className={`example-result-grid${isSingle ? " result-only" : ""}`}>{children}</div>
      {caption && <p className="caption">{caption}</p>}
    </div>
  );
}

export function SampleData({ summary, children }: { summary: string; children: ReactNode }) {
  return (
    <details className="sample-data-accordion">
      <summary>
        <span>Sample data</span>
        <span className="sample-data-summary">{summary}</span>
      </summary>
      <div className="sample-data-grid">{children}</div>
    </details>
  );
}
