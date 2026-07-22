export type ExperienceEntry = {
  company: string;
  role: string;
  dates: string;
  technologies: string;
  bullets: string[];
};

export type CompetencyEntry = {
  category: string;
  items: string;
};

export type HighlightEntry = {
  stat: string;
  detail: string;
};

export const NAME = "Wycliffe Otaniel Peart";

export const PROFESSIONAL_TITLE =
  "Building intelligent software systems where AI meets modern engineering.";

export const CONTACT = {
  email: "wycliffepeart@gmail.com",
  phoneDisplay: "+1 (876) 375-5597",
  phoneHref: "tel:+18763755597",
  location: "Jamaica",
  githubUrl: "https://github.com/wycliffepeart",
  githubDisplay: "github.com/wycliffepeart",
  linkedinUrl: "https://www.linkedin.com/in/wycliffepeart/",
  linkedinDisplay: "linkedin.com/in/wycliffepeart",
};

export const HIGHLIGHTS: HighlightEntry[] = [
  {
    stat: "10+ years",
    detail: "Enterprise software delivery across regulated and product environments.",
  },
  {
    stat: "5 industries",
    detail: "Banking, fintech, telecommunications, consulting, and digital media.",
  },
  {
    stat: "Full-stack",
    detail: "Backend platforms, web applications, APIs, integrations, and cloud delivery.",
  },
  {
    stat: "AI engineering",
    detail: "LLM integrations, AI-assisted workflows, agents, RAG, and automation.",
  },
];

export const SUMMARY: string[] = [
  "Senior Full-Stack AI Engineer with 10+ years of experience designing, developing, and delivering enterprise software solutions across banking, fintech, telecommunications, consulting, and digital media. I specialize in building intelligent applications that combine modern software engineering with large language models (LLMs), AI APIs, agentic workflows, and cloud-native architectures.",
  "Experienced in designing scalable backend services, distributed systems, microservices, enterprise integrations, and modern web applications using Node.js, Java, Spring Boot, React, Next.js, AWS, Kubernetes, and Terraform.",
  "Builds AI-powered software using LLM provider APIs, retrieval-augmented generation (RAG), Model Context Protocol (MCP), function calling, structured outputs, AI agents, and intelligent automation. Leverages AI-assisted engineering tools throughout the SDLC to accelerate delivery, improve software quality, automate testing, strengthen security, and optimize CI/CD pipelines while delivering secure, scalable, production-ready systems.",
];

export const COMPETENCIES: CompetencyEntry[] = [
  {
    category: "Agentic AI Engineering",
    items:
      "LLM Provider APIs, AI Agents, Agentic Workflows, MCP (Model Context Protocol), Function Calling, Structured Outputs, Retrieval-Augmented Generation (RAG), Prompt Engineering, AI Integration, Multi-step AI Workflows, Intelligent Automation",
  },
  {
    category: "AI Engineering Tools",
    items:
      "Cursor, GitHub Copilot, Claude Code, ChatGPT, Gemini Code Assist, Codex, AI-Assisted Code Review, Security Analysis, Test Generation, Documentation, CI/CD Optimization",
  },
  {
    category: "Backend Engineering",
    items: "Node.js, TypeScript, Java, Spring Boot, NestJS, Express.js, Fastify",
  },
  {
    category: "Frontend Engineering",
    items: "React, Next.js, Angular, TypeScript, JavaScript, HTML5, CSS3, Tailwind CSS, Material UI",
  },
  {
    category: "Mobile Development",
    items: "React Native, Flutter, Kotlin, Java, Expo, React Navigation, TanStack Query, EAS Build",
  },
  {
    category: "Architecture & Integration",
    items:
      "REST APIs, GraphQL, Microservices, Distributed Systems, Event-Driven Architecture, Domain-Driven Design, Design Patterns, Clean Architecture, Enterprise System Integration",
  },
  {
    category: "Cloud & DevOps",
    items: "AWS, Google Cloud Platform, Kubernetes, Docker, Terraform, GitHub Actions, GitLab CI/CD, Jenkins",
  },
  {
    category: "Data & Persistence",
    items: "PostgreSQL, MySQL, MongoDB, Oracle, DynamoDB, Redis",
  },
  {
    category: "Testing & Quality",
    items: "Jest, Cypress, Playwright, JUnit, Mockito, Test-Driven Development, Automated Testing",
  },
  {
    category: "Engineering Practices",
    items: "Agile, Scrum, CI/CD, SOLID Principles, Clean Code, Secure Software Development",
  },
  {
    category: "Version Control",
    items: "Git, GitHub, GitLab",
  },
];

export const EXPERIENCE: ExperienceEntry[] = [
  {
    company: "OnePay",
    role: "Software Engineer / AI Developer — Contract, BairesDev",
    dates: "May 2025 – June 2025",
    technologies:
      "Node.js, NestJS, Next.js, React, TypeScript, Jest, Cypress, Cursor, GitHub Copilot, Claude Code, ChatGPT, Gemini Code Assist, Codex, AI-Assisted Development, CI/CD Automation",
    bullets: [
      "Engineered backend services and REST APIs using Node.js, TypeScript, and NestJS for a fintech platform.",
      "Developed responsive web application features using React and Next.js, improving usability, maintainability, and frontend consistency.",
      "Designed and implemented AI-powered application features using LLM provider APIs and agentic workflows.",
      "Integrated AI capabilities using function calling, structured outputs, prompt engineering, and retrieval-augmented generation.",
      "Built reusable AI integration layers for intelligent application workflows.",
      "Leveraged Cursor, Claude Code, GitHub Copilot, ChatGPT, Gemini Code Assist, and Codex to accelerate implementation, refactoring, debugging, security analysis, documentation, and testing.",
      "Applied AI-driven code review, architecture analysis, and automated test generation to improve software quality and delivery velocity.",
      "Improved CI/CD and release workflows through analysis of build processes, deployment configuration, pipeline failures, and automation opportunities.",
      "Collaborated with engineering, product, and quality assurance teams on technical planning, code reviews, testing, documentation, and production deployments.",
    ],
  },
  {
    company: "National Commercial Bank Jamaica",
    role: "Senior Software Engineer — Contract",
    dates: "April 2023 – May 2025",
    technologies: "Node.js, Java, Spring Boot, React, Kubernetes, Docker, GitLab CI/CD, REST APIs, Microservices",
    bullets: [
      "Designed and developed enterprise backend services and REST APIs using Node.js, Java, and Spring Boot for banking applications.",
      "Built maintainable microservices using object-oriented design, reusable components, and modern software architecture patterns.",
      "Developed and supported containerized workloads using Docker and Kubernetes across enterprise application environments.",
      "Implemented and optimized GitLab CI/CD pipelines to support automated deployments across development, staging, and production environments.",
      "Integrated internal banking systems with external platforms, third-party services, and enterprise applications.",
      "Supported secure software delivery in a regulated banking environment with emphasis on reliability, maintainability, and operational continuity.",
      "Collaborated with business stakeholders, engineering teams, quality assurance professionals, and external vendors to deliver enterprise banking solutions.",
      "Participated in architecture reviews, code reviews, system testing, production releases, incident resolution, and ongoing improvements to performance, scalability, security, and maintainability.",
    ],
  },
  {
    company: "Cision — PR Software & Marketing Platform",
    role: "Frontend Engineer — Contract, In All Media",
    dates: "May 2022 – April 2023",
    technologies: "JavaScript, Web Components, HTML5, CSS3",
    bullets: [
      "Developed responsive, cross-browser-compatible, and accessibility-focused web applications for a digital media and public relations platform.",
      "Built reusable, modular, and maintainable user-interface components using JavaScript and Web Components.",
      "Translated product requirements, design specifications, and user-interface concepts into production-ready frontend features.",
      "Improved frontend performance, usability, consistency, and maintainability through continuous application enhancements and defect resolution.",
      "Collaborated with product owners, designers, backend engineers, and quality assurance teams during planning, code reviews, testing, and production releases.",
    ],
  },
  {
    company: "National Commercial Bank Jamaica",
    role: "Senior Software Engineer — Contract",
    dates: "February 2021 – May 2022",
    technologies: "Node.js, Java, Spring Boot, React, REST APIs, Microservices, CI/CD",
    bullets: [
      "Designed and implemented backend services, REST APIs, and enterprise integrations using Node.js, Java, and Spring Boot.",
      "Developed responsive frontend applications and reusable React components for internal banking and customer-facing systems.",
      "Built and maintained enterprise software supporting internal banking operations and customer-facing services.",
      "Translated business requirements into secure, scalable, and maintainable technical solutions.",
      "Integrated internal applications with external services, third-party platforms, and enterprise systems.",
      "Supported technical design, code reviews, automated testing, release planning, production deployments, and maintenance.",
      "Diagnosed and resolved defects, integration failures, production incidents, and application performance issues.",
    ],
  },
  {
    company: "Digicel Group",
    role: "Application Developer",
    dates: "August 2020 – February 2021",
    technologies: "Node.js, React, Angular, REST APIs, Cloud Services",
    bullets: [
      "Developed backend services, REST APIs, and system integrations using Node.js within cloud-based telecom environments.",
      "Extended the BiP Messaging platform by implementing channel-based features and customer-engagement capabilities.",
      "Developed frontend applications and reusable user-interface components using React and Angular.",
      "Integrated internal services and third-party platforms to support messaging and digital communication workflows.",
      "Collaborated with business stakeholders, analysts, designers, and engineers through design, development, testing, deployment, production support, and incident resolution.",
    ],
  },
  {
    company: "Vertis Technology",
    role: "Application Developer",
    dates: "March 2019 – June 2020",
    technologies: "Node.js, Java, Spring Boot, React, Angular, AWS, REST APIs",
    bullets: [
      "Designed and developed full-stack enterprise applications using Node.js, Java, Spring Boot, React, and Angular.",
      "Built and maintained cloud-native applications within AWS environments, focusing on scalability, reliability, and maintainability.",
      "Developed REST APIs, backend services, database integrations, reusable components, shared services, and modern frontend user interfaces.",
      "Translated business and functional requirements into practical technical designs and production-ready software.",
      "Supported application testing, deployment, maintenance, technical documentation, troubleshooting, and continuous improvement.",
    ],
  },
  {
    company: "Self-Employed",
    role: "Freelance Software Developer",
    dates: "January 2013 – December 2019",
    technologies: "Node.js, React, Laravel, Symfony, WordPress, JavaScript, PHP, MySQL",
    bullets: [
      "Designed and developed custom web applications, business platforms, and websites using Node.js, React, Laravel, Symfony, WordPress, JavaScript, and PHP.",
      "Delivered end-to-end software solutions covering requirements analysis, architecture, system design, development, testing, deployment, and maintenance.",
      "Developed REST APIs, authentication workflows, database schemas, administrative dashboards, and customer-facing interfaces.",
      "Integrated payment platforms, content management systems, third-party services, and external APIs.",
      "Managed client requirements, project scope, delivery schedules, releases, post-launch support, defect resolution, performance improvements, security enhancements, and new feature delivery.",
    ],
  },
];

export const EDUCATION = {
  school: "University of Technology, Jamaica",
  degreeLabel: "Bachelor of Science in Computing",
  status: "In Progress",
  dateLabel: "Expected 2028",
};

export const PROFESSIONAL_DEVELOPMENT =
  "Ongoing professional development through Udemy, technical documentation, vendor learning resources, and hands-on project work focused on LLM API integration, prompt engineering, AI agents, retrieval-augmented generation, cloud architecture, secure software delivery, system design, and modern full-stack engineering.";
