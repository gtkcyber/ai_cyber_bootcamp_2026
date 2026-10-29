variable "databricks_account_id" {
  description = "Databricks account ID (top-right of the account console)."
  type        = string
}

variable "aws_region" {
  description = "AWS region for the VPC, root bucket, and workspace."
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR. Databricks requires /16 to /25; the two private subnets are carved as /19s."
  type        = string
}

variable "workspace_name" {
  description = "Workspace display name in the account console and UI."
  type        = string
}

variable "deployment_name" {
  description = "Workspace subdomain: https://<prefix>-<deployment_name>.cloud.databricks.com. Requires a deployment-name prefix on the Databricks account; null takes Databricks' default URL. Changing it replaces the workspace."
  type        = string
  default     = null
}

variable "metastore_id" {
  description = "Unity Catalog metastore to assign to the workspace (must be in aws_region)."
  type        = string
}

variable "account_admins" {
  description = "Existing Databricks account users made account admins and workspace admins."
  type        = list(string)
}

variable "automation_service_principal" {
  description = "Display name of the account-admin service principal that runs Terraform and the CLI; it becomes a workspace admin too."
  type        = string
}

variable "enable_interface_endpoints" {
  description = "Create STS and Kinesis interface VPC endpoints (Databricks-recommended, ~USD 7/month each plus data). Off until classic compute traffic justifies it."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags applied to every AWS resource."
  type        = map(string)
  default     = {}
}
