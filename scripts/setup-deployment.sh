#!/usr/bin/env bash
# Render the Terraform variables and the setup job from deploy.config, and upload the setup notebooks.
# Does NOT run terraform apply and does NOT run the job. It prints the commands for those.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONF="${1:-$ROOT/deploy.config}"
[ -f "$CONF" ] || { echo "missing $CONF: copy deploy.config.example and fill it in" >&2; exit 2; }
set -a; . "$CONF"; set +a

# Refuse to render with any placeholder still in place.
for v in TFSTATE_BUCKET DATABRICKS_ACCOUNT_ID WORKSPACE_ID AUTOMATION_SP STUDENT_GROUP JOB_CLUSTER_USER_ID ADMIN_EMAILS; do
  val="${!v}"; case "$val" in *"<"*|"") echo "deploy.config: $v is not set" >&2; exit 2;; esac
done

# 1. Terraform variable files, from the examples
python3 - "$ROOT" "$CONF" <<'PY'
import os, re, sys, shutil
root, conf = sys.argv[1], sys.argv[2]
env = dict(l.rstrip("\n").split("=", 1) for l in open(conf) if "=" in l and not l.lstrip().startswith("#"))
emails = [e.strip() for e in env["ADMIN_EMAILS"].split(",") if e.strip()]
for mod in ["workspace", "bootcamp"]:
    src = os.path.join(root, "terraform", mod, "terraform.tfvars.example")
    dst = os.path.join(root, "terraform", mod, "terraform.tfvars")
    if not os.path.exists(src):
        continue
    s = open(src).read()
    s = s.replace("<YOUR_DATABRICKS_ACCOUNT_ID>", env["DATABRICKS_ACCOUNT_ID"])
    s = s.replace("<YOUR_WORKSPACE_ID>", env["WORKSPACE_ID"])
    s = s.replace("<YOUR_AUTOMATION_SERVICE_PRINCIPAL>", env["AUTOMATION_SP"])
    s = s.replace("<YOUR-TFSTATE-BUCKET>", env["TFSTATE_BUCKET"])
    s = re.sub(r'"[A-Za-z0-9._%+-]+@example\.com"', lambda m: '"' + m.group(0)[1:-1] + '"', s)
    extra = {"aws_profile": env["AWS_PROFILE"], "account_profile": env["ACCOUNT_PROFILE"]}
    if mod == "bootcamp":
        extra.update({"workspace_profile": env["WORKSPACE_PROFILE"], "prefix": env["PREFIX"]})
    s = s.rstrip() + "\n" + "".join(f'{k} = "{v}"\n' for k, v in extra.items())
    open(dst, "w").write(s)
    print("wrote", dst)
PY

# 2. The setup job, with this deployment's folder, group and cluster identity
sed -e "s#/Workspace/<YOUR_SETUP_FOLDER>#${WORKSPACE_SETUP_PATH}#g" \
    -e "s#<YOUR_STUDENT_GROUP>#${STUDENT_GROUP}#g" \
    -e "s#<YOUR_SERVICE_PRINCIPAL_OR_USER_ID>#${JOB_CLUSTER_USER_ID}#g" \
    "$ROOT/setup/job.json" > "$ROOT/setup/job.rendered.json"
echo "wrote setup/job.rendered.json"

# 3. Upload the setup notebooks to the workspace (the job reads them from there)
databricks -p "$WORKSPACE_PROFILE" workspace mkdirs "$WORKSPACE_SETUP_PATH"
databricks -p "$WORKSPACE_PROFILE" workspace import-dir "$ROOT/setup" "$WORKSPACE_SETUP_PATH" --overwrite
echo "uploaded setup notebooks to $WORKSPACE_SETUP_PATH"

cat <<MSG

Next, by hand, when you are ready:
  cd terraform/workspace
  terraform init -backend-config="bucket=$TFSTATE_BUCKET" -backend-config="region=$AWS_REGION" -backend-config="profile=$AWS_PROFILE"
  terraform plan && terraform apply        # then put the workspace id into deploy.config as WORKSPACE_ID

  cd terraform/bootcamp
  terraform init -backend-config="bucket=$TFSTATE_BUCKET" -backend-config="region=$AWS_REGION" -backend-config="profile=$AWS_PROFILE"
  terraform plan && terraform apply

  scripts/deploy-course-data.sh --profile $WORKSPACE_PROFILE --catalog $CATALOG --schema $SCHEMA

  # Only when you decide to spend the compute:
  databricks -p $WORKSPACE_PROFILE jobs create --json @setup/job.rendered.json
MSG
