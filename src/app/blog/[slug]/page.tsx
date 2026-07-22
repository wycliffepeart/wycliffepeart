import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { MDXRemote } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";
import rehypeSlug from "rehype-slug";
import "@/styles/blog.css";
import SiteFooter from "@/components/shared/SiteFooter";
import TableOfContents from "@/components/blog/TableOfContents";
import { mdxComponents } from "@/components/blog/mdx";
import { formatPostDate, getAllPosts, getPostBySlug } from "@/lib/blog";
import { extractHeadings } from "@/lib/toc";

export const dynamicParams = false;

export function generateStaticParams() {
  return getAllPosts().map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const post = getPostBySlug(slug);

  if (!post) {
    return {};
  }

  return {
    title: `${post.title} | Wycliffe Otaniel Peart`,
    description: post.excerpt,
    authors: [{ name: "Wycliffe Otaniel Peart" }],
    robots: "index, follow",
    alternates: {
      canonical: `https://www.wycliffepeart.com/blog/${post.slug}/`,
    },
  };
}

export default async function BlogPostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = getPostBySlug(slug);

  if (!post) {
    notFound();
  }

  const headings = extractHeadings(post.content);

  return (
    <div className="page">
      <nav className="nav" aria-label="Blog navigation">
        {/* Plain <a> tags intentionally used site-wide instead of next/link: this
            static export serves each page as an independent HTML document (no
            RSC prefetch payloads are deployed), matching the original site's
            hard-navigation behavior. */}
        {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
        <a className="brand" href="/" aria-label="Wycliffe Otaniel Peart profile home">
          <span className="brand-mark">WP</span>
          <span>Wycliffe Otaniel Peart</span>
        </a>

        {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
        <a className="nav-link" href="/blog/">
          Back to Blog
        </a>
      </nav>

      <main className="post-layout">
        <article className="post">
          <header className="post-header">
            {post.eyebrow && <p className="eyebrow">{post.eyebrow}</p>}
            <h2>{post.title}</h2>
            {post.subtitle && <p className="post-subtitle">{post.subtitle}</p>}
            <div className="post-byline">
              <span>{formatPostDate(post.date)}</span>
              {post.byline?.map((item) => <span key={item}>{item}</span>)}
              {post.tags.length > 0 && <span>{post.tags.join(", ")}</span>}
            </div>
          </header>

          <div className="post-hero-rule" />

          <div className="post-body">
            <MDXRemote
              source={post.content}
              components={mdxComponents}
              options={{
                mdxOptions: { remarkPlugins: [remarkGfm], rehypePlugins: [rehypeSlug] },
              }}
            />
          </div>
        </article>

        {headings.length > 0 && (
          <aside className="post-toc-wrap">
            <TableOfContents items={headings} />
          </aside>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
