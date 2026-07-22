import GithubSlugger from "github-slugger";

export type TocItem = {
  id: string;
  text: string;
  depth: number;
};

export function extractHeadings(markdown: string): TocItem[] {
  const slugger = new GithubSlugger();
  const headings: TocItem[] = [];
  let inCodeFence = false;

  for (const line of markdown.split("\n")) {
    if (/^```/.test(line.trim())) {
      inCodeFence = !inCodeFence;
      continue;
    }
    if (inCodeFence) continue;

    const match = /^(#{2,3})\s+(.+)$/.exec(line);
    if (!match) continue;

    const depth = match[1].length;
    const text = match[2].replace(/[`*_]/g, "").trim();
    const id = slugger.slug(text);
    headings.push({ id, text, depth });
  }

  return headings;
}
