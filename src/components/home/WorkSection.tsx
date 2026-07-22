export default function WorkSection() {
  return (
    <section className="section" id="work">
      <div className="section-heading">
        <h2>What I Build</h2>
        <p>
          I work across the full delivery path: understanding requirements, shaping architecture, writing
          maintainable code, and helping teams ship with confidence.
        </p>
      </div>

      <div className="grid">
        <article className="card">
          <h3>Backend Platforms</h3>
          <p>
            Secure APIs, distributed services, integrations, event-driven systems, and cloud-native foundations that
            are built to evolve.
          </p>
        </article>

        <article className="card">
          <h3>Web Applications</h3>
          <p>
            Responsive frontend experiences using modern JavaScript frameworks, clean interaction patterns, and
            practical component systems.
          </p>
        </article>

        <article className="card">
          <h3>AI Features</h3>
          <p>
            LLM API integrations, prompt workflows, structured outputs, function calling, retrieval patterns, and
            agent-style application behavior.
          </p>
        </article>
      </div>
    </section>
  );
}
