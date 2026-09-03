#!/usr/bin/env python3
"""Answer the build-time questions the design spec leaves open.

Generates one notebook, runs it on the labs cluster, prints the answers.

Usage (from the course repo root):
    .venv/bin/python databricks/tools/probe.py
"""

import io
import json
import sys
from datetime import timedelta
from pathlib import Path

import nbformat
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import NotebookTask, SubmitTask
from databricks.sdk.service.workspace import ImportFormat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_notebooks import PROFILE, SCRATCH, cluster_id

PROBE = '''
import json, os, subprocess, sys

answers = {}
answers["cwd"] = os.getcwd()
answers["notebook_dir_matches_cwd"] = os.getcwd().rstrip("/").endswith("probes")

# WORK_HOME as the seam computes it, and whether it is writable.
work = os.path.abspath("../work") + "/"
answers["work_home"] = work
try:
    os.makedirs(work, exist_ok=True)
    with open(work + "probe.txt", "w") as fh:
        fh.write("ok")
    answers["work_home_writable"] = open(work + "probe.txt").read() == "ok"
except Exception as exc:
    answers["work_home_writable"] = f"NO: {exc}"

# Subprocess spawning (Module 12.1 runs mcp_server.py over stdio).
try:
    out = subprocess.run([sys.executable, "-c", "print('spawned')"],
                         capture_output=True, text=True, timeout=60)
    answers["subprocess"] = out.stdout.strip() or f"rc={out.returncode} {out.stderr[:200]}"
except Exception as exc:
    answers["subprocess"] = f"NO: {exc}"

# Notebook-scoped install of TPOT with the old setuptools pin (Module 4.3).
try:
    out = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet",
                          "setuptools<58", "tpot"],
                         capture_output=True, text=True, timeout=900)
    answers["tpot_install_rc"] = out.returncode
    answers["tpot_install_tail"] = (out.stderr or out.stdout)[-400:]
except Exception as exc:
    answers["tpot_install_rc"] = f"NO: {exc}"

print(json.dumps(answers, indent=2))
dbutils.notebook.exit(json.dumps(answers))
'''


def main() -> int:
    w = WorkspaceClient(profile=PROFILE)
    cid = cluster_id()
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(PROBE))
    remote = f"{SCRATCH}/probes/build_facts"
    w.workspace.mkdirs(f"{SCRATCH}/probes")
    w.workspace.upload(remote, io.BytesIO(nbformat.writes(nb).encode("utf-8")),
                       format=ImportFormat.JUPYTER, overwrite=True)
    waiter = w.jobs.submit(
        run_name="bootcamp build-facts probe",
        tasks=[SubmitTask(task_key="probe", existing_cluster_id=cid,
                          notebook_task=NotebookTask(notebook_path=remote))],
    )
    waiter.result(timeout=timedelta(minutes=45))
    run = w.jobs.get_run(waiter.run_id)
    payload = w.jobs.get_run_output(run.tasks[0].run_id).notebook_output.result
    print(json.dumps(json.loads(payload), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
