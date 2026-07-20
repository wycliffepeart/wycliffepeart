# Agent Instructions

This repository is a Moon-managed profile project. The root `README.md` is the
public profile and must reflect the profile details maintained in
`apps/wp-profile`. The `apps/wp-profile` project contains Wycliffe Peart's
GitHub profile content, a static profile site, a resume HTML/PDF workflow, a
small Python CLI, and Terraform deployment configuration for S3 plus
CloudFront.

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

- Root `README.md` is the public profile README. Only update it with profile
  details from `apps/wp-profile`; do not use it for monorepo, Moon,
  infrastructure, CLI, or deployment documentation.
- `.moon/workspace.yml` discovers projects under `apps/*`.
- `apps/wp-profile/README.md` is the GitHub profile README. Only update it when
  resume/profile content changes require the public GitHub profile text to
  change. Do not update it for unrelated styling, infrastructure, CLI, or
  deployment changes unless the user explicitly asks.
- `apps/wp-profile/index.html` is the deployed profile site's primary page.
  Terraform uploads it as both `index.html` and `profile.html`.
- `apps/wp-profile/resume.html` is the source of the browser-rendered resume.
- `apps/wp-profile/resume.pdf` is generated output from `resume.html`. Do not
  hand-edit it.
- `apps/wp-profile/scripts/resume_to_pdf.py` converts
  `apps/wp-profile/resume.html` to `apps/wp-profile/resume.pdf` with a
  Chromium-based browser.
- Root `scripts/cli.py` provides the `cliffe` CLI for PDF generation and
  Terraform commands targeting `apps/wp-profile`.
- `apps/wp-profile/docs.md` documents CLI and non-resume project workflows.
  Update it for CLI, infrastructure, deployment, or other non-resume behavior
  changes that need documentation.
- `apps/wp-profile/terraform/README.md` documents Terraform-specific deployment
  steps. Update it when Terraform behavior, uploaded files, or deployment
  prerequisites change.

## Resume PDF Rules

- Keep the default PDF output filename in
  `apps/wp-profile/scripts/resume_to_pdf.py` synchronized with Terraform's
  upload key in
  `apps/wp-profile/terraform/main.tf`.
- The current invariant is:
  - `apps/wp-profile/scripts/resume_to_pdf.py` `DEFAULT_OUTPUT` ->
    `apps/wp-profile/resume.pdf`
  - `apps/wp-profile/terraform/main.tf` `local.optional_files` uploads
    `apps/wp-profile/resume.pdf` as S3 object key `resume.pdf`
- If the generated PDF filename or location changes, update all references in
  `apps/wp-profile/scripts/resume_to_pdf.py`, `scripts/cli.py`,
  `apps/wp-profile/docs.md`, `apps/wp-profile/terraform/main.tf`,
  `apps/wp-profile/terraform/README.md`, and any profile download links.
- Generate `resume.pdf` before deployment whenever `resume.html` has changed and
  the deployed PDF should reflect the latest resume.
- Do not commit a stale `resume.pdf` after changing `resume.html`. Regenerate it
  or clearly report that PDF generation could not be run.

## CLI And Local Commands

- Install locally with:
  `python3 -m pip install -e .`
- Use the package/module entry points instead of running `scripts/cli.py`
  directly:
  - `python3 -m scripts.cli --help`
  - `cliffe --help`
- Generate the resume PDF with one of:
  - `moon run wp-profile:resume-pdf`
  - `cliffe resume-pdf`
  - `resume-to-pdf`
  - `python3 apps/wp-profile/scripts/resume_to_pdf.py`
- Run the static profile locally with `moon run wp-profile:run`.
- `resume_to_pdf.py` requires Chrome, Chromium, Edge, or `CHROME_BIN` pointing to
  a Chromium-based browser.
- If touching Python code, run the relevant command help or targeted command when
  possible, for example `python3 -m scripts.cli --help`.

## Terraform And Deployment Rules

- Use root `cliffe deploy` as the primary deployment path. It regenerates
  `apps/wp-profile/resume.pdf`, runs Terraform init/plan/apply from the correct
  directory, and keeps the PDF plus infrastructure workflow together. Use direct
  Terraform commands only for targeted infrastructure operations, debugging, or
  when the user explicitly asks for Terraform commands.
- Terraform lives in `apps/wp-profile/terraform/` and should be run with that
  directory as the working directory unless using the `cliffe` wrapper.
- Do not add Route 53 hosted zones, Route 53 records, or DNS-provider automation
  unless the user explicitly asks for DNS to be managed in Terraform. The
  current domain workflow assumes DNS remains at GoDaddy and Terraform only
  attaches an already-issued ACM certificate to CloudFront.
- Terraform deploys a private S3 bucket with public access blocked, S3
  versioning, AES256 server-side encryption, CloudFront Origin Access Control,
  and a CloudFront distribution using either the default CloudFront certificate
  or a supplied ACM certificate ARN for a custom domain.
- Terraform uploads:
  - `index.html` as `index.html`
  - `index.html` as `profile.html`
  - `resume.html` as `resume.html`
  - `blog/index.html` as `blog/index.html`
  - `resume.pdf` as `resume.pdf` only when `apps/wp-profile/resume.pdf` exists
  - clean `/blog` and `/blog/` requests are rewritten to `/blog/index.html`
    by a CloudFront Function
- HTML objects use no-cache headers. Other uploaded assets, including PDFs, use
  long immutable caching by default.
- Keep `apps/wp-profile/terraform/main.tf` `local.html_files`,
  `local.optional_files`, `local.content_types`, and cache-control behavior
  synchronized with any new deployed asset types.
- Do not commit `apps/wp-profile/terraform/terraform.tfvars`, Terraform state
  files, plan files, AWS credentials, or generated provider directories.
- For deployment changes, validate with `terraform fmt` and `terraform validate`
  when Terraform is initialized. If validation cannot run because providers or
  credentials are unavailable, report that clearly.
- Use AWS SSO or an existing AWS profile. Do not add static AWS access keys to
  the repository.

## Documentation Rules

- Resume/profile content changes may require updates across root `README.md`,
  `apps/wp-profile/README.md`, `apps/wp-profile/index.html`,
  `apps/wp-profile/resume.html`, and regenerated `apps/wp-profile/resume.pdf`.
  Keep root `README.md` aligned with profile details from `apps/wp-profile`.
- CLI, PDF workflow, Terraform, or deployment behavior changes may require
  updates to `apps/wp-profile/docs.md` and
  `apps/wp-profile/terraform/README.md`.
- Keep command examples consistent with the supported entry points in
  `pyproject.toml`: `cliffe` and `resume-to-pdf`.

## Verification Checklist

- For profile or resume HTML changes, inspect the affected HTML for broken links,
  inconsistent visible content, and stale PDF/download references.
- For resume PDF workflow changes, run PDF generation if a Chromium-based browser
  is available.
- For CLI changes, run `python3 -m scripts.cli --help` and any affected
  subcommand help.
- For Terraform changes, run `moon run wp-profile:terraform-fmt` and
  `moon run wp-profile:terraform-validate` when possible, or run Terraform from
  `apps/wp-profile/terraform/`.
- Before finishing, run `git status --short` and summarize changed files,
  generated files, and any checks that could not be completed.
