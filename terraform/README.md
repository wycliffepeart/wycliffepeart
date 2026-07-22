# Static Site Deployment

This Terraform configuration deploys the profile site to a private S3 bucket and serves it through CloudFront over HTTPS.

The site is a Next.js app at the project root, built as a static export by
`wp build` (`next build`, since `next.config.ts` sets `output: "export"`).
Terraform uploads from the build output at `out/`, so run `wp build` (or
`wp deploy`, which does this automatically) before `terraform plan`/`apply`
when using Terraform directly. Run `wp` from the project root. Run direct
Terraform commands from this `terraform` directory.

## AWS SSO Setup

Use an AWS SSO-backed CLI profile. No access keys are required.

```sh
aws configure sso
aws sso login --profile your-sso-profile
```

Copy the example variables file and set a globally unique bucket name:

```sh
cp terraform.tfvars.example terraform.tfvars
```

Update:

```hcl
aws_profile         = "your-sso-profile"
site_bucket_name    = "wycliffepeart-profile-site-your-account-id"
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

## Deploy

The primary deployment path is the project CLI:

```sh
wp deploy
```

Use direct Terraform commands only for targeted infrastructure operations or
debugging. Run `wp build` first so `out/` is up to date.

```sh
wp build
terraform init
terraform plan
terraform apply
```

Terraform uploads every HTML document, `_next/` chunk, and `assets/` file from
`out/`, plus the top-level `favicon.ico` and `resume.pdf` when present. Next's
RSC prefetch payload files (`*.txt`, `__next.*`) and the `/404` and
`/_not-found` export artifacts are excluded - this site hard-navigates with
plain `<a>` tags instead of `next/link`, so the browser never fetches those
payloads. Because the selection is a filter over the whole export rather than
a hand-picked file list, adding a new MDX blog post under `content/blog/` and
running `wp deploy` is enough to publish it - no Terraform changes needed.

HTML documents are uploaded with no-cache headers so browsers always
revalidate them; everything else (content-hashed `_next/` chunks, images, the
resume PDF) is cached immutably.

A CloudFront Function rewrites any directory-style request (for example `/`,
`/blog`, `/blog/`, or `/blog/sql-joins/`) to its `index.html` object, so every
route - including per-post blog pages - can use a clean public URL while the
private S3 origin still stores an explicit object key.

The S3 bucket keeps object versions for rollback, and noncurrent object versions
expire after 30 days to keep storage costs bounded.

Generate the PDF before deployment with:

```sh
wp pdf
```

After deployment, use:

```sh
terraform output site_url
```

## Updating The Site

After editing the site under `src/`, run:

```sh
wp build
terraform apply
```

CloudFront may cache responses briefly. The HTML objects are uploaded with no-cache headers so browsers should revalidate them.

## Rollback

For a content rollback, revert the bad Git commit or check out the last known
good version, regenerate `resume.pdf` if resume content changed, and run
`wp deploy` again. S3 object versioning provides a short recovery window for
individual uploaded objects, but Git remains the source of truth.
