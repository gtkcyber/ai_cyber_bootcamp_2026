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

## Labs cluster: what the live runs established (2026-09-03)

The cluster is `bootcamp-labs` from `gtk_aws/terraform/bootcamp`: single node,
standard access mode, Databricks Runtime 18 LTS (not the ML runtime, which
standard mode does not support), the course stack as cluster PyPI libraries.
Cold start is about eleven minutes to RUNNING plus eight for the libraries.

**Memory.** In single-node standard mode the notebook kernels share one
4 GB cgroup with two JVMs (2 GB and 1 GB heaps), whatever the node size; the
same limit was measured on an 8 GB and a 16 GB node. One kernel running a
heavy lab fits: 7.2 (art, torch, torchvision, CIFAR-10 download) ran in 37
minutes, 9.2 (sentence-transformers, torch) in 59, 8.2 in under one. A
kernel that imports the whole course stack at once does not fit, and how
many student kernels fit at the same time is untested. The error to expect
is `Execution ran out of memory. Try increasing your compute instance
memory.`, and a bigger node does not change it in this mode.

**Data.** `databricks/tools/upload_data.py` put 906 files (139 MB) on the
data volume with no errors in under a minute. `databricks/tools/probe.py`
confirmed the notebook's working directory is its own folder, `WORK_HOME`
is writable, subprocesses spawn, and a notebook-scoped `pip install` works.

**Library gaps found by the runs.**
- `tensorboard` is not installed and Keras `fit` needs it (8.1 fails with
  `TBNotInstalledError`); added to `cluster_pypi_packages`.
- `langgraph-supervisor` does not import against the `langgraph` the cluster
  resolved (`cannot import name 'ExecutionInfo' from 'langgraph.runtime'`);
  13.5 needs a pin.

**Workspace notebook paths.** A JUPYTER import names the object exactly as
the path is given, extension included; upload to the extension-less path
the job will ask for (fixed in the tools on the first live run).

Run records land in `databricks/test-runs/` (gitignored).
