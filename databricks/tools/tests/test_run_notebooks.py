"""Unit tests for run_notebooks.py against a fake WorkspaceClient — no network, no
Databricks workspace, no cluster. subprocess.run is monkeypatched for cluster_id()."""

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import run_notebooks as rn

JOB_CLUSTER = {"node_type_id": "r5d.large", "spark_version": "18.x-scala2.13",
               "use_ml_runtime": True, "is_single_node": True, "kind": "CLASSIC_PREVIEW",
               "data_security_mode": "DATA_SECURITY_MODE_DEDICATED"}
JOB_LIBRARIES = [{"pypi": {"package": "apachelogs"}}]


class FakeWaiter:
    def __init__(self, run_id, raise_on_result=None):
        self.run_id = run_id
        self._raise = raise_on_result

    def result(self, timeout=None):
        if self._raise:
            raise self._raise
        return SimpleNamespace()


class FakeJobsAPI:
    def __init__(self):
        self.submitted = []  # list of kwargs passed to submit()
        self._next_run_id = 100
        self.runs = {}  # run_id -> SimpleNamespace(tasks=[...])
        self.outputs = {}  # task run_id -> SimpleNamespace(error=..., notebook_output=...)
        self.raise_on_result = None
        self.cancelled = []
        self.exported = []

    def submit(self, **kwargs):
        self.submitted.append(kwargs)
        run_id = self._next_run_id
        self._next_run_id += 1
        return FakeWaiter(run_id, raise_on_result=self.raise_on_result)

    def get_run(self, run_id):
        return self.runs[run_id]

    def get_run_output(self, task_run_id):
        return self.outputs[task_run_id]

    def cancel_run(self, run_id):
        self.cancelled.append(run_id)
        return FakeWaiter(run_id)

    def export_run(self, run_id, views_to_export=None):
        self.exported.append(run_id)
        return SimpleNamespace(views=[SimpleNamespace(content="<html>epoch 1</html>")])


class FakeWorkspaceAPI:
    def __init__(self):
        self.mkdirs_calls = []
        self.uploaded = {}  # remote path -> bytes

    def mkdirs(self, path):
        self.mkdirs_calls.append(path)

    def upload(self, path, buf, format=None, overwrite=True):
        self.uploaded[path] = buf.read()


class FakeWorkspaceClient:
    def __init__(self):
        self.jobs = FakeJobsAPI()
        self.workspace = FakeWorkspaceAPI()


def test_job_cluster_reads_the_terraform_outputs(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        outputs = {"node_type_id": "r5d.large", "gpu_node_type_id": "g4dn.xlarge",
                   "spark_version": "18.x-scala2.13",
                   "cluster_pypi_packages": '["apachelogs","mcp<2"]'}
        return SimpleNamespace(stdout=outputs[cmd[-1]] + "\n")

    monkeypatch.setattr(rn.subprocess, "run", fake_run)
    spec = rn.job_cluster()
    assert spec["node_type_id"] == "r5d.large"
    assert spec["spark_version"] == "18.x-scala2.13"
    assert spec["use_ml_runtime"] is True
    assert spec["is_single_node"] is True
    assert spec["kind"] == "CLASSIC_PREVIEW"
    assert spec["data_security_mode"] == "DATA_SECURITY_MODE_DEDICATED"
    assert "single_user_name" not in spec
    assert rn.job_libraries() == [{"pypi": {"package": "apachelogs"}}, {"pypi": {"package": "mcp<2"}}]
    assert all(cmd[2:4] == ["output", "-raw"] for cmd in calls)
    gpu = rn.job_cluster(gpu=True)
    assert gpu["node_type_id"] == "g4dn.xlarge"
    assert {k: v for k, v in gpu.items() if k != "node_type_id"} == \
        {k: v for k, v in spec.items() if k != "node_type_id"}


def test_sync_pushes_answers_utils_and_mcp_server(tmp_path, monkeypatch):
    (tmp_path / "answers").mkdir()
    (tmp_path / "answers" / "Worksheet_1.1-Answers.ipynb").write_text("{}")
    (tmp_path / "answers" / "notes.txt").write_text("not a notebook")
    (tmp_path / "utils").mkdir()
    (tmp_path / "utils" / "email_loader.py").write_text("# code")
    (tmp_path / "utils" / "__pycache__").mkdir()
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "notebooks" / "mcp_server.py").write_text("# server")

    monkeypatch.setattr(rn, "ROOT", tmp_path)
    w = FakeWorkspaceClient()
    rn.sync(w)

    uploaded = w.workspace.uploaded
    assert f"{rn.SCRATCH}/answers/Worksheet_1.1-Answers" in uploaded
    assert f"{rn.SCRATCH}/answers/Worksheet_1.1-Answers.ipynb" not in uploaded
    assert f"{rn.SCRATCH}/answers/notes.txt" not in uploaded
    assert f"{rn.SCRATCH}/utils/email_loader.py" in uploaded
    assert f"{rn.SCRATCH}/notebooks/mcp_server.py" in uploaded


def test_run_one_reports_success():
    w = FakeWorkspaceClient()
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(
        run_id=200,
        state=SimpleNamespace(result_state=SimpleNamespace(value="SUCCESS"),
                              state_message=""))])
    w.jobs.outputs[200] = SimpleNamespace(error=None)
    result = rn.run_one(w, JOB_CLUSTER, "Worksheet_1.1-Answers.ipynb", minutes=5)
    assert result["state"] == "SUCCESS"
    assert result["notebook"] == "Worksheet_1.1-Answers.ipynb"
    submitted = w.jobs.submitted[0]
    assert submitted["tasks"][0].notebook_task.notebook_path == \
        f"{rn.SCRATCH}/answers/Worksheet_1.1-Answers"
    # A group cluster refuses API jobs, so every run gets its own job cluster.
    assert submitted["tasks"][0].existing_cluster_id is None
    assert submitted["tasks"][0].new_cluster.node_type_id == "r5d.large"
    assert submitted["tasks"][0].new_cluster.data_security_mode.value == "DATA_SECURITY_MODE_DEDICATED"
    assert submitted["tasks"][0].libraries[0].pypi.package == "apachelogs"


def test_run_one_reports_the_failed_state_and_message():
    w = FakeWorkspaceClient()
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(
        run_id=200,
        state=SimpleNamespace(result_state=SimpleNamespace(value="FAILED"),
                              state_message="boom"))])
    w.jobs.outputs[200] = SimpleNamespace(error=None)
    result = rn.run_one(w, JOB_CLUSTER, "Worksheet_1.1-Answers.ipynb", minutes=5)
    assert result["state"] == "FAILED"
    assert result["message"] == "boom"


def test_run_one_prefers_the_run_output_error_when_present():
    w = FakeWorkspaceClient()
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(
        run_id=200,
        state=SimpleNamespace(result_state=SimpleNamespace(value="FAILED"),
                              state_message="boom"))])
    w.jobs.outputs[200] = SimpleNamespace(error="a more specific traceback")
    result = rn.run_one(w, JOB_CLUSTER, "Worksheet_1.1-Answers.ipynb", minutes=5)
    assert result["message"] == "a more specific traceback"


def test_run_one_cancels_a_run_it_stopped_waiting_for():
    w = FakeWorkspaceClient()
    w.jobs.raise_on_result = TimeoutError("still running")
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(run_id=200, state=None)])
    w.jobs.outputs[200] = SimpleNamespace(error=None)
    result = rn.run_one(w, JOB_CLUSTER, "Worksheet_1.1-Answers.ipynb", minutes=5)
    assert result["state"] == "TIMEOUT"
    assert result["message"] == "cancelled after 5 minutes"
    assert w.jobs.cancelled == [100]


def test_a_finished_run_is_not_cancelled():
    w = FakeWorkspaceClient()
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(
        run_id=200,
        state=SimpleNamespace(result_state=SimpleNamespace(value="FAILED"),
                              state_message="boom"))])
    w.jobs.outputs[200] = SimpleNamespace(error=None)
    rn.run_one(w, JOB_CLUSTER, "Worksheet_1.1-Answers.ipynb", minutes=5)
    assert w.jobs.cancelled == []


def test_export_views_writes_the_rendered_notebook(tmp_path):
    w = FakeWorkspaceClient()
    rn.export_views(w, 100, tmp_path / "run.html")
    assert (tmp_path / "run.html").read_text() == "<html>epoch 1</html>"
    assert w.jobs.exported == [100]


def test_import_check_parses_the_notebook_report():
    w = FakeWorkspaceClient()
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(run_id=200)])
    report = {"python": "3.11.9", "ok": [["numpy", "1.26"]], "missing": [["tpot", "no module"]],
              "cuda": {"torch": "2.6", "available": True, "device": "Tesla T4"}}
    w.jobs.outputs[200] = SimpleNamespace(
        notebook_output=SimpleNamespace(result=json.dumps(report)))
    out = rn.import_check(w, JOB_CLUSTER, JOB_LIBRARIES)
    assert out == report
    assert f"{rn.SCRATCH}/import_check" in w.workspace.uploaded


def test_main_sync_only_stops_after_sync(monkeypatch, tmp_path):
    (tmp_path / "answers").mkdir()
    (tmp_path / "utils").mkdir()
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "notebooks" / "mcp_server.py").write_text("# server")
    monkeypatch.setattr(rn, "ROOT", tmp_path)
    monkeypatch.setattr(rn, "job_cluster", lambda gpu=False: JOB_CLUSTER)
    monkeypatch.setattr(rn, "job_libraries", lambda: JOB_LIBRARIES)
    w = FakeWorkspaceClient()
    monkeypatch.setattr(rn, "WorkspaceClient", lambda profile: w)
    monkeypatch.setattr(sys, "argv", ["run_notebooks.py", "--sync-only"])
    assert rn.main() == 0
    assert f"{rn.SCRATCH}/notebooks/mcp_server.py" in w.workspace.uploaded


def test_main_only_filters_to_one_notebook_and_writes_a_run_record(monkeypatch, tmp_path):
    (tmp_path / "answers").mkdir()
    (tmp_path / "utils").mkdir()
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "notebooks" / "mcp_server.py").write_text("# server")
    (tmp_path / "databricks").mkdir()
    monkeypatch.setattr(rn, "ROOT", tmp_path)
    monkeypatch.setattr(rn, "job_libraries", lambda: JOB_LIBRARIES)
    w = FakeWorkspaceClient()
    monkeypatch.setattr(rn, "WorkspaceClient", lambda profile: w)
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(
        run_id=200,
        state=SimpleNamespace(result_state=SimpleNamespace(value="SUCCESS"),
                              state_message=""))])
    w.jobs.outputs[200] = SimpleNamespace(error=None)
    monkeypatch.setattr(sys, "argv", ["run_notebooks.py", "--only", "9.2", "--gpu"])
    seen = []
    monkeypatch.setattr(rn, "job_cluster", lambda gpu=False: seen.append(gpu) or JOB_CLUSTER)
    rc = rn.main()
    assert rc == 0
    assert seen == [True]
    run_files = list((tmp_path / "databricks" / "test-runs").glob("*.json"))
    assert len(run_files) == 1
    record = json.loads(run_files[0].read_text())
    assert record["job_cluster"]["node_type_id"] == "r5d.large"
    assert len(record["results"]) == 1
    assert record["results"][0]["notebook"] == \
        "Worksheet_9.2_Unsupervised_Learning_with_Embeddings-Answers.ipynb"
    assert w.jobs.exported == []


def test_main_keeps_the_notebook_views_of_a_run_that_did_not_succeed(monkeypatch, tmp_path):
    (tmp_path / "answers").mkdir()
    (tmp_path / "utils").mkdir()
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "notebooks" / "mcp_server.py").write_text("# server")
    (tmp_path / "databricks").mkdir()
    monkeypatch.setattr(rn, "ROOT", tmp_path)
    monkeypatch.setattr(rn, "job_cluster", lambda gpu=False: JOB_CLUSTER)
    monkeypatch.setattr(rn, "job_libraries", lambda: JOB_LIBRARIES)
    w = FakeWorkspaceClient()
    monkeypatch.setattr(rn, "WorkspaceClient", lambda profile: w)
    w.jobs.raise_on_result = TimeoutError("still running")
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(run_id=200, state=None)])
    w.jobs.outputs[200] = SimpleNamespace(error=None)
    monkeypatch.setattr(sys, "argv", ["run_notebooks.py", "--only", "8.1", "--minutes", "1"])
    assert rn.main() == 1
    html = list((tmp_path / "databricks" / "test-runs").glob("*-100.html"))
    assert len(html) == 1 and html[0].read_text() == "<html>epoch 1</html>"
    assert w.jobs.cancelled == [100]


def test_only_matches_a_whole_worksheet_number():
    assert rn.select(rn.ORDER, "1.1") == ["Worksheet_1.1_Vectorized_Data_Structures-Answers.ipynb"]
    assert "Worksheet_11.1_AI_RAG_CVEs-Answers.ipynb" not in rn.select(rn.ORDER, "1.1")
    assert rn.select(rn.ORDER, "11.1") == ["Worksheet_11.1_AI_RAG_CVEs-Answers.ipynb"]
    assert rn.select(rn.ORDER, None) == rn.ORDER
