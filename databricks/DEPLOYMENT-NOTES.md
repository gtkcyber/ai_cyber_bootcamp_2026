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

## Decks: Keynote manifests and media

A deck built from its Keynote file ships with `databricks/keynote/<slug>.json`: one
entry per PDF page naming the Keynote slide and build stage it renders, plus the
movies and YouTube embeds on the slides. `build_decks.py` groups a manifest deck's
pages by slide (no text heuristic), rewrites `databricks/pages/<slug>.json` from the
manifest on every build, and places each movie as a `<video>` and each YouTube link
as an `<iframe>` over the finished page in the box Keynote drew it in. Movie files
live in `decks/<slug>/media/` beside the page images and reach the app the same way,
through the volume. To take a deck back to text classification, delete both the
manifest and its `databricks/pages/` file.

The manifests come from `build_keynote.py`, which builds a deck from its Keynote file
with no Mac: LibreOffice's Keynote importer (in the project's Docker image) renders the
slides, and the tool rewrites the intermediate ODP so every build click is its own page,
matched to Keynote's build data by object geometry, before the PDF export. What the
importer cannot draw is listed under `losses` in the manifest: native tables (rendered
separately, see below) and any build object it produced nothing for. Rebuild one deck
with `.venv/bin/python databricks/tools/build_keynote.py "slides/keynote/<Module>.key"`
after the Keynote file changes; the notes stay keyed by finished page number, so a
change that adds or removes pages needs the notes re-keyed too.

Browsers fetch a `<video>` in byte ranges and refuse to play or seek without 206
replies, so `/decks/<path>` answers `Range` requests (`ranges.py`, also used by
`local_run.py`). A movie is read from the volume once and served from the byte cache
after that; the cache cap is 128 MB so the largest movie (43 MB) fits without
evicting the deck it belongs to.

## Labs cluster: what the live runs established

The cluster is `bootcamp-labs` from `gtk_aws/terraform/bootcamp`: single node,
**dedicated to the student group**, Databricks Runtime 18 LTS ML, with only the
libraries the ML runtime does not ship as cluster PyPI libraries. Cold start
is about ten minutes to RUNNING plus a few for the libraries.

**Why dedicated (2026-09-11).** In single-node standard mode the notebook
kernels share one 4 GB cgroup with two JVMs (2 GB and 1 GB heaps) whatever
the node size; the same limit was measured on an 8 GB and a 16 GB node. One
kernel running a heavy lab fit (7.2 in 37 minutes, 9.2 in 59, 8.2 in under
one), but the whole course stack in one kernel did not, and standard mode
supports neither the ML runtime nor GPU nodes. Measured on the same 16 GB
node in dedicated-group mode: an 11 GB cgroup, a 7.8 GB driver heap, and the
whole stack imports with the kernel at 1.3 GB.

**What dedicated-group changes.**
- Every action on the cluster runs with the group's permissions, so student
  work lives under `/Workspace/Groups/bh_india_2026_students/`, not home
  folders (the folder exists; per-student subfolders and the lab copies are
  the roster step).
- API jobs cannot target the cluster: a submit from the automation service
  principal fails with `PERMISSION_DENIED: not authorized to use account
  group`. `run_notebooks.py` and `probe.py` therefore submit each run on its
  own job cluster shaped like the labs cluster (node, runtime and library list
  read from the Terraform outputs), which exists only for that run.
- Students get CAN_ATTACH_TO on every course cluster; only admins start,
  restart or edit one. The class-hours jobs start and stop the cluster as the
  service principal, which CAN_MANAGE allows.

**GPU cluster.** `bootcamp-gpu` (g4dn.xlarge, GPU ML runtime, dedicated to
the same group) is declared in Terraform but cannot be created until the AWS
account's "Running On-Demand G and VT instances" vCPU quota is raised from
zero (Service Quotas, code L-DB2E81BA, us-east-1; four vCPUs cover one
g4dn.xlarge).

**Data.** `databricks/tools/upload_data.py` put 906 files (139 MB) on the
data volume with no errors in under a minute. `databricks/tools/probe.py`
confirmed the notebook's working directory is its own folder, `WORK_HOME`
is writable, subprocesses spawn, and a notebook-scoped `pip install` works.

**Library gaps found by the runs on the earlier standard-mode cluster.**
`tensorboard` (Keras fit needs it) and lower bounds on `langgraph` and
`langchain` (Databricks installs cluster libraries one at a time in list
order, and unbounded they settled on an inconsistent 1.0-era set that broke
13.5's `langgraph-supervisor`). The ML runtime ships all three now, so those
entries are gone from `cluster_pypi_packages`; what remains is only what the
runtime lacks.

**Workspace notebook paths.** A JUPYTER import names the object exactly as
the path is given, extension included; upload to the extension-less path
the job will ask for (fixed in the tools on the first live run).

Run records land in `databricks/test-runs/` (gitignored).

### GPU (2026-09-11)

`run_notebooks.py --gpu` shapes the job cluster like `bootcamp-gpu` (g4dn.xlarge, one T4).
`--import-check --gpu`: CUDA available, "Tesla T4", torch 2.9.0+cu129; every course
module imports except `databricks_langchain`, which fails on the GPU ML runtime with
`cannot import name 'RequestContext' from 'mcp.shared.context'` (the cluster-installed
`mcp<2` against the runtime's own langchain stack; the CPU runtime was not re-checked).
Lab 8.1 (CNN fingerprints) ran to SUCCESS in 1,121 s wall clock including about ten
minutes of cluster start, under a 25-minute cap. The AWS quota is four G-instance vCPUs,
so one g4dn.xlarge at a time: the course cluster and a GPU job cluster cannot coexist,
and a just-terminated node keeps its vCPUs for a couple of minutes.
