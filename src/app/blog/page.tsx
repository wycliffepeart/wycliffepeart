import type { Metadata } from "next";
import "@/styles/blog.css";
import SiteFooter from "@/components/shared/SiteFooter";
import { formatPostDate, getAllPosts } from "@/lib/blog";

export const metadata: Metadata = {
  title: "Blog | Wycliffe Otaniel Peart",
  description:
    "Blog posts by Wycliffe Otaniel Peart on practical software engineering, AI application development, cloud delivery, and production systems.",
  authors: [{ name: "Wycliffe Otaniel Peart" }],
  robots: "index, follow",
  alternates: {
    canonical: "https://www.wycliffepeart.com/blog/",
  },
};

export default function BlogPage() {
  const posts = getAllPosts();

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
        <a className="nav-link" href="/#blog">
          Back to Profile
        </a>
      </nav>

      <main>
        <header className="hero">
          <p className="eyebrow">Blog</p>
          <h1>Notes on practical software engineering and AI systems.</h1>
          <p className="hero-copy">
            Short posts on building useful software, applying AI responsibly, and keeping production systems
            maintainable.
          </p>
        </header>

        <div className="post-list">
          {posts.map((post) => (
            <article key={post.slug} className="post post-preview">
              <a className="post-link" href={`${post.slug}/`}>
                <p className="post-meta">{formatPostDate(post.date)}</p>
                <h2>{post.title}</h2>
              </a>
              <p>{post.excerpt}</p>
              {post.tags.length > 0 && (
                <div className="post-tags">
                  {post.tags.map((tag) => (
                    <span key={tag} className="post-tag">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </article>
          ))}

          {posts.length === 0 && (
            <article className="post">
              <p>No posts yet. Check back soon.</p>
            </article>
          )}
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
