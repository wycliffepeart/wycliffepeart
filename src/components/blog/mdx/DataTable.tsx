import type { ReactNode } from "react";

type Cell = string | number;

export function DataTable({ headers, rows }: { headers: string[]; rows: Cell[][] }) {
  return (
    <div className="data-table">
      <table>
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function TableGrid({ children, columns = 2 }: { children: ReactNode; columns?: 2 | 3 }) {
  return <div className={`data-grid data-grid-${columns}`}>{children}</div>;
}
