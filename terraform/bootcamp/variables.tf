variable "aws_region" {
  description = "Region for the course bucket. Must match the workspace region."
  type        = string
}

variable "databricks_account_id" {
  description = "Databricks account id; external id on the storage credential's IAM role."
  type        = string
}

variable "workspace_id" {
  description = "Numeric id of the workspace, for the group's workspace assignment."
  type        = number
}

variable "catalog_name" {
  type    = string
  default = "ai_cyber_bootcamp"
}

variable "schema_name" {
  type    = string
  default = "course"
}

variable "student_group" {
  description = "Account group that holds the students. Created empty; membership is managed later."
  type        = string
  default     = "bh_india_2026_students"
}

variable "admin_group" {
  description = "Account group of course administrators: CAN_MANAGE on the cluster."
  type        = string
  default     = "bh_india_2026_admins"
}

variable "admin_users" {
  description = "Human members of the admin group (emails)."
  type        = list(string)
  default     = ["admin1@example.com", "admin2@example.com", "admin3@example.com"]
}

variable "automation_service_principal" {
  description = "Service principal that runs deploys and test jobs; member of the admin group."
  type        = string
  default     = "<YOUR_AUTOMATION_SERVICE_PRINCIPAL>"
}

variable "cluster_name" {
  type    = string
  default = "bootcamp-labs"
}

variable "gpu_cluster_name" {
  type    = string
  default = "bootcamp-gpu"
}

variable "labs_b_cluster_name" {
  description = "Second labs cluster, same shape as bootcamp-labs, for splitting the class."
  type        = string
  default     = "bootcamp-labs-2"
}

variable "gpu_node_type_id" {
  description = "Single-GPU node for the deep-learning modules. g4dn.xlarge is the cheapest the workspace offers."
  type        = string
  default     = "g4dn.xlarge"
}

variable "gpu_cluster_pypi_packages" {
  description = "PyPI packages installed on the GPU cluster on top of the GPU ML runtime. Modules 7 to 9 import art (7.1, 7.2), which the runtime does not ship."
  type        = list(string)
  default     = ["adversarial-robustness-toolbox"]
}

variable "autotermination_minutes" {
  type    = number
  default = 20
}

variable "cluster_pypi_packages" {
  description = "PyPI packages installed on the cluster on top of the ML runtime."
  type        = list(string)
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "aws_profile" {
  description = "AWS CLI profile for the state bucket and course bucket"
  type        = string
}

variable "workspace_profile" {
  description = "Databricks CLI profile for the workspace (service principal)"
  type        = string
}

variable "account_profile" {
  description = "Databricks CLI profile for the account (service principal)"
  type        = string
}

variable "prefix" {
  description = "Name prefix for AWS resources, e.g. your-course-bootcamp"
  type        = string
}
