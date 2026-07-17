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

