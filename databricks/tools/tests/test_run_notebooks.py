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

    def submit(self, **kwargs):
        self.submitted.append(kwargs)
        run_id = self._next_run_id
        self._next_run_id += 1
        return FakeWaiter(run_id, raise_on_result=self.raise_on_result)

    def get_run(self, run_id):
        return self.runs[run_id]

    def get_run_output(self, task_run_id):
        return self.outputs[task_run_id]


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


def test_cluster_id_reads_terraform_output(monkeypatch):
    def fake_run(cmd, cwd, capture_output, text, check):
        assert cmd[0].endswith("bin/terraform")
        assert cmd[1] == "-chdir=terraform/bootcamp"
        assert cmd[2:] == ["output", "-raw", "cluster_id"]
        assert cwd == rn.GTK_AWS
        return subprocess.CompletedProcess(cmd, 0, stdout="0102-030405-abc123\n", stderr="")

    monkeypatch.setattr(rn.subprocess, "run", fake_run)
    assert rn.cluster_id() == "0102-030405-abc123"


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
    result = rn.run_one(w, "cluster-1", "Worksheet_1.1-Answers.ipynb", minutes=5)
    assert result["state"] == "SUCCESS"
    assert result["notebook"] == "Worksheet_1.1-Answers.ipynb"
    submitted = w.jobs.submitted[0]
    assert submitted["tasks"][0].notebook_task.notebook_path == \
        f"{rn.SCRATCH}/answers/Worksheet_1.1-Answers"


def test_run_one_reports_the_failed_state_and_message():
    w = FakeWorkspaceClient()
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(
        run_id=200,
        state=SimpleNamespace(result_state=SimpleNamespace(value="FAILED"),
                              state_message="boom"))])
    w.jobs.outputs[200] = SimpleNamespace(error=None)
    result = rn.run_one(w, "cluster-1", "Worksheet_1.1-Answers.ipynb", minutes=5)
    assert result["state"] == "FAILED"
    assert result["message"] == "boom"


def test_run_one_prefers_the_run_output_error_when_present():
    w = FakeWorkspaceClient()
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(
        run_id=200,
        state=SimpleNamespace(result_state=SimpleNamespace(value="FAILED"),
                              state_message="boom"))])
    w.jobs.outputs[200] = SimpleNamespace(error="a more specific traceback")
    result = rn.run_one(w, "cluster-1", "Worksheet_1.1-Answers.ipynb", minutes=5)
    assert result["message"] == "a more specific traceback"


def test_run_one_times_out_when_the_task_state_is_unresolved():
    w = FakeWorkspaceClient()
    w.jobs.raise_on_result = TimeoutError("still running")
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(run_id=200, state=None)])
    w.jobs.outputs[200] = SimpleNamespace(error=None)
    result = rn.run_one(w, "cluster-1", "Worksheet_1.1-Answers.ipynb", minutes=5)
    assert result["state"] == "TIMEOUT"
    assert "still running" in result["message"]


def test_import_check_parses_the_notebook_report():
    w = FakeWorkspaceClient()
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(run_id=200)])
    report = {"python": "3.11.9", "ok": [["numpy", "1.26"]], "missing": [["tpot", "no module"]]}
    w.jobs.outputs[200] = SimpleNamespace(
        notebook_output=SimpleNamespace(result=json.dumps(report)))
    out = rn.import_check(w, "cluster-1")
    assert out == report
    assert f"{rn.SCRATCH}/import_check" in w.workspace.uploaded


def test_main_sync_only_stops_after_sync(monkeypatch, tmp_path):
    (tmp_path / "answers").mkdir()
    (tmp_path / "utils").mkdir()
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "notebooks" / "mcp_server.py").write_text("# server")
    monkeypatch.setattr(rn, "ROOT", tmp_path)
    monkeypatch.setattr(rn, "cluster_id", lambda: "cluster-1")
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
    monkeypatch.setattr(rn, "cluster_id", lambda: "cluster-1")
    w = FakeWorkspaceClient()
    monkeypatch.setattr(rn, "WorkspaceClient", lambda profile: w)
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(
        run_id=200,
        state=SimpleNamespace(result_state=SimpleNamespace(value="SUCCESS"),
                              state_message=""))])
    w.jobs.outputs[200] = SimpleNamespace(error=None)
    # "9.2" is a substring of exactly one ORDER entry (run_notebooks.py's --only is a
    # plain substring match, unlike edits.py's exact-boundary _matches_only).
    monkeypatch.setattr(sys, "argv", ["run_notebooks.py", "--only", "9.2"])
    rc = rn.main()
    assert rc == 0
    run_files = list((tmp_path / "databricks" / "test-runs").glob("*.json"))
    assert len(run_files) == 1
    record = json.loads(run_files[0].read_text())
    assert record["cluster_id"] == "cluster-1"
    assert len(record["results"]) == 1
    assert record["results"][0]["notebook"] == \
        "Worksheet_9.2_Unsupervised_Learning_with_Embeddings-Answers.ipynb"
