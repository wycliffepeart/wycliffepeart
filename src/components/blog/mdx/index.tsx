import type { MDXComponents } from "mdx/types";
import { Card, Cards } from "./Cards";
import { CodeBlock } from "./CodeBlock";
import { DataTable, TableGrid } from "./DataTable";
import { ExampleResult, SampleData } from "./ExampleResult";
import { Formula } from "./Formula";
import { Note } from "./Note";
import { Path } from "./Path";
import { ReferenceTable } from "./ReferenceTable";
import { RelationshipCard, RelationshipCards } from "./RelationshipCards";
import { DiagramAndCopy, Venn } from "./Venn";

export const mdxComponents: MDXComponents = {
  pre: CodeBlock,
  Note,
  Cards,
  Card,
  DataTable,
  TableGrid,
  ExampleResult,
  SampleData,
  Venn,
  DiagramAndCopy,
  Formula,
  Path,
  ReferenceTable,
  RelationshipCards,
  RelationshipCard,
};
