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
  value       = local.custom_domain_enabled ? "https://${local.primary_custom_domain}" : "https://${aws_cloudfront_distribution.site.domain_name}"
}

output "custom_domain_names" {
  description = "Custom domain aliases attached to the CloudFront distribution."
  value       = local.custom_domain_names
}

output "godaddy_dns_records" {
  description = "DNS records to add in GoDaddy for custom domains."
  value       = local.custom_domain_enabled ? local.godaddy_dns_records : {}
}

output "godaddy_dns_note" {
  description = "GoDaddy DNS note for CloudFront custom domains."
  value       = local.custom_domain_enabled ? "Use CNAME records for www-style hostnames. For @ / apex domains, GoDaddy must support ALIAS/ANAME/CNAME flattening to stay on the apex domain; otherwise move DNS hosting to Route 53 or Cloudflare, or redirect the apex to www." : ""
}
