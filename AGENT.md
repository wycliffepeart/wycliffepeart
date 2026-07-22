# Agent Instructions

This repository is Wycliffe Peart's profile site, LinkedIn post generation
workflow, and blog/post content repo. The site itself is a Next.js (App
Router) app at the project root (`src/app/`, `public/`, `next.config.ts`,
`package.json`), built as a static export. Blog posts are native Next.js MDX
pages: source files live in `content/blog/*.mdx`, loaded by
`src/lib/blog.ts` and rendered by `src/app/blog/page.tsx` (the listing) and
`src/app/blog/[slug]/page.tsx` (each post, via `next-mdx-remote`). Adding a
new `.mdx` file under `content/blog/` and rebuilding is enough to publish a
new post - no merge step or Terraform change is needed.

`workspace/` holds content the Next.js app doesn't own: a resume PDF
workflow (`workspace/resume.pdf`) and the LinkedIn draft pipeline
(`workspace/blog/linkedin/`, plus `workspace/blog/sql/joins/` source
material for a LinkedIn carousel). None of `workspace/` is deployed to the
site; it's local/CI working storage for the content pipeline below.
`prompts/` and `templates/` hold the LinkedIn draft generation workflow.
The root `scripts/cli.py` module provides the single `wp` project CLI for
both areas, including `scripts/site_build.py`, which builds the Next.js
static export into `out/`.

`workspace/` must never be renamed to `app/`: Next.js treats a root-level
`app/` directory as its App Router directory even when the actual routes
live in `src/app/`, which silently breaks all routing except the built-in
404 page.

## Default Workflow

- Commit after any completed change when the user has asked for project edits.
  Use a detailed, descriptive commit message that clearly supports the change:
  summarize the purpose in the subject and include concise details about what
  changed in the commit body when the change is more than trivial.
- Before editing, check `git status --short` and do not overwrite unrelated user
  changes. If a file already has user edits, work with the current contents.
- Keep changes scoped to the requested area. Do not reformat large HTML,
  Terraform, or generated files unless formatting is part of the task.
- Prefer `rg` and `rg --files` for project searches.
- Use ASCII for new text unless the target file already uses non-ASCII content
  for a clear reason.

## Project Files

- `src/app/page.tsx` is the deployed profile site's primary page
  (route `/`). Terraform uploads its built output as both `index.html` and
  `profile.html`.
- `src/app/resume/page.tsx` is the source of the browser-rendered
  resume (route `/resume`, built to the flat `resume.html`).
  `src/lib/resume-data.ts` holds the resume content shared between
  that page and the home page's resume modal (`src/components/home/ResumeModal.tsx`)
  - keep both in sync by editing the shared data, not by hand-duplicating text.
- `content/blog/*.mdx` are the blog post sources. Each file needs frontmatter
  (`title`, `date` as `YYYY-MM-DD`, `excerpt`, `tags`, optional `slug` -
  defaults to the filename). `src/lib/blog.ts` reads and sorts them;
  `src/app/blog/page.tsx` lists them; `src/app/blog/[slug]/page.tsx` renders
  one via `next-mdx-remote/rsc` with `dynamicParams = false`, so every post
  must be discoverable through `generateStaticParams` at build time.
- `workspace/resume.pdf` is generated output from the built resume page. Do
  not hand-edit it.
- `scripts/resume_to_pdf.py` converts the built `out/resume.html` to
  `workspace/resume.pdf` with a Chromium-based browser. Run `wp build` (or
  `wp deploy`) before `wp pdf`, since it renders the build output, not
  `src/`.
- Root `scripts/cli.py` provides the `wp` CLI for building the site, PDF
  generation, and Terraform commands. `scripts/site_build.py` is the build
  step both `wp run` and `wp deploy` use.
- `terraform/README.md` documents Terraform-specific deployment
  steps. Update it when Terraform behavior, uploaded files, or deployment
  prerequisites change.

## Resume PDF Rules

- Keep the default PDF input/output paths in
  `scripts/resume_to_pdf.py` synchronized with Terraform's
  upload key in
  `terraform/main.tf`.
- The current invariant is:
  - `scripts/resume_to_pdf.py` `DEFAULT_INPUT` -> `out/resume.html`
    (the built resume page)
  - `scripts/resume_to_pdf.py` `DEFAULT_OUTPUT` -> `workspace/resume.pdf`
  - `terraform/main.tf`'s `deployable_files` filter uploads `resume.pdf`
    (from `out/resume.pdf`, copied there by `scripts/site_build.py` after
    PDF generation) as S3 object key `resume.pdf` whenever it's present in
    `out/`
- If the generated PDF filename or location changes, update all references in
  `scripts/resume_to_pdf.py`, `scripts/site_build.py`, `scripts/cli.py`,
  `terraform/main.tf`, `terraform/README.md`, and any profile
  download links.
- Generate `resume.pdf` before deployment whenever the resume content has
  changed and the deployed PDF should reflect the latest resume. `wp deploy`
  does this automatically (build site -> generate PDF from the built resume
  page -> copy it into `out/`).
- Do not commit a stale `resume.pdf` after changing resume content. Regenerate
  it or clearly report that PDF generation could not be run.

## CLI And Local Commands

- Install locally with:
  - `python3 -m pip install -e .`
  - `npm install`
- Use the package/module entry points instead of running `scripts/cli.py`
  directly:
  - `python3 -m scripts.cli --help`
  - `wp --help`
- Build the site (`next build` as a static export) with `wp build`.
- Generate the resume PDF with one of (after `wp build`):
  - `wp pdf`
  - `python3 -m scripts.resume_to_pdf`
- Run the built site locally with `wp run` (builds, then serves `out/`).
  For fast-iteration UI work, `npm run dev` runs the Next.js dev server
  directly (blog posts render from `content/blog/*.mdx` in dev too).
- `resume_to_pdf.py` requires Chrome, Chromium, Edge, or `CHROME_BIN` pointing to
  a Chromium-based browser.
- If touching Python code, run the relevant command help or targeted command when
  possible, for example `python3 -m scripts.cli --help`.
- If touching `src/`, `content/`, `public/`, or other Next.js project files,
  run `npm run lint && npm run build` to catch TypeScript/ESLint/build
  errors.

## Terraform And Deployment Rules

- Use root `wp deploy` as the primary deployment path. It builds the site,
  regenerates `workspace/resume.pdf`, runs Terraform init/plan/apply from
  the correct directory, and keeps the build, PDF, and infrastructure
  workflow together. Use direct Terraform commands only for targeted
  infrastructure operations, debugging, or when the user explicitly asks for
  Terraform commands - run `wp build` first so `out/` is current.
- Terraform lives in root `terraform/` and should be run with that directory as
  the working directory unless using the `wp` wrapper. It uploads from
  `out/` (the Next.js static export), not `workspace/` directly.
- Do not add Route 53 hosted zones, Route 53 records, or DNS-provider automation
  unless the user explicitly asks for DNS to be managed in Terraform. The
  current domain workflow assumes DNS remains at GoDaddy and Terraform only
  attaches an already-issued ACM certificate to CloudFront.
- Terraform deploys a private S3 bucket with public access blocked, S3
  versioning, AES256 server-side encryption, CloudFront Origin Access Control,
  and a CloudFront distribution using either the default CloudFront certificate
  or a supplied ACM certificate ARN for a custom domain.
- Terraform's `local.deployable_files` filters the full `out/` export down to
  HTML documents, `_next/` chunks, `assets/`, `favicon.ico`, and `resume.pdf`
  - excluding Next's RSC prefetch payload files (`*.txt`, `__next.*`) and the
    `/404` and `/_not-found` export artifacts, since this site hard-navigates
    with plain `<a>` tags instead of `next/link`. Every blog post's
    `out/blog/<slug>/index.html` is picked up automatically; there is no
    separate blog content merge step or per-post Terraform entry.
  - `index.html` is also uploaded as `profile.html` (legacy duplicate key,
    produced by `scripts/site_build.py`), and `resume/index.html` is
    flattened to `resume.html` the same way.
  - a CloudFront Function rewrites any directory-style request (`/`, `/blog`,
    `/blog/`, `/blog/<slug>/`, ...) to its `index.html` object.
- HTML objects use no-cache headers (`local.html_keys`). Everything else
  (content-hashed `_next/` chunks, images, the resume PDF) uses long
  immutable caching by default.
- Keep `terraform/main.tf`'s `local.deployable_files`, `local.html_keys`,
  `local.content_types`, and `local.content_dispositions` synchronized with
  any new deployed asset types.
- Do not commit `terraform/terraform.tfvars`, Terraform state
  files, plan files, AWS credentials, or generated provider directories.
- For deployment changes, validate with `terraform fmt` and `terraform validate`
  when Terraform is initialized. If validation cannot run because providers or
  credentials are unavailable, report that clearly.
- Use AWS SSO or an existing AWS profile. Do not add static AWS access keys to
  the repository.

## Documentation Rules

- Resume/profile content changes may require updates across root `README.md`,
  `src/app/page.tsx` (and its components), `src/app/resume/page.tsx` (and
  `src/lib/resume-data.ts`), and regenerated `workspace/resume.pdf`. Keep
  root `README.md` aligned with profile details from `src/`.
- CLI, PDF workflow, Terraform, or deployment behavior changes may require
  updates to `terraform/README.md` and root `README.md`.
- Keep command examples consistent with the supported entry point in
  `pyproject.toml`: `wp`.

## Content And LinkedIn Workflow Rules

This repository also stores blog/post content and automation for generating
one draft LinkedIn post at a time. The `wp` CLI exposes both the site
deployment commands above and these content workflow commands from a single
entry point.

- `workspace/blog/` holds topic-organized blog/post material (for example
  `workspace/blog/sql/joins/`, source material for a LinkedIn carousel) plus
  `workspace/blog/linkedin/`, the LinkedIn draft pipeline. None of it is
  deployed to the site - it's internal working storage, separate from the
  public MDX posts under `content/blog/`.
- `workspace/blog/linkedin/posts.json` is the LinkedIn post index.
- `workspace/blog/linkedin/posts/YYYY/MM/` contains generated markdown posts.
- `prompts/linkedin-post-generator.md` is the canonical LinkedIn generation prompt.
- `templates/design/` contains LinkedIn carousel HTML templates.
- `scripts/codex_json.py`, `scripts/env_utils.py`, `scripts/github_publish.py`,
  `scripts/linkedin_carousel.py`, `scripts/logging_utils.py`, and
  `scripts/posts.py` implement the `codex-json`, `codex e`,
  `linkedin-carousel generate`, `publish github`, and `github publish-post`
  `wp` subcommands.
- `.github/workflows/generate-linkedin-post.yml` runs the scheduled/manual
  LinkedIn post generation workflow.
- `.env.local` (gitignored) holds `GH_TOKEN`, `WP_GITHUB_REPO`,
  `WP_GITHUB_PROJECT_ID`, and `WP_CODEX_POST_RETRIES`. Copy `.env.example`
  to `.env.local` and fill in real values; never commit real tokens.

### Content Generation Rules

- Generate exactly one LinkedIn post per run.
- Never overwrite, delete, or rewrite existing posts unless explicitly requested.
- Read all files under `prompts/` before generating content.
- Read `workspace/blog/linkedin/posts.json` before generating content.
- Inspect previous markdown posts before choosing a topic, title, hook, examples, conclusion, and hashtags.
- Avoid duplicate topics, titles, hooks, conclusions, examples, hashtags, and distinctive wording.
- Keep posts professional, natural, educational, and practical.
- Avoid marketing language, clickbait, unsupported statistics, and references to AI generating the content.
- Keep post body length between 150 and 300 words.
- Include a strong opening, short paragraphs, practical insight, an actionable takeaway, a thoughtful closing question, and 3-5 hashtags.

### Metadata Rules

- Use UUID v4 for `id`.
- Use kebab-case for `slug`.
- Use UTC ISO-8601 for `createdAt`.
- Use `YYYY-MM-DD` for `date`.
- Set `status` to `draft` unless a workflow step (for example `wp publish github`) changes it.
- Use 3-5 tags.
- Keep `excerpt` at or below 180 characters.
- Store markdown at `workspace/blog/linkedin/posts/YYYY/MM/YYYY-MM-DD-HHMMSS-<slug>.md`.
- Ensure each JSON entry's `markdown` path matches the file that was created.

### Validation Rules

- Confirm the markdown file exists.
- Confirm `workspace/blog/linkedin/posts.json` is valid JSON.
- Confirm the UUID is unique.
- Confirm the slug is unique.
- Confirm exactly one new post was added.
- Confirm `updatedAt` was updated when a post is added.

### GitHub Publishing Rules

- Use `wp publish github` or `wp github publish-post` to create GitHub issues,
  branches, pull requests, and optional Project items for LinkedIn posts.
- Use GitHub CLI (`gh`) for GitHub issue, branch, push, and pull request operations.
- If `gh` lacks required scopes, refresh the token with the minimum required scopes and continue after authorization.
- If changing files under `.github/workflows/`, ensure the GitHub token has the `workflow` scope before pushing.

## Verification Checklist

- For profile, resume, or blog changes, run `npm run lint && npm run build`,
  and inspect the built pages for broken links, inconsistent visible content,
  and stale PDF/download references.
- For resume PDF workflow changes, run `wp build` then PDF generation if a
  Chromium-based browser is available.
- For CLI changes, run `python3 -m scripts.cli --help` and any affected
  subcommand help.
- For content workflow changes, run `python3 -m pytest tests/` and confirm
  `workspace/blog/linkedin/posts.json` stays valid JSON.
- For Terraform changes, run `terraform fmt` and `terraform validate` from
  `terraform/` when possible.
- Before finishing, run `git status --short` and summarize changed files,
  generated files, and any checks that could not be completed.
