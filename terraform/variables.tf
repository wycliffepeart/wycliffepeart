variable "aws_region" {
  description = "AWS region for S3. CloudFront remains global."
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile name. Use an AWS SSO-backed profile for local deployments."
  type        = string
  default     = ""
}

variable "site_bucket_name" {
  description = "Globally unique S3 bucket name for the static site."
  type        = string
}

variable "custom_domain_name" {
  description = "Optional custom domain name for the CloudFront distribution, such as wycliffepeart.com."
  type        = string
  default     = ""
}

variable "acm_certificate_arn" {
  description = "Optional issued ACM certificate ARN in us-east-1 for custom_domain_name."
  type        = string
  default     = ""
}

variable "default_root_object" {
  description = "CloudFront default root object."
  type        = string
  default     = "index.html"
}

variable "default_tags" {
  description = "Default tags applied to supported AWS resources."
  type        = map(string)
  default = {
    Project     = "wycliffepeart-profile"
    ManagedBy   = "terraform"
    Application = "developer-profile"
  }
}
