output "bucket_name" {
  description = "S3 bucket that stores the deployed static assets."
  value       = aws_s3_bucket.site.id
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID."
  value       = aws_cloudfront_distribution.site.id
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name."
  value       = aws_cloudfront_distribution.site.domain_name
}

output "site_url" {
  description = "HTTPS URL for the deployed site."
  value       = var.custom_domain_name != "" && var.acm_certificate_arn != "" ? "https://${var.custom_domain_name}" : "https://${aws_cloudfront_distribution.site.domain_name}"
}

output "custom_domain_name" {
  description = "Custom domain name attached to the CloudFront distribution."
  value       = var.custom_domain_name
}

output "godaddy_dns_record" {
  description = "DNS record to add in GoDaddy for the custom domain."
  value = var.custom_domain_name != "" && var.acm_certificate_arn != "" ? {
    type  = local.godaddy_record_type
    name  = local.godaddy_record_name
    value = aws_cloudfront_distribution.site.domain_name
    ttl   = "1 hour"
  } : null
}

output "godaddy_dns_note" {
  description = "GoDaddy DNS note for CloudFront custom domains."
  value       = var.custom_domain_name != "" && var.acm_certificate_arn != "" ? "If this output says CNAME, add that CNAME in GoDaddy. If it says ALIAS/ANAME or forwarding for @, GoDaddy cannot use a normal CNAME at the apex; use an ALIAS/ANAME-style record if available, or forward the apex domain to a www hostname that has a CNAME to CloudFront." : ""
}
