## Cliffe CLI Documentation

`cliffe` is the project CLI for generating the resume PDF and deploying the
static profile site with Terraform. The CLI entry point is configured in
`pyproject.toml` and points to `scripts.cli:main`.

The deployment creates a private S3 bucket, uploads the site files, and serves
them through CloudFront over HTTPS.

Use `cliffe deploy` as the primary deployment command. Use direct Terraform
commands only for targeted infrastructure operations or debugging.

## Installation

Create and activate a Python virtual environment, then install the package in
editable mode:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e .
```

After installation, the `cliffe` command should be available in the active
environment.

The pip upgrade matters because older pip versions cannot install modern
`pyproject.toml` projects in editable mode without legacy `setup.py` or
`setup.cfg` files.

For local testing without installing the package, run the module directly:

```sh
python3 -m scripts.cli --help
```

Do not run `python3 scripts/cli.py` directly. The CLI imports the `scripts`
package, so it expects the project root to be on Python's import path.

## Prerequisites

- Python 3.9 or newer.
- Terraform installed and available as `terraform`.
- AWS CLI installed and configured.
- An AWS SSO profile or another AWS profile that Terraform can use.
- Google Chrome, Chromium, Microsoft Edge, or another Chromium-based browser for
  PDF generation.

Set up AWS SSO:

```sh
aws configure sso
aws sso login --profile your-sso-profile
```

If you use `aws login`, export the login credentials before running Terraform:

```sh
eval "$(aws configure export-credentials --format env)"
```

Create Terraform variables:

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

For GoDaddy-managed DNS, create an ACM certificate in `us-east-1`, add the ACM
DNS validation CNAME in GoDaddy, wait for the certificate to be issued, then set
`acm_certificate_arn`. After deployment, point the GoDaddy DNS record to the
`godaddy_dns_records` output. Use `www.wycliffepeart.com` for a normal CNAME.
The apex `wycliffepeart.com` must use ALIAS/ANAME/CNAME flattening to stay on
the apex domain; if GoDaddy does not support that, move DNS hosting to Route 53
or Cloudflare, or redirect the apex to `www.wycliffepeart.com`.

Return to the project root before running `cliffe` commands:

```sh
cd ..
```

## Command Overview

```sh
cliffe resume-pdf
cliffe init
cliffe plan
cliffe apply
cliffe deploy
```

Run help for the full command list:

```sh
cliffe --help
```

Run help for a specific command:

```sh
cliffe resume-pdf --help
cliffe deploy --help
```

## `cliffe resume-pdf`

Generates a PDF version of the resume HTML file.

Default behavior:

- Reads `resume.html` from the project root.
- Writes `resume.pdf` to the project root.
- Looks for a Chromium-based browser automatically.
- Uses headless browser printing with `--print-to-pdf`.
- Creates the output directory if it does not already exist.
- Fails if the input file does not exist, no browser is found, the browser exits
  with an error, or the generated PDF is missing or empty.

Basic usage:

```sh
cliffe resume-pdf
```

Equivalent underlying action:

```sh
python3 -m scripts.resume_to_pdf
```

Options:

| Option | Description | Default |
| --- | --- | --- |
| `--input INPUT` | HTML file to render. | `resume.html` |
| `--output OUTPUT` | PDF output path. | `resume.pdf` |
| `--browser BROWSER` | Explicit path to Chrome, Chromium, or Edge. This overrides `CHROME_BIN` and automatic detection. | Auto-detected |
| `--timeout TIMEOUT` | Maximum seconds to wait for PDF generation. | `60` |

Examples:

```sh
cliffe resume-pdf --input resume.html --output resume.pdf
```

```sh
cliffe resume-pdf --browser "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

```sh
cliffe resume-pdf --timeout 120
```

Browser detection order:

1. `CHROME_BIN` environment variable.
2. `google-chrome`.
3. `google-chrome-stable`.
4. `chromium`.
5. `chromium-browser`.
6. `microsoft-edge`.
7. macOS Google Chrome application path.
8. macOS Microsoft Edge application path.
9. macOS Chromium application path.

Use this command before deployment when you want `resume.pdf` uploaded to S3.
Terraform only uploads `resume.pdf` when the file exists in the project root.

## `cliffe init`

Initializes Terraform in the `terraform/` directory.

Default behavior:

- Runs `terraform init`.
- Uses `terraform/` as the working directory.
- Downloads and initializes the Terraform providers declared by the project.
- Prepares the Terraform directory for `plan`, `apply`, and `deploy`.

Basic usage:

```sh
cliffe init
```

Equivalent underlying action:

```sh
cd terraform
terraform init
```

Run this after cloning the project, after changing provider configuration, or
after deleting Terraform's local `.terraform/` directory.

## `cliffe plan`

Creates a Terraform execution plan for the static site infrastructure.

Default behavior:

- Runs `terraform plan`.
- Uses `terraform/` as the working directory.
- Reads variables from `terraform/terraform.tfvars` when present.
- Shows what Terraform will create, update, or destroy.
- Does not make infrastructure changes.

Basic usage:

```sh
cliffe plan
```

Equivalent underlying action:

```sh
cd terraform
terraform plan
```

Options:

| Option | Description |
| --- | --- |
| `--out OUT` | Saves the generated plan to a file. The value is passed to Terraform as `-out OUT`. |

Example:

```sh
cliffe plan --out tfplan
```

The saved plan can be applied later:

```sh
cliffe apply tfplan
```

Use this command when you want to review the deployment changes before applying
them.

## `cliffe apply`

Applies Terraform changes for the static site infrastructure.

Default behavior:

- Runs `terraform apply`.
- Uses `terraform/` as the working directory.
- Prompts for approval unless `--auto-approve` is used or Terraform is applying
  a saved plan file.
- Creates or updates AWS resources.
- Uploads site files declared by Terraform.

Basic usage:

```sh
cliffe apply
```

Equivalent underlying action:

```sh
cd terraform
terraform apply
```

Options and arguments:

| Option or argument | Description |
| --- | --- |
| `--auto-approve` | Passes `-auto-approve` to Terraform so Terraform applies without an interactive confirmation prompt. |
| `plan_file` | Optional Terraform plan file to apply. |

Examples:

```sh
cliffe apply
```

```sh
cliffe apply --auto-approve
```

```sh
cliffe apply tfplan
```

The Terraform configuration uploads:

- `profile.html` as `index.html`.
- `profile.html` as `profile.html`.
- `resume.html` as `resume.html`.
- `resume.pdf` as `resume.pdf` when `resume.pdf` exists in the project root,
  with attachment headers for downloading.
- Every file under `assets/` under the same `/assets/` path.

The S3 bucket keeps object versions for rollback, and noncurrent object versions
expire after 30 days to keep storage costs bounded.

Use `cliffe resume-pdf` before `cliffe apply` if the deployed PDF should be
updated.

## `cliffe deploy`

Runs the full deployment workflow. This is the primary way to deploy the site.

Default behavior:

1. Generates `resume.pdf` from `resume.html`.
2. Runs `terraform init`.
3. Runs `terraform plan`.
4. Runs `terraform apply`.

Basic usage:

```sh
cliffe deploy
```

Options and arguments:

| Option or argument | Description | Default |
| --- | --- | --- |
| `--input INPUT` | HTML file to render into PDF before deployment. | `resume.html` |
| `--output OUTPUT` | PDF output path. | `resume.pdf` |
| `--browser BROWSER` | Explicit path to Chrome, Chromium, or Edge. Overrides `CHROME_BIN` and automatic detection. | Auto-detected |
| `--timeout TIMEOUT` | Maximum seconds to wait for PDF generation. | `60` |
| `--skip-init` | Skips `terraform init`. Use only when Terraform has already been initialized. | Disabled |
| `--out OUT` | Saves the Terraform plan to a file by passing `-out OUT` to `terraform plan`. | No saved plan |
| `--auto-approve` | Passes `-auto-approve` to `terraform apply`. | Disabled |
| `plan_file` | Optional Terraform plan file to apply. | None |

Examples:

```sh
cliffe deploy
```

```sh
cliffe deploy --auto-approve
```

```sh
cliffe deploy --skip-init --auto-approve
```

```sh
cliffe deploy --out tfplan
```

When `--out` is provided and no `plan_file` argument is supplied, `deploy`
automatically applies the plan file it just created.

This command:

```sh
cliffe deploy --out tfplan
```

runs the equivalent of:

```sh
cliffe resume-pdf
cliffe init
cliffe plan --out tfplan
cliffe apply tfplan
```

If both `--out` and `plan_file` are supplied, Terraform creates a new plan at
the `--out` path, but `apply` receives the explicit `plan_file` argument. Prefer
using one or the other to avoid applying a different plan than the one just
created.

Use `deploy` when you want the standard end-to-end path for publishing changes.
Use the individual commands when you want more control or need to inspect a
Terraform plan before applying it.

## Error Handling

The CLI returns a non-zero exit code when a command fails.

Terraform command failures:

- The failed Terraform command is printed before it runs.
- If Terraform exits with an error, the CLI prints:

```text
error: command failed with exit code N
```

PDF generation failures:

- Missing input HTML files fail with a file-not-found error.
- Missing browsers fail with a message asking you to install Chrome/Chromium or
  set `CHROME_BIN`.
- Browser failures include the browser exit code, stdout, and stderr.
- Empty or missing PDF output files are treated as failures.

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
cd terraform
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
cd ..
cliffe deploy
```

Review before applying:

```sh
cliffe resume-pdf
cliffe init
cliffe plan --out tfplan
cliffe apply tfplan
```

Regenerate only the PDF:

```sh
cliffe resume-pdf
```

Apply site changes after editing `profile.html` or `resume.html`:

```sh
cliffe resume-pdf
cliffe plan
cliffe apply
```

Get the deployed site URL after applying:

```sh
cd terraform
terraform output site_url
```

Rollback a bad content deploy by reverting the Git commit or checking out the
last known good version, regenerating `resume.pdf` when needed, and running
`cliffe deploy` again. Use S3 object versions only for short-term object
recovery; Git is the source of truth.

---

> Build it clearly. Ship it carefully. Improve it continuously.
