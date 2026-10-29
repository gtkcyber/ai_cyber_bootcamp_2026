data "aws_caller_identity" "current" {}

locals {
  prefix      = var.prefix
  bucket_name = "${local.prefix}-${data.aws_caller_identity.current.account_id}"
}
