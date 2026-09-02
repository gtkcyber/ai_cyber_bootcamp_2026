# Databricks port tooling

Project-local venv, never a global install:

```bash
cd /home/curtis/claude_projects/gtk_aws/ai_cyber_bootcamp_2026
python3 -m venv .venv && .venv/bin/python -m pip install -r databricks/tools/requirements.txt
```

| Tool | What it does |
|---|---|
| `edits.py` | Applies the seam cell and every listed substitution to the worksheets and answers. `--check` reports without writing. |
| `check_notebook.py` | The gate. Exit code is the number of violations. |
| `upload_data.py` | Mirrors `data/` plus the extracted fingerprint images to the course volume. |
| `run_notebooks.py` | Submits each answer notebook as a one-off job on the `bootcamp-labs` cluster and records the result. |

All Databricks calls go through the `gtk-workspace` profile; the CLI itself lives at
`/home/curtis/claude_projects/gtk_aws/bin/databricks`. Run `pytest databricks/tools/tests`
with `.venv/bin/python -m pytest` before committing a tool change.
