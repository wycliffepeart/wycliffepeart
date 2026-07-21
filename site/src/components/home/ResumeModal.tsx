"use client";

import { useEffect, useRef } from "react";
import { useResumeModal } from "./resume-modal-context";
import {
  COMPETENCIES,
  CONTACT,
  EDUCATION,
  EXPERIENCE,
  HIGHLIGHTS,
  NAME,
  PROFESSIONAL_DEVELOPMENT,
  PROFESSIONAL_TITLE,
  SUMMARY,
} from "@/lib/resume-data";

export default function ResumeModal() {
  const { isOpen, close } = useResumeModal();
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      closeButtonRef.current?.focus();
    }
  }, [isOpen]);

  return (
    <div
      className={`resume-modal${isOpen ? " is-open" : ""}`}
      id="resume-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="resume-modal-title"
    >
      <div className="resume-dialog">
        <header className="resume-modal-header">
          <div className="resume-modal-heading">
            <h2 className="resume-modal-title" id="resume-modal-title">
              Resume
            </h2>
            <p className="resume-modal-subtitle">{NAME} | Senior Full-Stack AI Engineer</p>
          </div>

          <div className="resume-modal-controls">
            <a
              className="resume-header-download"
              href="/resume.pdf"
              target="_blank"
              rel="noopener noreferrer"
              download="Wycliffe-Peart-Resume.pdf"
              aria-label="Download resume PDF"
            >
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M12 3v12" />
                <path d="m7 10 5 5 5-5" />
                <path d="M5 21h14" />
              </svg>
            </a>
            <button
              ref={closeButtonRef}
              className="modal-close"
              type="button"
              onClick={close}
              aria-label="Close resume modal"
            >
              ×
            </button>
          </div>
        </header>

        <div className="resume-modal-content">
          <div className="resume-sheet">
            <section className="resume-intro">
              <h3>{NAME}</h3>
              <p className="resume-title">{PROFESSIONAL_TITLE}</p>

              <div className="resume-contact">
                <span>
                  <strong>Email:</strong> <a href={`mailto:${CONTACT.email}`}>{CONTACT.email}</a>
                </span>
                <span>
                  <strong>Phone:</strong> <a href={CONTACT.phoneHref}>{CONTACT.phoneDisplay}</a>
                </span>
                <span>
                  <strong>Location:</strong> {CONTACT.location}
                </span>
                <span>
                  <strong>GitHub:</strong>{" "}
                  <a href={CONTACT.githubUrl} target="_blank" rel="noopener noreferrer">
                    {CONTACT.githubDisplay}
                  </a>
                </span>
                <span>
                  <strong>LinkedIn:</strong>{" "}
                  <a href={CONTACT.linkedinUrl} target="_blank" rel="noopener noreferrer">
                    {CONTACT.linkedinDisplay}
                  </a>
                </span>
              </div>

              <div className="resume-highlights" aria-label="Resume highlights">
                {HIGHLIGHTS.map((highlight) => (
                  <div className="resume-highlight" key={highlight.stat}>
                    <strong>{highlight.stat}</strong>
                    <span>{highlight.detail}</span>
                  </div>
                ))}
              </div>

              <div className="resume-actions" aria-label="Resume contact actions">
                <a
                  className="resume-action primary"
                  href="/resume.pdf"
                  target="_blank"
                  rel="noopener noreferrer"
                  download="Wycliffe-Peart-Resume.pdf"
                >
                  Download PDF
                </a>
                <a className="resume-action" href="resume.html" target="_blank" rel="noopener noreferrer">
                  Full Resume Page
                </a>
                <a className="resume-action" href={`mailto:${CONTACT.email}?subject=Engineering%20Opportunity`}>
                  Email Me
                </a>
                <a className="resume-action" href={CONTACT.phoneHref}>
                  Call
                </a>
                <a className="resume-action" href={CONTACT.githubUrl} target="_blank" rel="noopener noreferrer">
                  GitHub
                </a>
                <a className="resume-action" href={CONTACT.linkedinUrl} target="_blank" rel="noopener noreferrer">
                  LinkedIn
                </a>
              </div>
            </section>

            <details className="resume-panel" open>
              <summary>Professional Summary</summary>
              <div className="resume-panel-body">
                {SUMMARY.map((paragraph) => (
                  <p key={paragraph.slice(0, 24)}>{paragraph}</p>
                ))}
              </div>
            </details>

            <details className="resume-panel" open>
              <summary>Core Competencies</summary>
              <div className="resume-panel-body">
                <div className="competency-grid">
                  {COMPETENCIES.map((competency) => (
                    <div className="competency-item" key={competency.category}>
                      <strong>{competency.category}</strong>
                      {competency.items}
                    </div>
                  ))}
                </div>
              </div>
            </details>

            <details className="resume-panel" open>
              <summary>Professional Experience</summary>
              <div className="resume-panel-body">
                {EXPERIENCE.map((entry) => (
                  <details className="experience-card" open key={entry.company + entry.dates}>
                    <summary>
                      <span>
                        <h4>{entry.company}</h4>
                        <p className="experience-role">{entry.role}</p>
                      </span>
                      <span className="experience-dates">{entry.dates}</span>
                      <span className="experience-tech">
                        <strong>Technologies:</strong> {entry.technologies}
                      </span>
                    </summary>
                    <ul>
                      {entry.bullets.map((bullet) => (
                        <li key={bullet.slice(0, 32)}>{bullet}</li>
                      ))}
                    </ul>
                  </details>
                ))}
              </div>
            </details>

            <details className="resume-panel" open>
              <summary>Education</summary>
              <div className="resume-panel-body">
                <div className="education-block">
                  <div>
                    <h4>{EDUCATION.school}</h4>
                    <p>
                      {EDUCATION.degreeLabel} <em>— {EDUCATION.status}</em>
                    </p>
                  </div>
                  <p className="experience-dates">{EDUCATION.dateLabel}</p>
                </div>
              </div>
            </details>

            <details className="resume-panel" open>
              <summary>Professional Development</summary>
              <div className="resume-panel-body">
                <p>{PROFESSIONAL_DEVELOPMENT}</p>
              </div>
            </details>
          </div>
        </div>
      </div>
    </div>
  );
}
