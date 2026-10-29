# Newest LTS runtime id. With kind set, spark_version is always the plain id and
# use_ml_runtime selects the ML image (GPU flavour follows from the node type).
data "databricks_spark_version" "lts" {
  long_term_support = true
  latest            = true
}

# Single node dedicated to the student group, on the ML runtime. One driver, no workers:
# every notebook kernel is a Python process on that machine. r5d.4xlarge is 128 GB and
# 16 vCPU, for about 30 concurrent kernels. driver_node_type_id is set to the same type
# because on a single-node cluster the only machine is the driver; leaving it unset
# booted an 8 GB m5d.large while node_type_id said r5d.large.
# Standard access mode boxes every notebook kernel into one 4 GB cgroup shared with two
# JVMs whatever the node size. Dedicated mode gives user code the node. The ML runtime
# ships tensorflow, torch, sentence-transformers, prophet, shap, langchain and langgraph,
# so cluster_pypi_packages holds only what it does not.
# Spark cannot be turned off: single-node runs Spark locally and the notebook gateway
# lives in that JVM. The heap is pinned on the cluster to spark.driver.memory=2g and
# spark.driver.memoryOverhead=2g. Unset, Databricks assigns about
# 0.8 * (0.97 * node RAM - 4.8 GB), which is ~95 GB on this node. Those two keys are not
# in this resource: spark_conf is ignore_changes, so a cluster replace must set them again.
resource "databricks_cluster" "labs" {
  cluster_name            = var.cluster_name
  spark_version           = data.databricks_spark_version.lts.id
  node_type_id            = "r5d.4xlarge"
  driver_node_type_id     = "r5d.4xlarge"
  autotermination_minutes = var.autotermination_minutes
  kind                    = "CLASSIC_PREVIEW"
  is_single_node          = true
  use_ml_runtime          = true
  data_security_mode      = "DATA_SECURITY_MODE_DEDICATED"
  single_user_name        = databricks_group.students.display_name
  is_pinned               = true

  # No aws_attributes: is_single_node makes the one node on-demand (first_on_demand = 1),
  # and a local-disk node needs no EBS volume.

  # Driver and event logs land in the logs volume, so a cluster that fails to start
  # still leaves its driver log behind.
  cluster_log_conf {
    volumes {
      destination = "/Volumes/${databricks_volume.logs.catalog_name}/${databricks_volume.logs.schema_name}/${databricks_volume.logs.name}"
    }
  }

  spark_env_vars = {
    COURSE_DATA_HOME = "/Volumes/${databricks_volume.data.catalog_name}/${databricks_volume.data.schema_name}/${databricks_volume.data.name}/"
  }

  # The course libraries come from a pinned wheelhouse, not PyPI: pip's resolver gave up on
  # the unpinned list (ResolutionTooDeep after 27 min) and took ~18 min when it did not.
  # The init script installs the exact pins with --no-deps from the wheelhouse volume in
  # seconds. Rebuild the wheelhouse when cluster_pypi_packages or the runtime changes:
  # docs/runbooks/wheelhouse.md.
  init_scripts {
    volumes {
      destination = "/Volumes/${databricks_volume.data.catalog_name}/${databricks_volume.data.schema_name}/${databricks_volume.data.name}/wheelhouse/install-wheelhouse.sh"
    }
  }

  # is_single_node makes Databricks set spark_conf (cluster.profile, spark.master) and the
  # ResourceClass tag on the cluster; the provider then reads them back as drift to remove.
  lifecycle {
    ignore_changes = [spark_conf, custom_tags]
  }

  depends_on = [databricks_mws_permission_assignment.students]
}

# Second labs cluster, same shape as the first, so the class can split in half. Unlike the
# first, the 2g driver heap is set here at create (spark_conf is still ignore_changes, so
# later edits in the UI are left alone). Students attach to whichever cluster they are told.
resource "databricks_cluster" "labs_b" {
  cluster_name            = var.labs_b_cluster_name
  spark_version           = data.databricks_spark_version.lts.id
  node_type_id            = "r5d.4xlarge"
  driver_node_type_id     = "r5d.4xlarge"
  autotermination_minutes = var.autotermination_minutes
  kind                    = "CLASSIC_PREVIEW"
  is_single_node          = true
  use_ml_runtime          = true
  data_security_mode      = "DATA_SECURITY_MODE_DEDICATED"
  single_user_name        = databricks_group.students.display_name
  is_pinned               = true

  cluster_log_conf {
    volumes {
      destination = "/Volumes/${databricks_volume.logs.catalog_name}/${databricks_volume.logs.schema_name}/${databricks_volume.logs.name}"
    }
  }

  spark_conf = {
    "spark.driver.memory"         = "2g"
    "spark.driver.memoryOverhead" = "2g"
  }

  spark_env_vars = {
    COURSE_DATA_HOME = "/Volumes/${databricks_volume.data.catalog_name}/${databricks_volume.data.schema_name}/${databricks_volume.data.name}/"
  }

  init_scripts {
    volumes {
      destination = "/Volumes/${databricks_volume.data.catalog_name}/${databricks_volume.data.schema_name}/${databricks_volume.data.name}/wheelhouse/install-wheelhouse.sh"
    }
  }

  lifecycle {
    ignore_changes = [spark_conf, custom_tags]
  }

  depends_on = [databricks_mws_permission_assignment.students]
}

# GPU cluster for the deep-learning modules (7 to 9): same shape as the labs cluster on a
# single-GPU node. The GPU ML runtime ships TensorFlow and Torch with CUDA; the only
# cluster library is art for modules 7.1 and 7.2. Needs the account's "Running On-Demand
# G and VT instances" vCPU quota raised from zero before it can start.
resource "databricks_cluster" "gpu" {
  cluster_name            = var.gpu_cluster_name
  spark_version           = data.databricks_spark_version.lts.id
  node_type_id            = var.gpu_node_type_id
  autotermination_minutes = var.autotermination_minutes
  kind                    = "CLASSIC_PREVIEW"
  is_single_node          = true
  use_ml_runtime          = true
  data_security_mode      = "DATA_SECURITY_MODE_DEDICATED"
  single_user_name        = databricks_group.students.display_name
  is_pinned               = true

  cluster_log_conf {
    volumes {
      destination = "/Volumes/${databricks_volume.logs.catalog_name}/${databricks_volume.logs.schema_name}/${databricks_volume.logs.name}"
    }
  }

  spark_env_vars = {
    COURSE_DATA_HOME = "/Volumes/${databricks_volume.data.catalog_name}/${databricks_volume.data.schema_name}/${databricks_volume.data.name}/"
  }

  dynamic "library" {
    for_each = toset(var.gpu_cluster_pypi_packages)
    content {
      pypi {
        package = library.value
      }
    }
  }

  lifecycle {
    ignore_changes = [spark_conf, custom_tags]
  }

  depends_on = [databricks_mws_permission_assignment.students]
}
