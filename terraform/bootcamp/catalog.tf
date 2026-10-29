resource "databricks_catalog" "course" {
  name           = var.catalog_name
  comment        = "AI Cyber Bootcamp 2026"
  storage_root   = "s3://${aws_s3_bucket.course.bucket}/catalog"
  isolation_mode = "ISOLATED"

  depends_on = [databricks_external_location.course]
}

resource "databricks_schema" "course" {
  catalog_name = databricks_catalog.course.name
  name         = var.schema_name
  comment      = "Course dataset and app assets"
}

# The course dataset. External so the bytes live at a known S3 path we can re-upload to.
resource "databricks_volume" "data" {
  catalog_name     = databricks_catalog.course.name
  schema_name      = databricks_schema.course.name
  name             = "data"
  volume_type      = "EXTERNAL"
  storage_location = "s3://${aws_s3_bucket.course.bucket}/data"
  comment          = "Read-only course data (mirror of the repo's data/ plus handoff outputs)"
}

# Rendered decks and tutor state. Managed: the app service principal reads and writes it.
resource "databricks_volume" "app" {
  catalog_name = databricks_catalog.course.name
  schema_name  = databricks_schema.course.name
  name         = "app"
  volume_type  = "MANAGED"
  comment      = "Slide decks and per-user tutor conversations"
}

resource "databricks_volume" "logs" {
  catalog_name = databricks_catalog.course.name
  schema_name  = databricks_schema.course.name
  name         = "logs"
  volume_type  = "MANAGED"
  comment      = "Cluster driver and event logs; they outlive the cluster"
}
