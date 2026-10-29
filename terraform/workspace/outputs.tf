output "workspace_url" {
  value = databricks_mws_workspaces.this.workspace_url
}

output "workspace_id" {
  value = databricks_mws_workspaces.this.workspace_id
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnets
}

output "security_group_id" {
  value = aws_security_group.databricks.id
}

output "cross_account_role_arn" {
  value = aws_iam_role.cross_account.arn
}

output "root_bucket" {
  value = aws_s3_bucket.root.bucket
}
