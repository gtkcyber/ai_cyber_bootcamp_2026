# Databricks notebook source
# MAGIC %md
# MAGIC # 3. Create the model serving endpoints
# MAGIC One endpoint per registered model, scale to zero, and query access for the students group. Run after
# MAGIC `02_train_register` has registered the models (versions must exist).

# COMMAND ----------

dbutils.widgets.text("catalog", "ai_cyber_bootcamp")
dbutils.widgets.text("schema", "models")
dbutils.widgets.text("student_group", "students")
CATALOG = dbutils.widgets.get("catalog")
MODELS_SCHEMA = dbutils.widgets.get("schema")
STUDENTS = dbutils.widgets.get("student_group")

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ServedEntityInput
from databricks.sdk.service.iam import AccessControlRequest, PermissionLevel
w = WorkspaceClient()

# Registered model name -> endpoint name. Keep in sync with the labs that call them.
MODELS = {
    "fingerprint_cnn": "bootcamp-fingerprint-cnn",
    "url_lstm_classifier": "bootcamp-url-lstm",
    "sql_injection_rf": "bootcamp-sql-injection",
    "gpt_9_5": "bootcamp-gpt-9-5",
    "gpt_9_6_base": "bootcamp-gpt-9-6-base",
    "gpt_9_6_finetuned": "bootcamp-gpt-9-6-finetuned",
    "gpt_9_6_scratch": "bootcamp-gpt-9-6-scratch",
    "gpt_9_6_victim": "bootcamp-gpt-9-6-victim",
    "gpt_9_6_clean": "bootcamp-gpt-9-6-clean",
}

# COMMAND ----------

for model, endpoint in MODELS.items():
    full = f"{CATALOG}.{MODELS_SCHEMA}.{model}"
    try:
        versions = list(w.model_versions.list(full_name=full))
    except Exception as e:
        print(f"SKIP {endpoint}: {full} is not registered ({e.__class__.__name__})")
        continue
    if not versions:
        print(f"SKIP {endpoint}: {full} has no versions yet")
        continue
    version = max(int(v.version) for v in versions)
    try:
        w.serving_endpoints.get(endpoint)
        print(f"exists: {endpoint}")
    except Exception:
        w.serving_endpoints.create_and_wait(
            name=endpoint,
            config={"served_entities": [ServedEntityInput(
                entity_name=full, entity_version=str(version),
                workload_size="Small", scale_to_zero_enabled=True)]})
        print(f"created: {endpoint} (v{version})")
    ep = w.serving_endpoints.get(endpoint)
    w.serving_endpoints.set_permissions(serving_endpoint_id=ep.id, access_control_list=[
        AccessControlRequest(group_name=STUDENTS, permission_level=PermissionLevel.CAN_QUERY)])
    print(f"students can query: {endpoint}")
