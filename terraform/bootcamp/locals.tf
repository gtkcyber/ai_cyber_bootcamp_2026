data "aws_caller_identity" "current" {}

locals {
  prefix      = "gtk-cyber-bootcamp"
  bucket_name = "${local.prefix}-${data.aws_caller_identity.current.account_id}"
}
