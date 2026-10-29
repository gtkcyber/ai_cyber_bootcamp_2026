# Course bucket: dataset, catalog storage, rendered decks. Same posture as the workspace root bucket.
resource "aws_s3_bucket" "course" {
  bucket        = local.bucket_name
  force_destroy = false

  tags = { Name = local.bucket_name }
}

resource "aws_s3_bucket_versioning" "course" {
  bucket = aws_s3_bucket.course.id

  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "course" {
  bucket = aws_s3_bucket.course.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "course" {
  bucket                  = aws_s3_bucket.course.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM role that Unity Catalog assumes to reach the bucket. Trust and access policies come
# from the provider's data sources so they track Databricks' current requirements
# (UC master role, external id = account id, self-assumption).
data "databricks_aws_unity_catalog_assume_role_policy" "course" {
  aws_account_id = data.aws_caller_identity.current.account_id
  role_name      = "${local.prefix}-uc-access"
  external_id    = var.databricks_account_id
}

data "databricks_aws_unity_catalog_policy" "course" {
  aws_account_id = data.aws_caller_identity.current.account_id
  bucket_name    = aws_s3_bucket.course.bucket
  role_name      = "${local.prefix}-uc-access"
}

resource "aws_iam_policy" "uc_access" {
  name   = "${local.prefix}-uc-access"
  policy = data.databricks_aws_unity_catalog_policy.course.json
}

resource "aws_iam_role" "uc_access" {
  name               = "${local.prefix}-uc-access"
  assume_role_policy = data.databricks_aws_unity_catalog_assume_role_policy.course.json
}

resource "aws_iam_role_policy_attachment" "uc_access" {
  role       = aws_iam_role.uc_access.name
  policy_arn = aws_iam_policy.uc_access.arn
}

# IAM propagation: Databricks validates the role the moment the credential and the external
# location are created, and a role attached seconds earlier fails that check.
resource "time_sleep" "iam_propagation" {
  create_duration = "30s"

  depends_on = [aws_iam_role_policy_attachment.uc_access]
}

resource "databricks_storage_credential" "course" {
  name    = local.prefix
  comment = "AI Cyber Bootcamp course bucket"

  aws_iam_role {
    role_arn = aws_iam_role.uc_access.arn
  }

  depends_on = [time_sleep.iam_propagation]
}

resource "databricks_external_location" "course" {
  name            = local.prefix
  url             = "s3://${aws_s3_bucket.course.bucket}/"
  credential_name = databricks_storage_credential.course.name
  comment         = "Whole course bucket: catalog storage root and the data volume"

  depends_on = [time_sleep.iam_propagation]
}
