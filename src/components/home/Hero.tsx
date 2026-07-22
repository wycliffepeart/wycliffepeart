import Image from "next/image";
import ResumeOpenButton from "./ResumeOpenButton";

export default function Hero() {
  return (
    <section className="hero" aria-labelledby="intro-title">
      <aside className="intro-card" aria-label="Wycliffe Otaniel Peart introduction">
        <Image
          className="intro-portrait"
          src="/assets/head-shot.jpeg"
          alt="Wycliffe Otaniel Peart"
          width={420}
          height={525}
        />

        <div className="intro-card-body">
          <h2 className="intro-name">Wycliffe Otaniel Peart</h2>
          <p className="intro-role">Building intelligent software systems where AI meets modern engineering.</p>

          <div className="actions intro-actions" aria-label="Profile links">
            <ResumeOpenButton />
            <a className="button" href="https://www.linkedin.com/in/wycliffepeart/" target="_blank" rel="noopener noreferrer">
              LinkedIn
            </a>
            <a className="button" href="https://github.com/wycliffepeart" target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
          </div>

          <div className="intro-principles" aria-label="Mission and vision">
            <div className="intro-principle">
              <span className="intro-principle-label">Mission</span>
              <p>Help organizations build secure, scalable, AI-powered software that creates measurable business value.</p>
            </div>

            <div className="intro-principle">
              <span className="intro-principle-label">Vision</span>
              <p>Shape the next generation of intelligent software where AI becomes a core capability rather than an add-on.</p>
            </div>
          </div>
        </div>
      </aside>

      <div className="hero-intro">
        <p className="eyebrow">Available for engineering consultations</p>
        <h1 id="intro-title">Designing and delivering production software across web, cloud, and AI.</h1>
        <p className="hero-copy">
          I help organizations design, build, and modernize production software across web applications, backend
          platforms, cloud infrastructure, and AI-enabled workflows.
        </p>
        <p className="intro-lead">
          My work brings technical clarity to complex initiatives: aligning product goals, shaping scalable
          architecture, delivering dependable code, and improving the systems teams rely on to ship with confidence.
        </p>

        <div className="intro-outcomes" aria-label="What I provide to organizations">
          <div className="intro-outcome">
            <strong>Product Engineering</strong>
            Full-stack applications, APIs, integrations, and user-facing features built for business-critical workflows.
          </div>

          <div className="intro-outcome">
            <strong>Architecture</strong>
            Scalable backend foundations, clean service boundaries, cloud infrastructure, and delivery practices that
            support growth.
          </div>

          <div className="intro-outcome">
            <strong>AI Capability</strong>
            Practical LLM integrations, automation, structured workflows, and AI features aligned with organizational
            goals.
          </div>
        </div>
      </div>
    </section>
  );
}
