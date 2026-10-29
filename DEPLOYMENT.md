# Deploying your own copy of the bootcamp

This builds the same Databricks setup the course runs on, with only you as a user. You need a Databricks account, an AWS account, and an admin service principal for each. Nothing here is shared with the course.

## 1. Prerequisites

- An AWS account with rights to create S3 buckets and IAM roles.
- A Databricks account (account console) and an account admin login.
- Databricks CLI v0.2xx or later, and Terraform 1.6 or later. Check with `databricks --version` and `terraform -version`.
- Python 3.10+ (for `scripts/deploy-course-data.sh` helpers, if you use them).

## 2. Credentials (one-time, by you)

1. In the account console, create a service principal for automation (for example `my_automation`). Give it the account admin role and create an OAuth secret for it.
2. Put three profiles in `~/.databrickscfg` (never commit this file):

   ```ini
   [my-account]
   host          = https://accounts.cloud.databricks.com
   account_id    = <YOUR_DATABRICKS_ACCOUNT_ID>
   client_id     = <service principal application id>
   client_secret = <OAuth secret>

   [my-workspace]
   host          = <your workspace URL, filled in after step 3>
   client_id     = <same service principal>
   client_secret = <same secret>
   ```

3. Create an AWS profile with `aws configure --profile my-aws`, using credentials for your AWS account. Terraform's state bucket also lives in that account.

## 3. Change the account-specific values

The Terraform copied from the course has our values in it. Replace these before you run anything:

| File | What to change |
|---|---|
| `terraform/workspace/versions.tf` | `bucket = "<YOUR-TFSTATE-BUCKET>"`, `profile = "<your AWS profile>"`, `region` |
| `terraform/bootcamp/versions.tf` | the same backend bucket and profile |
| `terraform/*/providers.tf` | the profile names (`gtk-cyber`, `gtk-workspace`, `gtk-account`) to your `my-aws`, `my-workspace`, `my-account` |
| `terraform/bootcamp/locals.tf` | `prefix = "gtk-cyber-bootcamp"` to your own prefix |
| `terraform/bootcamp/variables.tf` | `admin_users` (the emails) and `automation_service_principal` |
| `terraform/workspace/*.tfvars.example` and `terraform/bootcamp/*.tfvars.example` | copy each to `terraform.tfvars` and fill in your account and workspace IDs |

Create the state bucket first: `aws s3 mb s3://<your-state-bucket> --profile my-aws --region us-east-1`, with versioning on.

## 4. Workspace (Terraform, first)

```bash
cd terraform/workspace
terraform init
terraform plan
terraform apply
```

Note the outputs: the workspace ID and URL. Put the URL into the `my-workspace` profile.

## 5. Course infrastructure (Terraform, second)

Set the workspace ID in `terraform/bootcamp/terraform.tfvars`, then:

```bash
cd terraform/bootcamp
terraform init
terraform plan
terraform apply
```

This creates the catalog, the course and logs volumes, the student group (only the people you list), the clusters, and the grants. It does not create the model endpoints or upload any data.

## 6. Data and notebooks (script)

```bash
scripts/deploy-course-data.sh --profile my-workspace --catalog ai_cyber_bootcamp --schema course
```

The script uploads `data/` and `slides/` to the data volume. Add `--home you@example.com` to also import the notebooks and answer keys into your home folder. Use `--dry-run` first to see the commands.

## 7. Library wheelhouse (not in this repo yet)

The clusters install their Python packages from a pinned wheelhouse in the data volume, not from PyPI. The wheelhouse is not in this repo; it has to be built and uploaded before the clusters can start cleanly. Until it exists, the cluster init script fails, so a cluster won't come up. Ask the course maintainer for the wheelhouse files, or build them with the wheelhouse steps the maintainer documents.

## 8. Models and endpoints (not automated yet)

The lab models (8.1, 8.2, 9.1, 9.5, 9.6) are trained by running the answer notebooks, then registered in Unity Catalog and served from endpoints. This step is manual today. The notebooks fall back to local training when the endpoints are missing, so the labs still run without them, just more slowly.

## 9. Check it works

- Start `bootcamp-labs` from the clusters page and wait for it to report RUNNING.
- Open your copy of Worksheet 1.1 and run it top to bottom.
- Open the 8.1 answer key and confirm the cells that load data run.

## Cost and shutdown

Clusters auto-terminate after 20 minutes of inactivity. Model endpoints scale to zero when idle. To stop everything, run `terraform destroy` in `terraform/bootcamp`, then `terraform/workspace`. Destroy needs your explicit go, because it deletes data.
