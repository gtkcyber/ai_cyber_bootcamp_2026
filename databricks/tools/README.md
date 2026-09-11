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
| `run_notebooks.py` | Submits each answer notebook as a one-off job on its own job cluster, shaped like `bootcamp-labs` from the Terraform outputs, and records the result. The labs cluster itself is dedicated to the student group and refuses API jobs. |
| `probe.py` | Runs one generated notebook on a job cluster to settle the four build-time facts the design spec left open. |
| `keynote/` | Decodes a Keynote (.key) file into a plain-Python deck model (slides, drawables, build/click chunks, movies, web videos, table dimensions) using keynote-parser's Python API directly. `python -m keynote inspect <key> [--json PATH]` prints a per-slide summary. |

All Databricks calls go through the `gtk-workspace` profile; the CLI itself lives at
`/home/curtis/claude_projects/gtk_aws/bin/databricks`. Run `pytest databricks/tools/tests`
with `.venv/bin/python -m pytest` before committing a tool change.
