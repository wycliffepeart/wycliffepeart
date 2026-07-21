export default function BlogPreviewSection() {
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
        <article className="blog-post">
          <div>
            <p className="blog-meta">Sample post</p>
            <h3>Building AI Features That Survive Production</h3>
            <p>
              A practical note on treating LLM integrations like product systems: clear boundaries, measurable
              behavior, fallback paths, and observability from the start.
            </p>
          </div>

          <a className="button" href="/blog/">
            Read Blog
          </a>
        </article>
      </div>
    </section>
  );
}
