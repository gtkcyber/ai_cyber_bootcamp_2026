resource "databricks_mws_workspaces" "this" {
  provider = databricks.mws

  account_id      = var.databricks_account_id
  workspace_name  = var.workspace_name
  deployment_name = var.deployment_name
  aws_region      = var.aws_region

  credentials_id           = databricks_mws_credentials.this.credentials_id
  storage_configuration_id = databricks_mws_storage_configurations.this.storage_configuration_id
  network_id               = databricks_mws_networks.this.network_id

  timeouts {
    create = "30m"
  }

  depends_on = [time_sleep.iam_propagation]
}

resource "databricks_metastore_assignment" "this" {
  provider = databricks.mws

  workspace_id = databricks_mws_workspaces.this.workspace_id
  metastore_id = var.metastore_id
}
