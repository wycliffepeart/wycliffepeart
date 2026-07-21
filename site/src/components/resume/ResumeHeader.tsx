import { CONTACT, NAME, PROFESSIONAL_TITLE } from "@/lib/resume-data";

export default function ResumeHeader() {
  return (
    <header className="resume-header">
      <h1 className="name">{NAME}</h1>

      <p className="professional-title">{PROFESSIONAL_TITLE}</p>

      <div className="contact-details">
        <span className="contact-item">
          <strong>Email:</strong> <a href={`mailto:${CONTACT.email}`}>{CONTACT.email}</a>
        </span>

        <span className="contact-item">
          <strong>Phone:</strong> <a href={CONTACT.phoneHref}>{CONTACT.phoneDisplay}</a>
        </span>

        <span className="contact-item">
          <strong>Location:</strong> {CONTACT.location}
        </span>

        <span className="contact-item">
          <strong>GitHub:</strong>{" "}
          <a href={CONTACT.githubUrl} target="_blank" rel="noopener noreferrer">
            {CONTACT.githubDisplay}
          </a>
        </span>

        <span className="contact-item">
          <strong>LinkedIn:</strong>{" "}
          <a href={CONTACT.linkedinUrl} target="_blank" rel="noopener noreferrer">
            {CONTACT.linkedinDisplay}
          </a>
        </span>
      </div>
    </header>
  );
}
