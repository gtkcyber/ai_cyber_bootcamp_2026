provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = var.tags
  }
}

# Workspace-level provider: Unity Catalog objects, cluster, permissions.
# Auth is the automation service principal via the gtk-workspace profile.
provider "databricks" {
  profile = var.workspace_profile
}

# Account-level provider, only for the student group (identity-federated workspaces
# take account groups, not workspace-local ones).
provider "databricks" {
  alias   = "mws"
  profile = var.account_profile
}
