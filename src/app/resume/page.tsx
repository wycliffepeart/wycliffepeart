import type { Metadata } from "next";
import "@/styles/resume.css";
import ResumeHeader from "@/components/resume/ResumeHeader";
import {
  CompetenciesSection,
  EducationSection,
  ExperienceSection,
  ProfessionalDevelopmentSection,
  SummarySection,
} from "@/components/resume/ResumeSections";
import PrintButton from "@/components/resume/PrintButton";

export const metadata: Metadata = {
  title: "Wycliffe Otaniel Peart | Senior Full-Stack AI Engineer",
};

export default function ResumePage() {
  return (
    <>
      {/* Rendered directly in the page (not a root-layout <head>) so the font
          only loads on this route. React 19 hoists <link> tags rendered
          anywhere in the tree into <head> automatically. The no-page-custom-font
          rule targets the legacy Pages Router's _document.js and doesn't apply
          to this App Router pattern. */}
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      {/* eslint-disable-next-line @next/next/no-page-custom-font */}
      <link
        href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"
        rel="stylesheet"
      />

      <main className="resume">
        <ResumeHeader />
        <SummarySection />
        <CompetenciesSection />
        <ExperienceSection />
        <EducationSection />
        <ProfessionalDevelopmentSection />
      </main>

      <PrintButton />
    </>
  );
}
