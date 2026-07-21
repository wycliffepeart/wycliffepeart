# Agent Instructions

This repository is Wycliffe Peart's profile site, LinkedIn post generation
workflow, and blog/post content repo. The site itself is a Next.js (App
Router) app in `site/`, built as a static export. The `app` directory
contains the GitHub profile content and the content the Next.js app doesn't
own: images, a resume PDF workflow, and Terraform deployment configuration
for S3 plus CloudFront. `app/blog/` holds topic-organized blog/post content
plus `app/blog/linkedin/`, the LinkedIn draft pipeline; it is merged into
the built site and deployed to the site's `/blog/` path (the `/blog` page
itself is `site/src/app/blog/page.tsx`, not part of `app/`).
`prompts/` and `templates/` hold the LinkedIn draft generation workflow.
The root `scripts/cli.py` module provides the single `wp` project CLI for
both areas, including `scripts/site_build.py`, which builds the Next.js app
and merges it with `app/`'s content directories into `site/out/`.

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

- `app/README.md` is the GitHub profile README. Only update it when
  resume/profile content changes require the public GitHub profile text to
  change. Do not update it for unrelated styling, infrastructure, CLI, or
  deployment changes unless the user explicitly asks.
- `site/src/app/page.tsx` is the deployed profile site's primary page
  (route `/`). Terraform uploads its built output as both `index.html` and
  `profile.html`.
- `site/src/app/resume/page.tsx` is the source of the browser-rendered
  resume (route `/resume`, built to the flat `resume.html`).
  `site/src/lib/resume-data.ts` holds the resume content shared between
  that page and the home page's resume modal (`site/src/components/home/ResumeModal.tsx`)
  - keep both in sync by editing the shared data, not by hand-duplicating text.
- `app/resume.pdf` is generated output from the built resume page. Do not
  hand-edit it.
- `scripts/resume_to_pdf.py` converts the built `site/out/resume.html` to
  `app/resume.pdf` with a Chromium-based browser. Run `wp build` (or
  `wp deploy`) before `wp pdf`, since it renders the build output, not
  `site/src/`.
- Root `scripts/cli.py` provides the `wp` CLI for building the site, PDF
  generation, and Terraform commands. `scripts/site_build.py` is the build
  and content-merge step both `wp run` and `wp deploy` use.
- `app/docs.md` documents CLI and non-resume project workflows.
  Update it for CLI, infrastructure, deployment, or other non-resume behavior
  changes that need documentation.
- `terraform/README.md` documents Terraform-specific deployment
  steps. Update it when Terraform behavior, uploaded files, or deployment
  prerequisites change.

## Resume PDF Rules

- Keep the default PDF input/output paths in
  `scripts/resume_to_pdf.py` synchronized with Terraform's
  upload key in
  `terraform/main.tf`.
- The current invariant is:
  - `scripts/resume_to_pdf.py` `DEFAULT_INPUT` -> `site/out/resume.html`
    (the built resume page)
  - `scripts/resume_to_pdf.py` `DEFAULT_OUTPUT` -> `app/resume.pdf`
  - `terraform/main.tf` `local.optional_files` uploads
    `resume.pdf` (from `site/out/resume.pdf`, copied there by
    `scripts/site_build.py` after PDF generation) as S3 object key
    `resume.pdf`
- If the generated PDF filename or location changes, update all references in
  `scripts/resume_to_pdf.py`, `scripts/site_build.py`, `scripts/cli.py`,
  `terraform/main.tf`, `terraform/README.md`, and any profile
  download links.
- Generate `resume.pdf` before deployment whenever the resume content has
  changed and the deployed PDF should reflect the latest resume. `wp deploy`
  does this automatically (build site -> generate PDF from the built resume
  page -> copy it into the merged output).
- Do not commit a stale `resume.pdf` after changing resume content. Regenerate
  it or clearly report that PDF generation could not be run.

## CLI And Local Commands

- Install locally with:
  - `python3 -m pip install -e .`
  - `cd site && npm install && cd ..`
- Use the package/module entry points instead of running `scripts/cli.py`
  directly:
  - `python3 -m scripts.cli --help`
  - `wp --help`
- Build the site (Next.js build + merge with `app/`'s content) with
  `wp build`.
- Generate the resume PDF with one of (after `wp build`):
  - `wp pdf`
  - `python3 -m scripts.resume_to_pdf`
- Run the built site locally with `wp run` (builds, then serves
  `site/out/`). For fast-iteration UI work without the content merge,
  `cd site && npm run dev` runs the Next.js dev server directly.
- `resume_to_pdf.py` requires Chrome, Chromium, Edge, or `CHROME_BIN` pointing to
  a Chromium-based browser.
- If touching Python code, run the relevant command help or targeted command when
  possible, for example `python3 -m scripts.cli --help`.
- If touching `site/`, run `cd site && npm run lint && npm run build` to
  catch TypeScript/ESLint/build errors.

## Terraform And Deployment Rules

- Use root `wp deploy` as the primary deployment path. It builds the site,
  regenerates `app/resume.pdf`, runs Terraform init/plan/apply from the
  correct directory, and keeps the build, PDF, and infrastructure workflow
  together. Use direct Terraform commands only for targeted infrastructure
  operations, debugging, or when the user explicitly asks for Terraform
  commands - run `wp build` first so `site/out/` is current.
- Terraform lives in root `terraform/` and should be run with that directory as
  the working directory unless using the `wp` wrapper. It uploads from
  `site/out/` (the merged Next.js build output), not `app/` directly.
- Do not add Route 53 hosted zones, Route 53 records, or DNS-provider automation
  unless the user explicitly asks for DNS to be managed in Terraform. The
  current domain workflow assumes DNS remains at GoDaddy and Terraform only
  attaches an already-issued ACM certificate to CloudFront.
- Terraform deploys a private S3 bucket with public access blocked, S3
  versioning, AES256 server-side encryption, CloudFront Origin Access Control,
  and a CloudFront distribution using either the default CloudFront certificate
  or a supplied ACM certificate ARN for a custom domain.
- Terraform uploads, from `site/out/`:
  - `index.html` as `index.html`
  - `profile.html` as `profile.html`
  - `resume.html` as `resume.html`
  - `blog/index.html` as `blog/index.html`
  - every other file under `blog/` (content merged in from `app/blog/`) as
    the same path under `blog/`
  - every file under `_next/` as the same path under `_next/` (the Next.js
    build's JS/CSS chunks)
  - `resume.pdf` as `resume.pdf` only when it exists
  - clean `/blog` and `/blog/` requests are rewritten to `/blog/index.html`
    by a CloudFront Function
- HTML objects and everything under `blog/` (except `blog/index.html`, which
  is covered by `local.html_files`) use no-cache headers. Other uploaded
  assets, including PDFs and `_next/`, use long immutable caching by default.
- Keep `terraform/main.tf` `local.html_files`, `local.optional_files`,
  `local.asset_files`, `local.next_static_files`, `local.blog_files`,
  `local.content_types`, and cache-control behavior synchronized with any
  new deployed asset types.
- Do not commit `terraform/terraform.tfvars`, Terraform state
  files, plan files, AWS credentials, or generated provider directories.
- For deployment changes, validate with `terraform fmt` and `terraform validate`
  when Terraform is initialized. If validation cannot run because providers or
  credentials are unavailable, report that clearly.
- Use AWS SSO or an existing AWS profile. Do not add static AWS access keys to
  the repository.

## Documentation Rules

- Resume/profile content changes may require updates across root `README.md`,
  `app/README.md`, `site/src/app/page.tsx` (and its components),
  `site/src/app/resume/page.tsx` (and `site/src/lib/resume-data.ts`), and
  regenerated `app/resume.pdf`. Keep root `README.md` aligned with profile
  details from `site/`.
- CLI, PDF workflow, Terraform, or deployment behavior changes may require
  updates to `terraform/README.md` and root `README.md`.
- Keep command examples consistent with the supported entry point in
  `pyproject.toml`: `wp`.

## Content And LinkedIn Workflow Rules

This repository also stores blog/post content and automation for generating
one draft LinkedIn post at a time. The `wp` CLI exposes both the site
deployment commands above and these content workflow commands from a single
entry point.

- `app/blog/` holds topic-organized blog/post material (for example
  `app/blog/sql/joins/`) plus `app/blog/linkedin/`, the LinkedIn draft
  pipeline. It is deployed to the site's `/blog/` path, so treat everything
  under it as public once deployed.
- `app/blog/linkedin/posts.json` is the LinkedIn post index.
- `app/blog/linkedin/posts/YYYY/MM/` contains generated markdown posts.
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
- Read `app/blog/linkedin/posts.json` before generating content.
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
- Store markdown at `app/blog/linkedin/posts/YYYY/MM/YYYY-MM-DD-HHMMSS-<slug>.md`.
- Ensure each JSON entry's `markdown` path matches the file that was created.

### Validation Rules

- Confirm the markdown file exists.
- Confirm `app/blog/linkedin/posts.json` is valid JSON.
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

- For profile or resume changes in `site/`, run `cd site && npm run lint && npm run build`,
  and inspect the built pages for broken links, inconsistent visible content,
  and stale PDF/download references.
- For resume PDF workflow changes, run `wp build` then PDF generation if a
  Chromium-based browser is available.
- For CLI changes, run `python3 -m scripts.cli --help` and any affected
  subcommand help.
- For content workflow changes, run `python3 -m pytest tests/` and confirm
  `app/blog/linkedin/posts.json` stays valid JSON.
- For Terraform changes, run `terraform fmt` and `terraform validate` from
  `terraform/` when possible.
- Before finishing, run `git status --short` and summarize changed files,
  generated files, and any checks that could not be completed.
