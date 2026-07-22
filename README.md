# Wycliffe Peart Profile

Next.js developer profile site (built as a static export) with an MDX blog,
a resume PDF generator, Terraform deployment utilities, and a LinkedIn post
generation / content workflow.

The site is a Next.js App Router project at the project root (`src/`,
`public/`, `content/`, `next.config.ts`, `package.json`). Blog posts are
MDX files under `content/blog/`, rendered by native Next.js pages - no
separate content-merge step. `workspace/` holds content the Next.js app
doesn't own: the generated resume PDF and the LinkedIn draft pipeline. The
`wp` CLI handles the common local and deployment tasks:

- build the Next.js static export and serve it locally
- generate `workspace/resume.pdf` from the built resume page
- initialize, plan, and apply the Terraform deployment
- run the full deploy workflow end to end

Terraform deploys the site to a private S3 bucket and serves it through
CloudFront over HTTPS.

The same `wp` CLI also drives the content workflow that lives in
`workspace/blog/`, `prompts/`, and `templates/`:

- extract structured JSON from Codex transcript output
- run Codex to draft one LinkedIn post at a time and persist it under
  `workspace/blog/linkedin/`
- render LinkedIn carousel HTML/PDF from `templates/design/`
- publish pending LinkedIn posts as GitHub issues, branches, and pull requests

See [Content And LinkedIn Workflow](#content-and-linkedin-workflow) below.

## Project Layout

| Path | Purpose |
| --- | --- |
| `src/app/` | Next.js App Router pages: `/` (`page.tsx`), `/resume`, `/blog`, `/blog/[slug]`. |
| `src/components/`, `src/lib/`, `src/styles/` | Site components, shared data (including the MDX blog loader `src/lib/blog.ts`), and styles. |
| `content/blog/*.mdx` | Blog post source files (frontmatter + Markdown/MDX body). Add a file here and rebuild to publish a post - no other changes needed. |
| `public/` | Static assets served as-is, including `public/assets/` (profile image, social preview). |
| `out/` | Build output: `wp build` runs `next build` here (`next.config.ts` sets `output: "export"`). Not committed; this is what Terraform uploads. |
| `workspace/` | Content the Next.js app doesn't own, used only by the Python CLI/content workflow - never deployed. |
| `workspace/resume.pdf` | Generated resume PDF, uploaded only when present. |
| `workspace/blog/` | LinkedIn draft pipeline (`workspace/blog/linkedin/`) and source material for a LinkedIn carousel (`workspace/blog/sql/joins/`). |
| `prompts/` | LinkedIn post generation prompts used by `wp codex e`. |
| `templates/design/` | LinkedIn carousel HTML templates used by `wp linkedin-carousel generate`. |
| `assets/` | Reference assets for the content workflow (design references, etc.). |
| `.github/workflows/generate-linkedin-post.yml` | Scheduled/manual LinkedIn post generation workflow. |
| `scripts/` | Python CLI, PDF generation, site build, and content workflow code. |
| `terraform/` | AWS S3, CloudFront, DNS, and upload configuration. |
| `pyproject.toml` | Python package metadata and CLI entry points. |
| `package.json` | Next.js project metadata, dependencies, and scripts. |

Run `wp` and `python3 -m scripts...` commands from the project root unless
the package is installed in your active environment.

`workspace/` must stay named `workspace/`, not `app/`: Next.js treats a
root-level `app/` directory as its App Router directory even though the
site's routes live in `src/app/`, so a root `app/` silently breaks routing.

## Prerequisites

- Python 3.9 or newer.
- Node.js and npm, for the Next.js site.
- Terraform installed as `terraform`.
- AWS CLI installed and configured.
- An AWS SSO profile, or another AWS profile Terraform can use.
- Playwright Chromium for PDF generation.

## Install The CLI

From the project root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e .
python3 -m playwright install chromium
npm install
```

For local testing without installing the package, run the module directly:

```sh
python3 -m scripts.cli --help
```

Do not run `python3 scripts/cli.py` directly. The CLI imports the `scripts`
package and expects the project root to be on Python's import path.

## Local Development

Build the site and serve it from `out/`:

```sh
wp run
```

This runs `next build`, then serves the static export - the same thing
`wp deploy` uploads. There's no hot-reload; re-run `wp run` after editing
`src/` or `content/`. For fast-iteration UI work, run `npm run dev` directly
(the dev server also reads blog posts from `content/blog/*.mdx`).

The default URL is:

```text
http://127.0.0.1:8000
```

Use another port when needed:

```sh
wp run --port 8080
```

Build the site without serving it:

```sh
wp build
```

Generate the resume PDF:

```sh
wp pdf
```

By default, this reads the built `out/resume.html` and writes
`workspace/resume.pdf`, so run `wp build` first (or use `wp deploy`, which
sequences this automatically).

## Writing A Blog Post

Add a new file under `content/blog/`, for example `content/blog/my-post.mdx`,
with frontmatter and a Markdown/MDX body:

```mdx
---
title: "My Post Title"
date: "2026-08-01"
excerpt: "One or two sentences shown in the post list and link previews."
tags: ["topic-one", "topic-two"]
---

Post body in Markdown, including code fences, tables, and lists.
```

`slug` is optional in frontmatter and defaults to the filename (without
`.mdx`); set it explicitly if you want a different URL. Run `wp build` (or
`npm run dev` while iterating) to see the post at `/blog/<slug>/`; it's
listed automatically on `/blog` and the homepage's blog preview, newest
first by `date`. No Terraform or build-script change is needed - the next
`wp deploy` publishes it.

## AWS And Terraform Setup

Set up and log in to AWS SSO:

```sh
aws configure sso
aws sso login --profile your-sso-profile
```

If you use `aws login`, export the login credentials before running Terraform:

```sh
eval "$(aws configure export-credentials --format env)"
```

Create local Terraform variables:

```sh
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform/terraform.tfvars` and set at least:

```hcl
aws_profile         = "your-sso-profile"
site_bucket_name    = "globally-unique-bucket-name"
custom_domain_name  = "wycliffepeart.com"
custom_domain_names = ["wycliffepeart.com", "www.wycliffepeart.com"]
acm_certificate_arn = "arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERTIFICATE_ID"
```

The CloudFront ACM certificate must be issued in `us-east-1` and cover every
domain in `custom_domain_names`.

For GoDaddy-managed DNS, create the ACM certificate, add the ACM DNS validation
CNAME in GoDaddy, wait for the certificate to be issued, then set
`acm_certificate_arn`. After deployment, point GoDaddy DNS to the
`godaddy_dns_records` Terraform output.

Use a normal CNAME for `www.wycliffepeart.com`. The apex domain
`wycliffepeart.com` needs ALIAS, ANAME, or CNAME flattening. If GoDaddy cannot
support that for the apex, move DNS hosting to Route 53 or Cloudflare, or
redirect the apex to `www.wycliffepeart.com`.

Return to the project root before running `wp`:

```sh
cd ..
```

## Deploy

Use `wp deploy` as the primary deployment command:

```sh
wp deploy
```

The deploy workflow:

1. Builds the Next.js static export into `out/`.
2. Generates `workspace/resume.pdf` from the freshly built resume page.
3. Runs `terraform init`.
4. Runs `terraform plan`.
5. Runs `terraform apply`.

To skip Terraform init after the directory has already been initialized:

```sh
wp deploy --skip-init
```

To apply without Terraform's interactive confirmation:

```sh
wp deploy --auto-approve
```

To save and apply a named Terraform plan:

```sh
wp deploy --out tfplan
```

When `--out` is provided without a `plan_file`, `deploy` applies the plan file
it just created.

## Review Before Applying

Use the individual commands when you want to inspect changes before applying
them:

```sh
wp build
wp pdf
wp init
wp plan --out tfplan
wp apply tfplan
```

Get the deployed site URL after applying:

```sh
cd terraform
terraform output site_url
```

## CLI Reference

Run help for the full command list:

```sh
wp --help
```

Run help for a specific command:

```sh
wp pdf --help
wp deploy --help
wp run --help
```

### `wp pdf`

Generates a PDF version of the resume page. Requires `wp build` to have run
first, since it renders the built `out/resume.html`, not source files under
`src/`.

Default behavior:

- reads `out/resume.html`
- writes `workspace/resume.pdf`
- uses Playwright's managed Chromium browser
- creates the output directory when needed
- fails if the input file is missing, Playwright or Chromium is not installed,
  rendering times out, or the generated PDF is missing or empty

Options:

| Option | Description | Default |
| --- | --- | --- |
| `--input INPUT` | Built HTML file to render. | `out/resume.html` |
| `--output OUTPUT` | Destination PDF path. | `workspace/resume.pdf` |
| `--browser BROWSER` | Optional path to a Chrome or Chromium executable. | Playwright Chromium |
| `--timeout TIMEOUT` | Maximum seconds to wait for PDF generation. | `60` |

Examples:

```sh
wp build
wp pdf
wp pdf --timeout 120
wp pdf --browser "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

Terraform uploads `resume.pdf` only when it exists in `out/` (copied there
from `workspace/resume.pdf` by `wp build`/`wp deploy`).

### `wp init`

Runs `terraform init` in `terraform/`.

Use it after cloning the project, changing provider configuration, or deleting
Terraform's local `.terraform/` directory.

### `wp plan`

Runs `terraform plan` in `terraform/`.

Options:

| Option | Description |
| --- | --- |
| `--out OUT` | Saves the generated plan to a file by passing `-out OUT` to Terraform. |

Example:

```sh
wp plan --out tfplan
```

### `wp apply`

Runs `terraform apply` in `terraform/`.

Options and arguments:

| Option or argument | Description |
| --- | --- |
| `--auto-approve` | Passes `-auto-approve` to Terraform. |
| `plan_file` | Optional Terraform plan file to apply. |

Examples:

```sh
wp apply
wp apply --auto-approve
wp apply tfplan
```

### `wp deploy`

Runs the full deployment workflow: builds the site, generates `resume.pdf`
from the freshly built resume page, then runs Terraform init/plan/apply.

Options and arguments:

| Option or argument | Description | Default |
| --- | --- | --- |
| `--input INPUT` | Built HTML file to render into PDF before deployment. | `out/resume.html` |
| `--output OUTPUT` | Destination PDF path. | `workspace/resume.pdf` |
| `--browser BROWSER` | Optional path to a Chrome or Chromium executable. | Playwright Chromium |
| `--timeout TIMEOUT` | Maximum seconds to wait for PDF generation. | `60` |
| `--skip-init` | Skips `terraform init`. | Disabled |
| `--out OUT` | Saves the Terraform plan to a file. | No saved plan |
| `--auto-approve` | Passes `-auto-approve` to Terraform apply. | Disabled |
| `plan_file` | Optional Terraform plan file to apply. | None |

Prefer either `--out` or an explicit `plan_file`. If both are supplied,
Terraform creates a new plan at the `--out` path, but apply receives the
explicit `plan_file`.

### `wp build`

Builds the Next.js static export (`next build`) into `out/`. This is what
`wp run` and `wp deploy` both use.

### `wp run`

Runs `wp build`, then serves `out/` locally.

Options:

| Option | Description | Default |
| --- | --- | --- |
| `--host HOST` | Host interface to bind. | `127.0.0.1` |
| `--port PORT` | Port to serve on. | `8000` |

## What Terraform Uploads

The Terraform configuration filters `out/` down to HTML documents, `_next/`
JS/CSS chunks, `assets/`, `favicon.ico`, and `resume.pdf` (when present), and
uploads that set to S3:

- `index.html` as `index.html`
- `profile.html` as `profile.html` (legacy duplicate of `index.html`)
- `resume.html` as `resume.html`
- every blog post's `blog/<slug>/index.html`, plus `blog/index.html`, exactly
  as `next build` produced them - adding a new `content/blog/*.mdx` file and
  redeploying is enough to publish it, with no Terraform change
- `resume.pdf` with attachment headers for downloading
- every file under `assets/` and `_next/`

Next's RSC prefetch payload files (`*.txt`, `__next.*`) and the `/404` and
`/_not-found` export artifacts are excluded, since the site hard-navigates
with plain `<a>` tags instead of `next/link` and never fetches them.

A CloudFront Function rewrites any directory-style request (`/`, `/blog`,
`/blog/`, `/blog/<slug>/`, ...) to its `index.html` object.

The S3 bucket keeps object versions for rollback, and noncurrent object
versions expire after 30 days to keep storage costs bounded.

## Content And LinkedIn Workflow

`workspace/blog/` stores blog/post material organized by topic (for example
`workspace/blog/sql/joins/`, source material for a LinkedIn carousel) plus
`workspace/blog/linkedin/`, the LinkedIn draft pipeline. This is separate
from `content/blog/`, the public MDX posts the site actually deploys -
nothing under `workspace/` is served by the site.

- `workspace/blog/linkedin/posts.json` is the post index.
- `workspace/blog/linkedin/posts/YYYY/MM/` contains generated markdown posts.
- `prompts/linkedin-post-generator.md` is the canonical generation prompt.
- `templates/design/` contains LinkedIn carousel HTML templates.

Set up local secrets before running the Codex or GitHub publishing commands:

```sh
cp .env.example .env.local
# edit .env.local and set GH_TOKEN, WP_GITHUB_REPO, WP_GITHUB_PROJECT_ID
```

### `wp codex-json`

Extracts the assistant JSON payload from Codex transcript text.

```sh
wp codex-json codex-output.txt --pretty
wp codex-json codex-output.txt --field choices.0.message.content
codex ... | wp codex-json --pretty
```

### `wp codex e`

Runs `codex e` and requires a LinkedIn post JSON response, then writes the
Markdown file under `workspace/blog/linkedin/posts/YYYY/MM/` and appends the
metadata-only entry to `workspace/blog/linkedin/posts.json`.

```sh
wp codex e "write linkedin post about idempotency, respond in json" --pretty
wp codex e "..." --no-write --pretty
wp codex e "..." --dry-run --pretty
```

If validation or persistence fails, the command retries Codex generation up
to 5 times by default. Set `WP_CODEX_POST_RETRIES` in `.env.local` or pass
`--retries` to change the retry count.

### `wp linkedin-carousel generate`

Renders LinkedIn carousel HTML, and PDF when Playwright's Chromium browser is
available, from a JSON data file and an HTML template.

```sh
wp linkedin-carousel generate \
  --data workspace/blog/sql/joins/data.json \
  --template templates/design/11-gloss.html \
  --output-dir workspace/blog/sql/joins \
  --pretty
wp linkedin-carousel generate --no-pdf --pretty
```

### `wp publish github`

Creates GitHub issues, branches, pull requests, and optional Project items
for every post with `pending` status in `workspace/blog/linkedin/posts.json`.

```sh
wp publish github --pretty
wp publish github --repo 9to5guru/wp-profile --base main --project-id 5 --dry-run --pretty
```

### `wp github publish-post`

Publishes a single LinkedIn post Markdown file through the same GitHub
issue/branch/PR flow.

```sh
wp github publish-post workspace/blog/linkedin/posts/2026/07/2026-07-21-post.md --pretty
```

### `.github/workflows/generate-linkedin-post.yml`

Runs on a schedule and on manual dispatch to generate one LinkedIn post via
Codex and commit it back to the repository. It requires an `OPENAI_API_KEY`
secret in the repository settings.

## Common Workflows

First-time setup and deployment:

```sh
aws configure sso
aws sso login --profile your-sso-profile
eval "$(aws configure export-credentials --format env)"
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e .
npm install
cd terraform
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
cd ..
wp deploy
```

Apply site changes after editing `src/` or `content/`:

```sh
wp build
wp pdf
wp plan
wp apply
```

Regenerate only the PDF:

```sh
wp pdf
```

Rollback a bad content deploy by reverting the Git commit or checking out the
last known good version, regenerating `resume.pdf` when needed, and running
`wp deploy` again. Use S3 object versions only for short-term object
recovery; Git is the source of truth.

Draft and publish a LinkedIn post locally:

```sh
wp codex e "write linkedin post about idempotency, respond in json"
git status --short
wp publish github --dry-run --pretty
wp publish github --pretty
```

Run the test suite for the content workflow CLI:

```sh
python3 -m pytest tests/
```

## Error Handling

The CLI returns a non-zero exit code when a command fails.

Terraform command failures print the failed command first, then report the exit
code.

PDF generation failures include missing input files, missing Playwright
dependencies, browser errors, timeouts, and empty or missing PDF output files.
