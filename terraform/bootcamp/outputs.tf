output "bucket" {
  value = aws_s3_bucket.course.bucket
}

output "data_volume_path" {
  value = "/Volumes/${databricks_volume.data.catalog_name}/${databricks_volume.data.schema_name}/${databricks_volume.data.name}"
}

output "app_volume_path" {
  value = "/Volumes/${databricks_volume.app.catalog_name}/${databricks_volume.app.schema_name}/${databricks_volume.app.name}"
}

output "cluster_id" {
  value = databricks_cluster.labs.id
}

output "node_type_id" {
  value = databricks_cluster.labs.node_type_id
}

output "spark_version" {
  value = data.databricks_spark_version.lts.id
}

output "student_group" {
  value = databricks_group.students.display_name
}

output "gpu_node_type_id" {
  value = databricks_cluster.gpu.node_type_id
}

output "gpu_cluster_id" {
  value = databricks_cluster.gpu.id
}

output "cluster_pypi_packages" {
  description = "JSON list, read by the course repo's run_notebooks.py to shape its job clusters like the labs cluster."
  value       = jsonencode(var.cluster_pypi_packages)
}
