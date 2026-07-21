import type { Metadata } from "next";
import "@/styles/home.css";
import Nav from "@/components/home/Nav";
import Hero from "@/components/home/Hero";
import WorkSection from "@/components/home/WorkSection";
import StackSection from "@/components/home/StackSection";
import FocusSection from "@/components/home/FocusSection";
import BlogPreviewSection from "@/components/home/BlogPreviewSection";
import ContactSection from "@/components/home/ContactSection";
import SiteFooter from "@/components/shared/SiteFooter";
import ResumeModal from "@/components/home/ResumeModal";
import { ResumeModalProvider } from "@/components/home/resume-modal-context";

const TITLE = "Wycliffe Otaniel Peart | Senior Full-Stack AI Engineer";
const DESCRIPTION =
  "Wycliffe Otaniel Peart is a Senior Full-Stack AI Engineer building intelligent software systems where AI meets modern engineering.";
const SOCIAL_DESCRIPTION =
  "Building end-to-end solutions across web, cloud, and AI with production-ready applications, APIs, cloud delivery, and practical AI integrations.";
const IMAGE_URL = "https://www.wycliffepeart.com/assets/head-shot.jpeg";
const IMAGE_ALT =
  "Headshot of Wycliffe Otaniel Peart, building intelligent software systems where AI meets modern engineering.";

export const metadata: Metadata = {
  title: TITLE,
  description: DESCRIPTION,
  authors: [{ name: "Wycliffe Otaniel Peart" }],
  keywords: [
    "Wycliffe Otaniel Peart",
    "intelligent software systems",
    "agentic AI engineering",
    "web development",
    "cloud engineering",
    "AWS",
    "Node.js",
    "Java",
    "React",
    "software architecture",
  ],
  robots: "index, follow",
  alternates: {
    canonical: "https://www.wycliffepeart.com/",
  },
  openGraph: {
    type: "profile",
    firstName: "Wycliffe",
    lastName: "Peart",
    username: "wycliffepeart",
    url: "https://www.wycliffepeart.com/",
    title: TITLE,
    description: SOCIAL_DESCRIPTION,
    siteName: "Wycliffe Otaniel Peart",
    images: [
      {
        url: IMAGE_URL,
        secureUrl: IMAGE_URL,
        type: "image/jpeg",
        width: 1195,
        height: 1316,
        alt: IMAGE_ALT,
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: SOCIAL_DESCRIPTION,
    images: [IMAGE_URL],
  },
};

const PERSON_JSON_LD = {
  "@context": "https://schema.org",
  "@type": "Person",
  name: "Wycliffe Otaniel Peart",
  jobTitle: "Senior Full-Stack AI Engineer",
  description: "Building intelligent software systems where AI meets modern engineering.",
  email: "mailto:wycliffepeart@gmail.com",
  telephone: "+18763755597",
  address: {
    "@type": "PostalAddress",
    addressCountry: "JM",
  },
  sameAs: ["https://github.com/wycliffepeart", "https://www.linkedin.com/in/wycliffepeart/"],
  knowsAbout: [
    "Full-stack software engineering",
    "AI application development",
    "Cloud architecture",
    "AWS",
    "Node.js",
    "Java",
    "React",
    "DevOps",
  ],
};

export default function HomePage() {
  return (
    <ResumeModalProvider>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(PERSON_JSON_LD) }}
      />

      <div className="page">
        <Nav />

        <main id="top">
          <Hero />
          <WorkSection />
          <StackSection />
          <FocusSection />
          <BlogPreviewSection />
          <ContactSection />
        </main>

        <SiteFooter />
      </div>

      <ResumeModal />
    </ResumeModalProvider>
  );
}
