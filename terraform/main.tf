locals {
  # out/ is the Next.js static export produced by `wp build` (next.config.ts
  # sets output: "export", trailingSlash: true). scripts/site_build.py
  # additionally copies index.html -> profile.html (legacy duplicate key)
  # and flattens resume/index.html -> resume.html to match the site's own
  # relative links, and copies workspace/resume.pdf in as resume.pdf. Run
  # `wp build` (or `wp deploy`, which does this automatically) before
  # `terraform plan`/`apply`.
  #
  # Blog posts are native Next.js MDX pages (content/blog/*.mdx), so every
  # post's out/blog/<slug>/index.html is already part of this export - no
  # separate content merge step, and no Terraform change needed to deploy a
  # new post.
  source_root = abspath("${path.module}/../out")

  configured_custom_domains = length(var.custom_domain_names) > 0 ? var.custom_domain_names : compact([var.custom_domain_name])
  custom_domain_names       = distinct(local.configured_custom_domains)
  primary_custom_domain     = length(local.custom_domain_names) > 0 ? local.custom_domain_names[0] : ""
  custom_domain_enabled     = length(local.custom_domain_names) > 0 && var.acm_certificate_arn != ""

  godaddy_dns_records = {
    for domain in local.custom_domain_names : domain => {
      type  = length(split(".", domain)) == 2 ? "ALIAS/ANAME/CNAME flattening" : "CNAME"
      name  = length(split(".", domain)) == 2 ? "@" : split(".", domain)[0]
      value = aws_cloudfront_distribution.site.domain_name
      ttl   = "1 hour"
    }
  }

  # `next build` also writes RSC prefetch payload files (*.txt, __next.*)
  # alongside each route's index.html, plus /404 and /_not-found export
  # artifacts. This site hard-navigates with plain <a> tags instead of
  # next/link, so those payloads are never fetched by the browser and are
  # deliberately excluded here - only HTML documents, the Next.js JS/CSS
  # chunks, and known top-level files are deployed.
  all_output_files = fileset(local.source_root, "**")

  deployable_files = toset([
    for f in local.all_output_files : f
    if(
      (
        endswith(f, ".html") ||
        startswith(f, "_next/") ||
        startswith(f, "assets/") ||
        f == "favicon.ico" ||
        f == "resume.pdf"
      ) &&
      !startswith(f, "404/") &&
      !startswith(f, "_not-found/")
    )
  ])

  site_files = {
    for f in local.deployable_files : f => "${local.source_root}/${f}"
  }

  # HTML documents change on every deploy and must never be served stale.
  # Everything else (content-hashed _next/ chunks, images, the resume PDF)
  # is safe to cache immutably.
  html_keys = toset([for f in local.deployable_files : f if endswith(f, ".html")])

  content_dispositions = {
    "resume.pdf" = "attachment; filename=\"Wycliffe-Peart-Resume.pdf\""
  }

  content_types = {
    html = "text/html; charset=utf-8"
    css  = "text/css; charset=utf-8"
    js   = "application/javascript; charset=utf-8"
    json = "application/json; charset=utf-8"
    md   = "text/markdown; charset=utf-8"
    txt  = "text/plain; charset=utf-8"
    pdf  = "application/pdf"
    png  = "image/png"
    jpg  = "image/jpeg"
    jpeg = "image/jpeg"
    webp = "image/webp"
    svg  = "image/svg+xml"
    ico  = "image/x-icon"
  }
}

resource "aws_s3_bucket" "site" {
  bucket = var.site_bucket_name
}

resource "aws_s3_bucket_public_access_block" "site" {
  bucket = aws_s3_bucket.site.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "site" {
  bucket = aws_s3_bucket.site.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_versioning" "site" {
  bucket = aws_s3_bucket.site.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "site" {
  bucket = aws_s3_bucket.site.id

  rule {
    id     = "expire-old-site-versions"
    status = "Enabled"

    filter {
      prefix = ""
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  depends_on = [
    aws_s3_bucket_versioning.site
  ]
}

resource "aws_s3_bucket_server_side_encryption_configuration" "site" {
  bucket = aws_s3_bucket.site.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_object" "site_files" {
  for_each = local.site_files

  bucket              = aws_s3_bucket.site.id
  key                 = each.key
  source              = each.value
  etag                = filemd5(each.value)
  content_type        = lookup(local.content_types, lower(regex("[^.]+$", each.key)), "application/octet-stream")
  content_disposition = lookup(local.content_dispositions, each.key, null)
  cache_control = contains(local.html_keys, each.key) ? (
    "no-cache, no-store, must-revalidate"
  ) : "public, max-age=31536000, immutable"

  depends_on = [
    aws_s3_bucket_ownership_controls.site,
    aws_s3_bucket_public_access_block.site
  ]
}

resource "aws_cloudfront_origin_access_control" "site" {
  name                              = "${var.site_bucket_name}-oac"
  description                       = "Origin access control for ${var.site_bucket_name}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_response_headers_policy" "site_security" {
  name    = "${var.site_bucket_name}-security-headers"
  comment = "Security headers for the profile site"

  security_headers_config {
    content_type_options {
      override = true
    }

    frame_options {
      frame_option = "DENY"
      override     = true
    }

    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }

    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      preload                    = false
      override                   = true
    }

    xss_protection {
      mode_block = true
      protection = true
      override   = true
    }
  }
}

resource "aws_cloudfront_function" "directory_index_rewrite" {
  name    = "${var.site_bucket_name}-directory-index-rewrite"
  runtime = "cloudfront-js-2.0"
  comment = "Append index.html to directory-style requests (every route, including blog posts)"
  publish = true
  code    = <<-EOT
function handler(event) {
  var request = event.request;
  var uri = request.uri;

  if (uri.endsWith("/")) {
    request.uri = uri + "index.html";
  } else if (!uri.includes(".")) {
    request.uri = uri + "/index.html";
  }

  return request;
}
EOT
}

resource "aws_cloudfront_distribution" "site" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Developer profile static site"
  default_root_object = var.default_root_object
  price_class         = "PriceClass_100"
  aliases             = local.custom_domain_enabled ? local.custom_domain_names : []

  origin {
    domain_name              = aws_s3_bucket.site.bucket_regional_domain_name
    origin_id                = "s3-${aws_s3_bucket.site.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.site.id
  }

  default_cache_behavior {
    target_origin_id           = "s3-${aws_s3_bucket.site.id}"
    viewer_protocol_policy     = "redirect-to-https"
    allowed_methods            = ["GET", "HEAD", "OPTIONS"]
    cached_methods             = ["GET", "HEAD"]
    compress                   = true
    response_headers_policy_id = aws_cloudfront_response_headers_policy.site_security.id

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.directory_index_rewrite.arn
    }

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
  }

  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = local.custom_domain_enabled ? false : true
    acm_certificate_arn            = local.custom_domain_enabled ? var.acm_certificate_arn : null
    ssl_support_method             = local.custom_domain_enabled ? "sni-only" : null
    minimum_protocol_version       = local.custom_domain_enabled ? "TLSv1.2_2021" : null
  }
}

data "aws_iam_policy_document" "site" {
  statement {
    sid     = "AllowCloudFrontRead"
    effect  = "Allow"
    actions = ["s3:GetObject"]

    resources = [
      "${aws_s3_bucket.site.arn}/*"
    ]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.site.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "site" {
  bucket = aws_s3_bucket.site.id
  policy = data.aws_iam_policy_document.site.json

  depends_on = [
    aws_s3_bucket_public_access_block.site
  ]
}
