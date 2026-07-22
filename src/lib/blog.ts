import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";

const BLOG_DIR = path.join(process.cwd(), "content", "blog");

export type BlogPostMeta = {
  slug: string;
  title: string;
  date: string;
  excerpt: string;
  tags: string[];
  eyebrow?: string;
  subtitle?: string;
  byline?: string[];
};

export type BlogPost = BlogPostMeta & { content: string };

function readPostFile(fileName: string): BlogPost {
  const filePath = path.join(BLOG_DIR, fileName);
  const raw = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(raw);
  const slug = typeof data.slug === "string" ? data.slug : fileName.replace(/\.mdx$/, "");

  return {
    slug,
    title: data.title as string,
    date: data.date as string,
    excerpt: data.excerpt as string,
    tags: Array.isArray(data.tags) ? (data.tags as string[]) : [],
    eyebrow: typeof data.eyebrow === "string" ? data.eyebrow : undefined,
    subtitle: typeof data.subtitle === "string" ? data.subtitle : undefined,
    byline: Array.isArray(data.byline) ? (data.byline as string[]) : undefined,
    content,
  };
}

export function getAllPosts(): BlogPost[] {
  const fileNames = fs.existsSync(BLOG_DIR) ? fs.readdirSync(BLOG_DIR) : [];

  return fileNames
    .filter((name) => name.endsWith(".mdx"))
    .map(readPostFile)
    .sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getPostBySlug(slug: string): BlogPost | undefined {
  return getAllPosts().find((post) => post.slug === slug);
}

export function formatPostDate(date: string): string {
  return new Date(`${date}T00:00:00Z`).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  });
}
