const SKILLS = [
  "Node.js",
  "TypeScript",
  "Java",
  "Spring Boot",
  "NestJS",
  "React",
  "Next.js",
  "Angular",
  "React Native",
  "Flutter",
  "AWS",
  "Google Cloud",
  "Kubernetes",
  "Docker",
  "Terraform",
  "PostgreSQL",
  "MongoDB",
  "Redis",
  "Jest",
  "Playwright",
  "GitHub Actions",
  "LLM APIs",
  "RAG",
  "AI Agents",
];

export default function StackSection() {
  return (
    <section className="section" id="stack">
      <div className="section-heading">
        <h2>Technology Stack</h2>
        <p>A practical stack for building, testing, deploying, and improving modern software products.</p>
      </div>

      <ul className="skills" aria-label="Technology skills">
        {SKILLS.map((skill) => (
          <li key={skill}>{skill}</li>
        ))}
      </ul>
    </section>
  );
}
