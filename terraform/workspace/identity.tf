# Admins already exist as account users; Terraform manages their roles and workspace access, not the users.
data "databricks_user" "admins" {
  for_each = toset(var.account_admins)
  provider = databricks.mws

  user_name = each.value
}

resource "databricks_user_role" "account_admin" {
  for_each = data.databricks_user.admins
  provider = databricks.mws

  user_id = each.value.id
  role    = "account_admin"
}

resource "databricks_mws_permission_assignment" "admins" {
  for_each = data.databricks_user.admins
  provider = databricks.mws

  workspace_id = databricks_mws_workspaces.this.workspace_id
  principal_id = each.value.id
  permissions  = ["ADMIN"]

  depends_on = [databricks_metastore_assignment.this]
}

data "databricks_service_principal" "automation" {
  provider = databricks.mws

  display_name = var.automation_service_principal
}

resource "databricks_mws_permission_assignment" "automation" {
  provider = databricks.mws

  workspace_id = databricks_mws_workspaces.this.workspace_id
  principal_id = data.databricks_service_principal.automation.id
  permissions  = ["ADMIN"]

  depends_on = [databricks_metastore_assignment.this]
}
