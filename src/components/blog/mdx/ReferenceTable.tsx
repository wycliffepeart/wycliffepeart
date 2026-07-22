import type { ReactNode } from "react";

export function ReferenceTable({ children }: { children: ReactNode }) {
  return (
    <table className="reference-table">
      <thead>
        <tr>
          <th>Need</th>
          <th>Use</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>{children}</tbody>
    </table>
  );
}
