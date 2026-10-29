# Instructions for the agent working on this course copy

You are helping a student or instructor run their own copy of the AI Cyber Bootcamp on Databricks. Read `DEPLOYMENT.md` first; it is the source of truth for setup.

## Ground rules
- Never print, copy or commit credentials: `~/.databrickscfg`, OAuth secrets, AWS keys, or `.env` files. Refer to profiles by name only.
- Run `terraform plan` freely. Ask before any `terraform apply` or `destroy`; `destroy` deletes data.
- Ask before creating anything that spends compute (clusters, endpoints, jobs) or grants access to anyone.
- The Databricks CLI profile is the only credential path. Use `--profile`, or set `DATABRICKS_CONFIG_PROFILE`.

## Where things are
- `DEPLOYMENT.md`: the setup steps and the values to change.
- `terraform/workspace`: the workspace (run first).
- `terraform/bootcamp`: catalog, volumes, group, clusters, grants (run second).
- `scripts/deploy-course-data.sh`: uploads data, slides and optionally notebooks.
- `notebooks/`, `answers/`, `utils/`: the labs and their answer keys.
- `data/`, `slides/`: uploaded to the data volume.

## Order of work
1. Check the credentials work: `databricks -p my-workspace current-user me`.
2. Follow `DEPLOYMENT.md` sections 3 to 6 in order. Stop at each apply and report the plan first.
3. The wheelhouse (section 7) and the models and endpoints (section 8) are separate. Ask the user before starting either.

## Known limits
- Values in the Terraform that still point at the original course account must be replaced (see DEPLOYMENT.md section 3). If a value is not in the table, search for it before running Terraform.
- The labs call model endpoints on Databricks when they exist and train locally otherwise. A missing endpoint is not an error.
