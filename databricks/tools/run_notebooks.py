#!/usr/bin/env python3
"""Run every answer notebook as a one-off job on its own job cluster.

Usage (from the course repo root):
    .venv/bin/python databricks/tools/run_notebooks.py                # all, in order
    .venv/bin/python databricks/tools/run_notebooks.py --only 4.1     # one notebook
    .venv/bin/python databricks/tools/run_notebooks.py --import-check # library probe
    .venv/bin/python databricks/tools/run_notebooks.py --sync-only    # push, run nothing

The labs cluster is dedicated to the student group and a group cluster refuses API
jobs from anyone outside the group, so each run gets a job cluster shaped like the labs
cluster (same node, runtime and libraries, read from the Terraform outputs) that lives
only for that run. A run record lands in databricks/test-runs/.
"""

import argparse
import io
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.compute import ClusterSpec, DataSecurityMode, Kind, Library, PythonPyPiLibrary
from databricks.sdk.service.jobs import NotebookTask, SubmitTask
from databricks.sdk.service.workspace import ImportFormat

PROFILE = "gtk-workspace"
SCRATCH = "/Workspace/Users/curtis@gtkcyber.com/bootcamp-test"
GTK_AWS = "/home/curtis/claude_projects/gtk_aws"
ROOT = Path(__file__).resolve().parents[2]

# Answer notebooks in dependency order. 3.1 feeds 4.1/4.2/4.3/5.1/7.1;
# 4.1 feeds 7.1; 9.4 feeds 9.5 and 9.6. The rest are independent.
ORDER = [
    "Worksheet_1.1_Vectorized_Data_Structures-Answers.ipynb",
    "Worksheet_2.1_Data Visualization-Answers.ipynb",
    "Worksheet_3.1_Feature_Engineering-Answers.ipynb",
    "Worksheet_4.1_DGA_Detection_using_Supervised_Learning-Answers.ipynb",
    "Worksheet_4.2_Tuning_Your_Classifier-Answers.ipynb",
    "Worksheet_4.3_Automate_It_All-Answers.ipynb",
    "Worksheet_5.1_Clustering-Answers.ipynb",
    "Worksheet_6.1_Anomaly_Detection-Answers.ipynb",
    "Worksheet_7.1_Attacking_AI-Answers.ipynb",
    "Worksheet_7.2_FSGM_Attack_on_Image_Classifier-Answers.ipynb",
    "Worksheet_8.1_Deep_Learning_CNN_Fingerprints-Answers.ipynb",
    "Worksheet_8.2_Deep_Learning_RNN_URL-Answers.ipynb",
    "Worksheet_9.1_Classification_with_Embeddings-Answers.ipynb",
    "Worksheet_9.2_Unsupervised_Learning_with_Embeddings-Answers.ipynb",
    "Worksheet_9.3_PyTorch_in_20_Minutes-Answers.ipynb",
    "Worksheet_9.4_Tokenizers_and_Embeddings-Answers.ipynb",
    "Worksheet_9.5_Attention_and_Your_First_GPT-Answers.ipynb",
    "Worksheet_9.6_Fine_Tuning_and_Poisoning-Answers.ipynb",
    "Worksheet_10.1_Programmatic_LLM_Interaction-Answers.ipynb",
    "Worksheet_10.2_Classification_with_LLMs-Answers.ipynb",
    "Worksheet_11.1_AI_RAG_CVEs-Answers.ipynb",
    "Worksheet_11.2_Building_Agent_Tools-Answers.ipynb",
    "Worksheet_12.1_Building_an_MCP_Server-Answers.ipynb",
    "Worksheet_13.1_Single_Email_Classifier-Answers.ipynb",
    "Worksheet_13.2_Tool_Calling_Agent-Answers.ipynb",
    "Worksheet_13.3_Conditional_Routing-Answers.ipynb",
    "Worksheet_13.4_Human_in_The_Loop-Answers.ipynb",
    "Worksheet_13.5_Multi_Agent_Supervisor-Answers.ipynb",
    "openai_api_fundamentals_answers.ipynb",
]

# Third-party modules the ported course imports on Databricks. anthropic and
# langchain_anthropic are deliberately absent: only the local seam branch uses them.
# tpot is absent too: Module 4.3 installs it notebook-scoped (spec Decision 12).
CLUSTER_MODULES = [
    "IPython", "PIL", "apachelogs", "art", "data_profiling", "databricks_langchain",
    "dotenv", "joblib", "keras", "langchain", "langchain_community", "langchain_core",
    "langchain_huggingface", "langchain_mcp_adapters", "langgraph",
    "langgraph_supervisor", "lime", "matplotlib", "mcp", "numpy", "openai", "pandas",
    "pmdarima", "prophet", "pydantic", "scipy", "seaborn", "sentence_transformers",
    "shap", "sklearn", "statsmodels", "tensorflow", "torch", "torchvision",
    "typing_extensions", "user_agents",
]


def _tf_output(name: str) -> str:
    out = subprocess.run(
        [f"{GTK_AWS}/bin/terraform", "-chdir=terraform/bootcamp", "output", "-raw", name],
        cwd=GTK_AWS, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def job_cluster() -> dict:
    """A single-node job cluster shaped like the labs cluster, dedicated to whoever
    submits the run (the automation service principal) rather than to the group."""
    return {"node_type_id": _tf_output("node_type_id"),
            "spark_version": _tf_output("spark_version"),
            "use_ml_runtime": True, "is_single_node": True, "kind": "CLASSIC_PREVIEW",
            "data_security_mode": "DATA_SECURITY_MODE_DEDICATED"}


def job_libraries() -> list[dict]:
    return [{"pypi": {"package": p}} for p in json.loads(_tf_output("cluster_pypi_packages"))]


def _task(key: str, path: str, spec: dict, libraries: list[dict]) -> SubmitTask:
    cluster = ClusterSpec(
        node_type_id=spec["node_type_id"], spark_version=spec["spark_version"],
        use_ml_runtime=spec["use_ml_runtime"], is_single_node=spec["is_single_node"],
        kind=Kind(spec["kind"]), data_security_mode=DataSecurityMode(spec["data_security_mode"]),
        num_workers=0)
    return SubmitTask(task_key=key, new_cluster=cluster,
                      libraries=[Library(pypi=PythonPyPiLibrary(package=l["pypi"]["package"])) for l in libraries],
                      notebook_task=NotebookTask(notebook_path=path))


def select(order: list[str], only: str | None) -> list[str]:
    """--only names a worksheet number; 1.1 must not also pick 11.1."""
    if not only:
        return list(order)
    return [n for n in order if f"Worksheet_{only}_" in n]


def _upload(w, local: Path, remote: str, fmt: ImportFormat) -> None:
    w.workspace.mkdirs(os.path.dirname(remote))
    with open(local, "rb") as fh:
        w.workspace.upload(remote, io.BytesIO(fh.read()), format=fmt, overwrite=True)


def sync(w) -> None:
    """Push answers/, utils/ and mcp_server.py into the scratch tree."""
    # A JUPYTER import names the workspace object after the path as given, extension
    # included, and the job then has to ask for that exact name; strip it here so the
    # object is Worksheet_X and run_one's path matches.
    for name in sorted(os.listdir(ROOT / "answers")):
        if name.endswith(".ipynb"):
            _upload(w, ROOT / "answers" / name, f"{SCRATCH}/answers/{name[:-6]}",
                    ImportFormat.JUPYTER)
    for name in sorted(os.listdir(ROOT / "utils")):
        if name.endswith(".py"):
            _upload(w, ROOT / "utils" / name, f"{SCRATCH}/utils/{name}",
                    ImportFormat.RAW)
    _upload(w, ROOT / "notebooks" / "mcp_server.py",
            f"{SCRATCH}/notebooks/mcp_server.py", ImportFormat.RAW)
    print(f"SYNCED to {SCRATCH}", flush=True)


def run_one(w, spec: dict, name: str, minutes: int = 90, libraries: list[dict] | None = None) -> dict:
    """Submit one notebook on its own job cluster, wait, and report state, message and wall time."""
    started = time.time()
    path = f"{SCRATCH}/answers/{name[:-6]}" if name.endswith(".ipynb") else name
    waiter = w.jobs.submit(
        run_name=f"bootcamp-test {name}",
        tasks=[_task("lab", path, spec, libraries or job_libraries())],
    )
    run_id = waiter.run_id
    state, message = "TIMEOUT", f"did not finish inside {minutes} minutes"
    try:
        waiter.result(timeout=timedelta(minutes=minutes))
    except Exception as exc:  # noqa: BLE001 - a failed run is data, not a crash
        message = str(exc)[:600]
    run = w.jobs.get_run(run_id)
    task = run.tasks[0]
    if task.state and task.state.result_state:
        state = task.state.result_state.value
        message = (task.state.state_message or "")[:600]
    try:
        out = w.jobs.get_run_output(task.run_id)
        if out.error:
            message = out.error[:600]
    except Exception:  # noqa: BLE001 - output is best-effort detail
        pass
    seconds = round(time.time() - started, 1)
    print(f"{state:9} {seconds:7.1f}s  {name}", flush=True)
    if message:
        print(f"          {message.splitlines()[0][:160]}", flush=True)
    return {"notebook": name, "state": state, "message": message,
            "seconds": seconds, "run_id": run_id}


IMPORT_CHECK_SOURCE = '''import importlib, json, sys
report = {"python": sys.version.split()[0], "ok": [], "missing": []}
for name in %s:
    try:
        module = importlib.import_module(name)
        report["ok"].append([name, getattr(module, "__version__", "?")])
    except Exception as exc:
        report["missing"].append([name, str(exc)[:200]])
print(json.dumps(report, indent=2))
dbutils.notebook.exit(json.dumps(report))
'''


def import_check(w, spec: dict, libraries: list[dict]) -> dict:
    """Run one generated notebook that imports every module the course needs."""
    import nbformat

    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(
        IMPORT_CHECK_SOURCE % json.dumps(CLUSTER_MODULES)))
    buf = io.BytesIO(nbformat.writes(nb).encode("utf-8"))
    remote = f"{SCRATCH}/import_check"
    w.workspace.mkdirs(SCRATCH)
    w.workspace.upload(remote, buf, format=ImportFormat.JUPYTER, overwrite=True)
    waiter = w.jobs.submit(
        run_name="bootcamp import-check",
        tasks=[_task("probe", remote, spec, libraries)],
    )
    waiter.result(timeout=timedelta(minutes=40))
    run = w.jobs.get_run(waiter.run_id)
    payload = w.jobs.get_run_output(run.tasks[0].run_id).notebook_output.result
    report = json.loads(payload)
    print(f"python {report['python']}")
    print(f"OK      {len(report['ok'])}: "
          f"{', '.join(n for n, _v in report['ok'])}")
    print(f"MISSING {len(report['missing'])}: "
          f"{', '.join(n for n, _e in report['missing'])}")
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="worksheet number of one answer notebook, e.g. 4.1")
    ap.add_argument("--import-check", action="store_true")
    ap.add_argument("--sync-only", action="store_true")
    ap.add_argument("--minutes", type=int, default=90, help="per-notebook timeout")
    args = ap.parse_args()

    w = WorkspaceClient(profile=PROFILE)
    spec, libraries = job_cluster(), job_libraries()
    print(f"job cluster {spec['node_type_id']} {spec['spark_version']} ml, "
          f"{len(libraries)} libraries", flush=True)
    sync(w)
    if args.sync_only:
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = ROOT / "databricks" / "test-runs"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.import_check:
        record = {"job_cluster": spec, "started": stamp,
                  "import_check": import_check(w, spec, libraries)}
        (out_dir / f"{stamp}-import-check.json").write_text(
            json.dumps(record, indent=2))
        return 0

    names = select(ORDER, args.only)
    results = [run_one(w, spec, n, args.minutes, libraries) for n in names]
    record = {"job_cluster": spec, "started": stamp, "results": results}
    (out_dir / f"{stamp}.json").write_text(json.dumps(record, indent=2))
    failed = [r for r in results if r["state"] != "SUCCESS"]
    print(f"\n{len(results) - len(failed)}/{len(results)} succeeded; "
          f"record at databricks/test-runs/{stamp}.json")
    for r in failed:
        print(f"  FAILED {r['notebook']}: {r['message'].splitlines()[0][:120]}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
