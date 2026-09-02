import importlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def test_data_dir_follows_course_data_home(monkeypatch, tmp_path):
    monkeypatch.setenv("COURSE_DATA_HOME", str(tmp_path) + "/")
    sys.path.insert(0, str(REPO))
    for name in ("utils.email_loader", "utils.mock_tools"):
        sys.modules.pop(name, None)
    mod = importlib.import_module("utils.email_loader")
    assert Path(mod._DATA_DIR) == tmp_path


def test_data_dir_defaults_to_the_repo_data_dir(monkeypatch):
    monkeypatch.delenv("COURSE_DATA_HOME", raising=False)
    sys.path.insert(0, str(REPO))
    sys.modules.pop("utils.email_loader", None)
    mod = importlib.import_module("utils.email_loader")
    assert Path(mod._DATA_DIR) == REPO / "data"
