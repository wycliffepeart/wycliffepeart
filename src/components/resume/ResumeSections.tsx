import {
  COMPETENCIES,
  EDUCATION,
  EXPERIENCE,
  PROFESSIONAL_DEVELOPMENT,
  SUMMARY,
} from "@/lib/resume-data";

export function SummarySection() {
  return (
    <section className="section">
      <h2 className="section-title">Professional Summary</h2>
      {SUMMARY.map((paragraph) => (
        <p key={paragraph.slice(0, 24)}>{paragraph}</p>
      ))}
    </section>
  );
}

export function CompetenciesSection() {
  return (
    <section className="section">
      <h2 className="section-title">Core Competencies</h2>

      <table className="competency-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Technologies</th>
          </tr>
        </thead>

        <tbody>
          {COMPETENCIES.map((competency) => (
            <tr key={competency.category}>
              <td>{competency.category}</td>
              <td>{competency.items}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export function ExperienceSection() {
  return (
    <section className="section">
      <h2 className="section-title">Professional Experience</h2>

      {EXPERIENCE.map((entry) => (
        <article className="experience-item" key={entry.company + entry.dates}>
          <div className="experience-header">
            <div>
              <h3 className="company-name">{entry.company}</h3>
              <p className="role-title">{entry.role}</p>
            </div>

            <div className="experience-dates">{entry.dates}</div>
          </div>

          <p className="technology-line">
            <span className="technology-label">Technologies:</span> {entry.technologies}
          </p>

          <ul>
            {entry.bullets.map((bullet) => (
              <li key={bullet.slice(0, 32)}>{bullet}</li>
            ))}
          </ul>
        </article>
      ))}
    </section>
  );
}

export function EducationSection() {
  return (
    <section className="section">
      <h2 className="section-title">Education</h2>

      <div className="education-item">
        <div className="experience-header">
          <h3>{EDUCATION.school}</h3>
          <div className="experience-dates">{EDUCATION.dateLabel}</div>
        </div>

        <p>
          {EDUCATION.degreeLabel}
          <em> — {EDUCATION.status}</em>
        </p>
      </div>
    </section>
  );
}

export function ProfessionalDevelopmentSection() {
  return (
    <section className="section">
      <h2 className="section-title">Professional Development</h2>
      <p>{PROFESSIONAL_DEVELOPMENT}</p>
    </section>
  );
}
