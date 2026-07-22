import type { ReactElement, ReactNode } from "react";

const TOKEN_PATTERN =
  /('[^']*')|\b(\d+)\b|\b(SELECT|FROM|WHERE|JOIN|INNER|LEFT|RIGHT|FULL|OUTER|CROSS|ON|AS|AND|OR|NOT|EXISTS|NULL|IS|GROUP|BY|ORDER|UNION|BETWEEN|COUNT|SUM|AVG|MIN|MAX|IN|USING)\b/g;

function highlightSql(code: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  let lastIndex = 0;
  let key = 0;

  for (const match of code.matchAll(TOKEN_PATTERN)) {
    const [full, stringToken, numberToken, keywordToken] = match;
    const index = match.index ?? 0;

    if (index > lastIndex) {
      nodes.push(code.slice(lastIndex, index));
    }

    if (stringToken) {
      nodes.push(
        <span className="sql-string" key={key++}>
          {stringToken}
        </span>,
      );
    } else if (numberToken) {
      nodes.push(
        <span className="sql-number" key={key++}>
          {numberToken}
        </span>,
      );
    } else if (keywordToken) {
      nodes.push(
        <span className="sql-keyword" key={key++}>
          {keywordToken}
        </span>,
      );
    }

    lastIndex = index + full.length;
  }

  if (lastIndex < code.length) {
    nodes.push(code.slice(lastIndex));
  }

  return nodes;
}

function getCodeText(node: ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(getCodeText).join("");
  if (node && typeof node === "object" && "props" in node) {
    return getCodeText((node as ReactElement<{ children?: ReactNode }>).props.children);
  }
  return "";
}

export function CodeBlock(props: { children?: ReactNode }) {
  const codeElement = props.children as
    | ReactElement<{ className?: string; children?: ReactNode }>
    | undefined;
  const className = codeElement?.props?.className ?? "";

  if (!className.includes("language-sql")) {
    return <pre>{props.children}</pre>;
  }

  const raw = getCodeText(codeElement?.props?.children).replace(/\n$/, "");

  return (
    <pre>
      <code className={className}>{highlightSql(raw)}</code>
    </pre>
  );
}
