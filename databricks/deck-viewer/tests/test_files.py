import base64
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from databricks.sdk.errors import BadRequest, NotFound  # noqa: E402
from databricks.sdk.service.workspace import ExportFormat  # noqa: E402

from tutor.files import LocalFiles, MissingFile, WorkspaceTextFiles  # noqa: E402


def test_local_read_write_round_trip(tmp_path):
    files = LocalFiles(tmp_path)
    files.write("/a/b.txt", b"hello")
    assert files.read("/a/b.txt") == b"hello"
    assert files.exists("/a/b.txt")
    assert files.list("/a") == ["b.txt"]


def test_local_missing_read_raises(tmp_path):
    with pytest.raises(MissingFile):
        LocalFiles(tmp_path).read("/nope")


class FakeWorkspace:
    """Stands in for w.workspace, whose only read call is export().

    databricks-sdk 0.133 has no WorkspaceAPI.download; export returns the
    bytes base64-encoded in ExportResponse.content.
    """

    def __init__(self, contents=None, entries=(), refuse_formats=()):
        self.contents = contents or {}
        self.entries = entries
        self.refuse_formats = refuse_formats
        self.formats_seen = []

    def export(self, path, format=None):
        self.formats_seen.append(format)
        if format in self.refuse_formats:
            raise BadRequest(f"{format} not supported for {path}")
        if path not in self.contents:
            raise NotFound(path)
        return SimpleNamespace(content=base64.b64encode(self.contents[path]).decode("ascii"))

    def list(self, path):
        return [SimpleNamespace(path=f"{path}/{n}", object_type="FILE") for n in self.entries]

    def get_status(self, path):
        if path not in self.contents:
            raise NotFound(path)
        return SimpleNamespace(path=path)


def _w(**kw):
    return SimpleNamespace(workspace=FakeWorkspace(**kw))


def test_workspace_read_returns_bytes():
    files = WorkspaceTextFiles(_w(contents={"/Workspace/x/a.md": b"body"}))
    assert files.read("/Workspace/x/a.md") == b"body"


def test_workspace_read_of_a_missing_path_raises_missing_file():
    with pytest.raises(MissingFile):
        WorkspaceTextFiles(_w()).read("/Workspace/x/gone.md")


def test_a_markdown_file_is_exported_as_auto():
    w = _w(contents={"/Workspace/x/a.md": b"body"})
    WorkspaceTextFiles(w).read("/Workspace/x/a.md")
    assert w.workspace.formats_seen == [ExportFormat.AUTO]


def test_a_notebook_is_exported_as_jupyter_so_read_lab_gets_json():
    w = _w(contents={"/Workspace/x/lab.ipynb": b'{"cells": []}'})
    assert WorkspaceTextFiles(w).read("/Workspace/x/lab.ipynb") == b'{"cells": []}'
    assert w.workspace.formats_seen == [ExportFormat.JUPYTER]


def test_a_notebook_the_workspace_will_not_export_as_jupyter_falls_back_to_auto():
    """A .ipynb synced as a plain file, not a notebook, refuses JUPYTER."""
    w = _w(contents={"/Workspace/x/lab.ipynb": b'{"cells": []}'},
           refuse_formats=(ExportFormat.JUPYTER,))
    assert WorkspaceTextFiles(w).read("/Workspace/x/lab.ipynb") == b'{"cells": []}'
    assert w.workspace.formats_seen == [ExportFormat.JUPYTER, ExportFormat.AUTO]


def test_workspace_list_returns_basenames():
    files = WorkspaceTextFiles(_w(entries=("a.ipynb", "b.ipynb")))
    assert files.list("/Workspace/x") == ["a.ipynb", "b.ipynb"]


def test_workspace_exists_is_true_only_for_a_real_path():
    files = WorkspaceTextFiles(_w(contents={"/Workspace/x/a.md": b"y"}))
    assert files.exists("/Workspace/x/a.md")
    assert not files.exists("/Workspace/x/b.md")


@pytest.mark.parametrize("method,args", [("write", ("/p", b"x")), ("delete", ("/p",))])
def test_workspace_backend_is_read_only(method, args):
    with pytest.raises(NotImplementedError):
        getattr(WorkspaceTextFiles(_w()), method)(*args)
