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
| `run_notebooks.py` | Submits each answer notebook as a one-off job on its own job cluster, shaped like `bootcamp-labs` from the Terraform outputs (`--gpu`: like `bootcamp-gpu`), and records the result. The course clusters themselves are dedicated to the student group and refuse API jobs. `--import-check` also reports whether torch sees a CUDA device. |
| `probe.py` | Runs one generated notebook on a job cluster to settle the four build-time facts the design spec left open. |
| `build_decks.py` | Renders `slides/*.pdf` into the reveal decks under `decks/`. A deck with a Keynote manifest in `databricks/keynote/<slug>.json` takes its build stages, movies and YouTube embeds from it; without one the stages are inferred from the page text and the inference in `databricks/pages/` is kept as a human override surface. |
| `check_decks.py` | The deck gate: page images, notes, manifest consistency and media files. Exit code is the number of failures. |
| `build_keynote.py` | Builds a deck from its Keynote file on Linux: LibreOffice (in the `bootcamp-keynote` Docker image, built on first use from `keynote/docker/`) renders the slides, one page per build stage; the movies come out as `decks/<slug>/media/`; the manifest lands in `databricks/keynote/`; then `build_decks` runs. `--all <folder>` does every deck. Keynote sources live in `slides/keynote/` (gitignored). |
| `rekey_notes.py` | One-off migration of a deck's notes from the text-classified page numbers to the manifest's: old page p was Keynote slide p, so its note moves to slide p's finished page; slides the classifier had merged into one build each get the shared note and are reported. Refuses a deck already migrated. |
| `keynote/` | The package behind it: `package.py` flattens a .key, `model.py` decodes it (slides, drawables, click chunks, movies, web videos, tables), `stages.py` works out the canvas after each click, `odp.py` rewrites LibreOffice's ODP into stage pages, `render.py` drives LibreOffice and ffmpeg in Docker, `media.py` converts the movies. `PYTHONPATH=databricks/tools .venv/bin/python -m keynote inspect <key> [--json PATH]` prints a per-slide summary. |

All Databricks calls go through the `gtk-workspace` profile; the CLI itself lives at
`/home/curtis/claude_projects/gtk_aws/bin/databricks`. Run `pytest databricks/tools/tests`
with `.venv/bin/python -m pytest` before committing a tool change.
