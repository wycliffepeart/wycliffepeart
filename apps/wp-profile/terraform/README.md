# Static Site Deployment

This Terraform configuration deploys the profile site to a private S3 bucket and serves it through CloudFront over HTTPS.

This app lives at `apps/wp-profile` inside the monorepo. Run `cliffe` from the
monorepo root, or use Moon tasks such as `moon run wp-profile:terraform-fmt`
and `moon run wp-profile:terraform-validate` from the monorepo root.

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
cliffe deploy
```

Use direct Terraform commands only for targeted infrastructure operations or
debugging.

```sh
terraform init
terraform plan
terraform apply
```

Terraform uploads:

- `profile.html` as `index.html`
- `profile.html` as `profile.html`
- `resume.html` as `resume.html`
- `blog/index.html` as `blog/index.html`
- `resume.pdf` as `resume.pdf` when `apps/wp-profile/resume.pdf` exists, with
  attachment headers for downloading
- every file under `assets/` under the same `/assets/` path

A CloudFront Function rewrites `/blog` and `/blog/` to `/blog/index.html` so
the blog can use a clean public URL while the private S3 origin still stores an
explicit object key.

The S3 bucket keeps object versions for rollback, and noncurrent object versions
expire after 30 days to keep storage costs bounded.

Generate the PDF before deployment with:

```sh
python3 -m scripts.resume_to_pdf
```

After deployment, use:

```sh
terraform output site_url
```

## Updating The Site

After editing `profile.html` or `resume.html`, run:

```sh
terraform apply
```

CloudFront may cache responses briefly. The HTML objects are uploaded with no-cache headers so browsers should revalidate them.

## Rollback

For a content rollback, revert the bad Git commit or check out the last known
good version, regenerate `resume.pdf` if resume content changed, and run
`cliffe deploy` again. S3 object versioning provides a short recovery window for
individual uploaded objects, but Git remains the source of truth.
