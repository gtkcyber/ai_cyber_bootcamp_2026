# Deployment notes

What an operator has to know that the bundle cannot say for itself. Every
command runs from the course repo root
(`/home/curtis/claude_projects/gtk_aws/ai_cyber_bootcamp_2026`) with the
project-local CLI at `/home/curtis/claude_projects/gtk_aws/bin/databricks`.

## App

The bundle deploys `bootcamp-slides` and the two class-hours jobs together, and
`cluster_id` is the one variable with no default. It comes from the infra
Terraform module, not from this repo:

```bash
/home/curtis/claude_projects/gtk_aws/bin/terraform \
  -chdir=/home/curtis/claude_projects/gtk_aws/terraform/bootcamp \
  output -raw cluster_id
```

so a deploy reads:

```bash
/home/curtis/claude_projects/gtk_aws/bin/databricks bundle deploy -p gtk-workspace \
  --var cluster_id="$(/home/curtis/claude_projects/gtk_aws/bin/terraform \
      -chdir=/home/curtis/claude_projects/gtk_aws/terraform/bootcamp output -raw cluster_id)"
```

Passing `--var cluster_id=""` is not a way to defer the cluster. It bakes an
empty id into both scheduled jobs, and `course_up.py` and `course_down.py` exit
non-zero on it rather than silently skipping the cluster half every morning and
evening of the class week. Both still start and stop the app before they fail,
so a misdeploy cannot leave the app running overnight.
