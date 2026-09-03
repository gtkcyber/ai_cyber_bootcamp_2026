"""Unit tests for probe.py against a fake WorkspaceClient — no network, no Databricks
workspace, no cluster. The generated PROBE cell can't run here (it needs dbutils and a
driver), so the local check is that it compiles as valid Python."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import probe


class FakeWaiter:
    def __init__(self, run_id):
        self.run_id = run_id

    def result(self, timeout=None):
        return SimpleNamespace()


class FakeJobsAPI:
    def __init__(self):
        self.submitted = []
        self.runs = {}
        self.outputs = {}

    def submit(self, **kwargs):
        self.submitted.append(kwargs)
        return FakeWaiter(run_id=100)

    def get_run(self, run_id):
        return self.runs[run_id]

    def get_run_output(self, task_run_id):
        return self.outputs[task_run_id]


class FakeWorkspaceAPI:
    def __init__(self):
        self.mkdirs_calls = []
        self.uploaded = {}

    def mkdirs(self, path):
        self.mkdirs_calls.append(path)

    def upload(self, path, buf, format=None, overwrite=True):
        self.uploaded[path] = buf.read()


class FakeWorkspaceClient:
    def __init__(self):
        self.jobs = FakeJobsAPI()
        self.workspace = FakeWorkspaceAPI()


def test_probe_source_compiles():
    # The PROBE cell runs remotely under dbutils; the reachable local check is that
    # it is valid Python (a syntax typo here would only surface after a real job run).
    compile(probe.PROBE, "probe", "exec")


def test_main_uploads_the_probe_notebook_and_prints_the_answers(monkeypatch, capsys):
    w = FakeWorkspaceClient()
    monkeypatch.setattr(probe, "WorkspaceClient", lambda profile: w)
    monkeypatch.setattr(probe, "cluster_id", lambda: "cluster-1")

    answers = {
        "cwd": "/Workspace/Users/curtis@gtkcyber.com/bootcamp-test/probes",
        "notebook_dir_matches_cwd": True,
        "work_home": "/Workspace/.../work/",
        "work_home_writable": True,
        "subprocess": "spawned",
        "tpot_install_rc": 0,
        "tpot_install_tail": "",
    }
    w.jobs.runs[100] = SimpleNamespace(tasks=[SimpleNamespace(run_id=200)])
    w.jobs.outputs[200] = SimpleNamespace(
        notebook_output=SimpleNamespace(result=json.dumps(answers)))

    rc = probe.main()
    assert rc == 0

    assert f"{probe.SCRATCH}/probes/build_facts" in w.workspace.uploaded
    assert f"{probe.SCRATCH}/probes" in w.workspace.mkdirs_calls

    submitted = w.jobs.submitted[0]
    assert submitted["tasks"][0].existing_cluster_id == "cluster-1"
    assert submitted["tasks"][0].notebook_task.notebook_path == \
        f"{probe.SCRATCH}/probes/build_facts"

    out = json.loads(capsys.readouterr().out)
    assert out == answers
