provider "aws" {
  region  = var.aws_region
  profile = "gtk-cyber"

  default_tags {
    tags = var.tags
  }
}

# Workspace-level provider: Unity Catalog objects, cluster, permissions.
# Auth is the automation service principal via the gtk-workspace profile.
provider "databricks" {
  profile = "gtk-workspace"
}

# Account-level provider, only for the student group (identity-federated workspaces
# take account groups, not workspace-local ones).
provider "databricks" {
  alias   = "mws"
  profile = "gtk-account"
}
