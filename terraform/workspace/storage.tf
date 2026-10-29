# Workspace root bucket (DBFS root, workspace system data). Not versioned, per Databricks guidance.
resource "aws_s3_bucket" "root" {
  bucket        = "${local.prefix}-databricks-root-${data.aws_caller_identity.current.account_id}"
  force_destroy = false

  tags = { Name = "${local.prefix}-databricks-root" }
}

resource "aws_s3_bucket_versioning" "root" {
  bucket = aws_s3_bucket.root.id

  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "root" {
  bucket = aws_s3_bucket.root.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "root" {
  bucket                  = aws_s3_bucket.root.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "databricks_aws_bucket_policy" "root" {
  provider = databricks.mws
  bucket   = aws_s3_bucket.root.bucket
}

resource "aws_s3_bucket_policy" "root" {
  bucket = aws_s3_bucket.root.id
  policy = data.databricks_aws_bucket_policy.root.json

  depends_on = [aws_s3_bucket_public_access_block.root]
}

resource "databricks_mws_storage_configurations" "this" {
  provider = databricks.mws

  account_id                 = var.databricks_account_id
  storage_configuration_name = "${local.prefix}-storage"
  bucket_name                = aws_s3_bucket.root.bucket

  depends_on = [aws_s3_bucket_policy.root]
}
