const FOCUS_ITEMS = [
  {
    number: "01",
    title: "Production AI Features",
    detail: "LLM APIs, structured outputs, function calling, agents, and RAG patterns designed for real product behavior.",
  },
  {
    number: "02",
    title: "Backend Architecture",
    detail: "Secure APIs, clean service boundaries, reliable integrations, and scalable cloud infrastructure.",
  },
  {
    number: "03",
    title: "Developer Workflows",
    detail: "AI-assisted code review, test generation, documentation, CI/CD improvements, and release automation.",
  },
  {
    number: "04",
    title: "System Quality",
    detail: "Maintainability, observability, security, and architecture decisions that support long-term business use.",
  },
];

export default function FocusSection() {
  return (
    <section className="section" id="focus">
      <div className="section-heading">
        <h2>Current Focus</h2>
        <p>
          I am focused on building software systems that combine strong engineering fundamentals with practical AI
          capabilities and reliable delivery.
        </p>
      </div>

      <div className="focus-board">
        <article className="focus-primary">
          <div>
            <p className="focus-kicker">Engineering Direction</p>
            <h3>Practical AI, clean architecture, and delivery systems that hold up in production.</h3>
          </div>

          <p>
            My current work sits at the intersection of full-stack product engineering, cloud-native backend design,
            and AI-supported development workflows.
          </p>
        </article>

        <div className="focus-items" aria-label="Current focus areas">
          {FOCUS_ITEMS.map((item) => (
            <article className="focus-item" key={item.number}>
              <span className="focus-number">{item.number}</span>
              <h3>{item.title}</h3>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
