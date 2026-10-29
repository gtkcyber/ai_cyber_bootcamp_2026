resource "databricks_group" "students" {
  provider     = databricks.mws
  display_name = var.student_group
}

resource "databricks_mws_permission_assignment" "students" {
  provider     = databricks.mws
  workspace_id = var.workspace_id
  principal_id = databricks_group.students.id
  permissions  = ["USER"]
}

# One resource per grant so nothing here replaces the owner's implicit privileges.
resource "databricks_grant" "students_catalog" {
  catalog    = databricks_catalog.course.name
  principal  = databricks_group.students.display_name
  privileges = ["USE_CATALOG"]

  depends_on = [databricks_mws_permission_assignment.students]
}

resource "databricks_grant" "students_schema" {
  schema     = "${databricks_catalog.course.name}.${databricks_schema.course.name}"
  principal  = databricks_group.students.display_name
  privileges = ["USE_SCHEMA"]

  depends_on = [databricks_mws_permission_assignment.students]
}

resource "databricks_grant" "students_data" {
  volume     = "${databricks_catalog.course.name}.${databricks_schema.course.name}.${databricks_volume.data.name}"
  principal  = databricks_group.students.display_name
  privileges = ["READ_VOLUME"]

  depends_on = [databricks_mws_permission_assignment.students]
}

# Cluster log delivery runs as the single-user principal (the students group) and fails
# without READ on the logs volume: "PERMISSION_DENIED ... READ VOLUME on ... course.logs".
resource "databricks_grant" "students_logs" {
  volume     = "${databricks_catalog.course.name}.${databricks_schema.course.name}.${databricks_volume.logs.name}"
  principal  = databricks_group.students.display_name
  privileges = ["READ_VOLUME", "WRITE_VOLUME"]

  depends_on = [databricks_mws_permission_assignment.students]
}

# Students attach to a running cluster; only admins start, restart or edit one. The same
# grant on every course cluster.
resource "databricks_permissions" "clusters" {
  for_each   = { labs = databricks_cluster.labs.id, labs_b = databricks_cluster.labs_b.id, gpu = databricks_cluster.gpu.id }
  cluster_id = each.value

  access_control {
    group_name       = databricks_group.students.display_name
    permission_level = "CAN_ATTACH_TO"
  }

  access_control {
    group_name       = databricks_group.admins.display_name
    permission_level = "CAN_MANAGE"
  }

  depends_on = [databricks_mws_permission_assignment.students, databricks_mws_permission_assignment.admins]
}

# Course administrators: manage the cluster, and later the roster.
resource "databricks_group" "admins" {
  provider     = databricks.mws
  display_name = var.admin_group
}

resource "databricks_mws_permission_assignment" "admins" {
  provider     = databricks.mws
  workspace_id = var.workspace_id
  principal_id = databricks_group.admins.id
  permissions  = ["USER"]
}

data "databricks_user" "admins" {
  provider  = databricks.mws
  for_each  = toset(var.admin_users)
  user_name = each.value
}

data "databricks_service_principal" "automation" {
  provider     = databricks.mws
  display_name = var.automation_service_principal
}

resource "databricks_group_member" "admin_users" {
  provider  = databricks.mws
  for_each  = data.databricks_user.admins
  group_id  = databricks_group.admins.id
  member_id = each.value.id
}

resource "databricks_group_member" "admin_automation" {
  provider  = databricks.mws
  group_id  = databricks_group.admins.id
  member_id = data.databricks_service_principal.automation.id
}
