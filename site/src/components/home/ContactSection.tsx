export default function ContactSection() {
  return (
    <section className="section" id="contact">
      <div className="contact">
        <div>
          <p className="eyebrow">Connect</p>
          <h2>Let us talk about the next useful thing to build.</h2>
          <p>
            I am open to conversations around full-stack engineering, backend architecture, AI application
            development, DevOps workflows, and maintainable product delivery.
          </p>
        </div>

        <div className="actions">
          <a className="button primary" href="mailto:wycliffepeart@gmail.com">
            Email Me
          </a>
          <a className="button" href="https://www.linkedin.com/in/wycliffepeart/" target="_blank" rel="noopener noreferrer">
            LinkedIn
          </a>
        </div>
      </div>
    </section>
  );
}
