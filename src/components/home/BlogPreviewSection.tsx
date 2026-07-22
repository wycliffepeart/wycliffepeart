import { formatPostDate, getAllPosts } from "@/lib/blog";

export default function BlogPreviewSection() {
  const [latestPost] = getAllPosts();

  return (
    <section className="section" id="blog">
      <div className="section-heading">
        <h2>Blog</h2>
        <p>
          Short notes on practical software engineering, AI application development, and the delivery systems that
          help teams ship with confidence.
        </p>
      </div>

      <div className="blog-list">
        {latestPost ? (
          <article className="blog-post">
            <div>
              <p className="blog-meta">{formatPostDate(latestPost.date)}</p>
              <h3>{latestPost.title}</h3>
              <p>{latestPost.excerpt}</p>
            </div>

            {/* Plain <a> tags intentionally used site-wide instead of next/link: this
                static export serves each page as an independent HTML document (no
                RSC prefetch payloads are deployed), matching the original site's
                hard-navigation behavior. */}
            <a className="button" href={`/blog/${latestPost.slug}/`}>
              Read Post
            </a>
          </article>
        ) : null}
      </div>
    </section>
  );
}
