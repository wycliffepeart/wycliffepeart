# Static Site Deployment

This Terraform configuration deploys the profile site to a private S3 bucket and serves it through CloudFront over HTTPS.

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
aws_profile      = "your-sso-profile"
site_bucket_name = "wycliffepeart-profile-site-your-account-id"
custom_domain_name = "wycliffepeart.com"
acm_certificate_arn = "arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERTIFICATE_ID"
```

For GoDaddy-managed DNS, create an ACM certificate in `us-east-1`, add the ACM
DNS validation CNAME in GoDaddy, wait for the certificate to be issued, then set
`acm_certificate_arn`. After deployment, point the GoDaddy DNS record to the
`godaddy_dns_record` output. Use `www.wycliffepeart.com` for a normal CNAME; the
apex `wycliffepeart.com` usually needs GoDaddy forwarding or an ALIAS/ANAME
feature if available. The `godaddy_dns_note` output calls this out when relevant.

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
- `resume.pdf` as `resume.pdf` when that file exists in the project root

Generate the PDF before deployment with:

```sh
python3 ../scripts/resume_to_pdf.py
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
