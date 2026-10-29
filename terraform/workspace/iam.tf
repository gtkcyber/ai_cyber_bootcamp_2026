# Cross-account role Databricks assumes to run classic compute in this account.
data "databricks_aws_assume_role_policy" "this" {
  provider    = databricks.mws
  external_id = var.databricks_account_id
}

data "databricks_aws_crossaccount_policy" "this" {
  provider    = databricks.mws
  policy_type = "customer"
}

resource "aws_iam_role" "cross_account" {
  name               = "${local.prefix}-databricks-crossaccount"
  assume_role_policy = data.databricks_aws_assume_role_policy.this.json
}

resource "aws_iam_role_policy" "cross_account" {
  name   = "${local.prefix}-databricks-crossaccount"
  role   = aws_iam_role.cross_account.id
  policy = data.databricks_aws_crossaccount_policy.this.json
}

# IAM is eventually consistent; Databricks validates the role at credential and workspace creation.
resource "time_sleep" "iam_propagation" {
  depends_on      = [aws_iam_role_policy.cross_account]
  create_duration = "20s"
}

resource "databricks_mws_credentials" "this" {
  provider = databricks.mws

  credentials_name = "${local.prefix}-credentials"
  role_arn         = aws_iam_role.cross_account.arn

  depends_on = [time_sleep.iam_propagation]
}
