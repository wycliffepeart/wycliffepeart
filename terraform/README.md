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
```

## Deploy

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
