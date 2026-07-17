# Agent Instructions

This repository contains Wycliffe Peart's GitHub profile content, a static profile
site, a resume HTML/PDF workflow, a small Python CLI, and Terraform deployment
configuration for S3 plus CloudFront.

## Default Workflow

- Commit changes after each completed change when the user has asked for project
  edits. Use descriptive commit messages that clearly match the change being
  committed, and include a concise commit description that explains what changed.
- Before editing, check `git status --short` and do not overwrite unrelated user
  changes. If a file already has user edits, work with the current contents.
- Keep changes scoped to the requested area. Do not reformat large HTML,
  Terraform, or generated files unless formatting is part of the task.
- Prefer `rg` and `rg --files` for project searches.
- Use ASCII for new text unless the target file already uses non-ASCII content
  for a clear reason.

## Project Files

- `README.md` is the GitHub profile README. Only update it when resume/profile
  content changes require the public GitHub profile text to change. Do not update
  it for unrelated styling, infrastructure, CLI, or deployment changes unless the
  user explicitly asks.
- `profile.html` is the deployed profile site's primary page. Terraform uploads
  it as both `index.html` and `profile.html`.
- `resume.html` is the source of the browser-rendered resume.
- `resume.pdf` is generated output from `resume.html`. Do not hand-edit it.
- `scripts/resume_to_pdf.py` converts `resume.html` to `resume.pdf` with a
  Chromium-based browser.
- `scripts/cli.py` provides the `cliffe` CLI for PDF generation and Terraform
  commands.
- `docs.md` documents CLI and non-resume project workflows. Update it for CLI,
  infrastructure, deployment, or other non-resume behavior changes that need
  documentation.
- `terraform/README.md` documents Terraform-specific deployment steps. Update it
  when Terraform behavior, uploaded files, or deployment prerequisites change.

## Resume PDF Rules

- Keep the default PDF output filename in `scripts/resume_to_pdf.py` synchronized
  with Terraform's upload key in `terraform/main.tf`.
- The current invariant is:
  - `scripts/resume_to_pdf.py` `DEFAULT_OUTPUT` -> project-root `resume.pdf`
  - `terraform/main.tf` `local.optional_files` uploads project-root
    `resume.pdf` as S3 object key `resume.pdf`
- If the generated PDF filename or location changes, update all references in
  `scripts/resume_to_pdf.py`, `scripts/cli.py`, `docs.md`,
  `terraform/main.tf`, `terraform/README.md`, and any profile download links.
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
  - `cliffe resume-pdf`
  - `python3 -m scripts.resume_to_pdf`
- `resume_to_pdf.py` requires Chrome, Chromium, Edge, or `CHROME_BIN` pointing to
  a Chromium-based browser.
- If touching Python code, run the relevant command help or targeted command when
  possible, for example `python3 -m scripts.cli --help`.

## Terraform And Deployment Rules

- Terraform lives in `terraform/` and should be run with that directory as the
  working directory unless using the `cliffe` wrapper.
- Terraform deploys a private S3 bucket with public access blocked, S3
  versioning, AES256 server-side encryption, CloudFront Origin Access Control,
  and a CloudFront distribution using the default CloudFront certificate.
- Terraform uploads:
  - `profile.html` as `index.html`
  - `profile.html` as `profile.html`
  - `resume.html` as `resume.html`
  - `resume.pdf` as `resume.pdf` only when project-root `resume.pdf` exists
- HTML objects use no-cache headers. Other uploaded assets, including PDFs, use
  long immutable caching by default.
- Keep `terraform/main.tf` `local.html_files`, `local.optional_files`,
  `local.content_types`, and cache-control behavior synchronized with any new
  deployed asset types.
- Do not commit `terraform/terraform.tfvars`, Terraform state files, plan files,
  AWS credentials, or generated provider directories.
- For deployment changes, validate with `terraform fmt` and `terraform validate`
  when Terraform is initialized. If validation cannot run because providers or
  credentials are unavailable, report that clearly.
- Use AWS SSO or an existing AWS profile. Do not add static AWS access keys to
  the repository.

## Documentation Rules

- Resume/profile content changes may require updates across `README.md`,
  `profile.html`, `resume.html`, and regenerated `resume.pdf`.
- CLI, PDF workflow, Terraform, or deployment behavior changes may require
  updates to `docs.md` and `terraform/README.md`.
- Keep command examples consistent with the supported entry points in
  `pyproject.toml`: `cliffe` and `resume-to-pdf`.

## Verification Checklist

- For profile or resume HTML changes, inspect the affected HTML for broken links,
  inconsistent visible content, and stale PDF/download references.
- For resume PDF workflow changes, run PDF generation if a Chromium-based browser
  is available.
- For CLI changes, run `python3 -m scripts.cli --help` and any affected
  subcommand help.
- For Terraform changes, run `terraform fmt` and `terraform validate` from
  `terraform/` when possible.
- Before finishing, run `git status --short` and summarize changed files,
  generated files, and any checks that could not be completed.
