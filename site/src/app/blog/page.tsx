import type { Metadata } from "next";
import "@/styles/blog.css";
import SiteFooter from "@/components/shared/SiteFooter";

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

        <article className="post">
          <p className="post-meta">Sample post | July 17, 2026</p>
          <h2>Building AI Features That Survive Production</h2>
          <p>
            AI features become valuable when they are treated as part of the product system, not as a thin layer
            around a prompt. The useful work starts with clear user intent, explicit boundaries, stable input and
            output contracts, and a plan for what should happen when the model is uncertain or unavailable.
          </p>
          <p>
            I like to design these features around measurable behavior. That means structured outputs where
            possible, narrow tools for external actions, test cases based on realistic examples, and enough logging
            to understand decisions without exposing sensitive data. The goal is not to make the model seem magical.
            The goal is to make the system dependable.
          </p>
          <p>
            A production-ready AI workflow should have fallback paths, human review where risk is high, and
            monitoring that shows whether the feature is actually helping users. When those basics are in place,
            LLMs can become a practical capability inside the software instead of a fragile demo.
          </p>
        </article>
      </main>

      <SiteFooter />
    </div>
  );
}
