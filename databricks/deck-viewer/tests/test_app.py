import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

DECKS = "/Volumes/ai_cyber_bootcamp/course/app/decks"


def _title(text):
    return f"<!doctype html><html><head><title>{text}</title></head><body></body></html>".encode()


class FakeFiles:
    """Stands in for w.files: directories and index.html bodies keyed by path."""

    def __init__(self, decks):
        self.decks = decks

    def list_directory_contents(self, path):
        return [SimpleNamespace(path=f"{path}/{name}", is_directory=True) for name in self.decks]

    def download(self, path):
        name = path[len(DECKS) + 1:].split("/", 1)[0]
        body = self.decks.get(name)
        if body is None:
            from databricks.sdk.errors import NotFound
            raise NotFound(path)
        return SimpleNamespace(contents=SimpleNamespace(read=lambda: body))


@pytest.fixture
def app_module(monkeypatch):
    monkeypatch.setenv("DECKS_VOLUME_PATH", DECKS)
    monkeypatch.setenv("COURSE_TITLE", "AI Cyber Bootcamp 2026")
    monkeypatch.setenv("TUTOR_STATE_PATH", "/Volumes/ai_cyber_bootcamp/course/app/tutor_state")
    monkeypatch.setenv("TUTOR_CHAT_ENDPOINT", "databricks-deepseek-v4-flash-0731")
    monkeypatch.setenv("TUTOR_SKILLS_PATH", "/Workspace/x/databricks/tutor-skills")
    monkeypatch.setenv("TUTOR_LABS_PATH", "/Workspace/x/notebooks")
    monkeypatch.setenv("TUTOR_ANSWERS_PATH", "/Workspace/x/answers")
    monkeypatch.setattr("databricks.sdk.WorkspaceClient", lambda *a, **k: SimpleNamespace(
        files=None, config=SimpleNamespace(host="https://example.cloud.databricks.com"),
        workspace=None))
    sys.modules.pop("app", None)
    return importlib.import_module("app")


def _decks(app, mapping):
    app.w.files = FakeFiles(mapping)
    app.read_volume_file.cache_clear()
    app.list_decks.cache_clear()
    return app.list_decks()


def test_module_deck_label_is_number_and_name(app_module):
    decks = _decks(app_module, {
        "04-supervised-machine-learning":
            _title("AI Cyber Bootcamp 2026 — Module 4: Supervised Machine Learning")})
    assert decks == [{"id": "04-supervised-machine-learning",
                      "title": "Module 4 — Supervised Machine Learning"}]


def test_final_project_has_no_module_number(app_module):
    decks = _decks(app_module, {
        "15-final-project": _title("AI Cyber Bootcamp 2026 — Final Project")})
    assert decks == [{"id": "15-final-project", "title": "Final Project"}]


def test_module_zero_keeps_its_zero(app_module):
    decks = _decks(app_module, {
        "00-introduction": _title("AI Cyber Bootcamp 2026 — Module 0: Introduction")})
    assert decks[0]["title"] == "Module 0 — Introduction"


def test_decks_are_sorted_by_folder_so_fifteen_is_last(app_module):
    decks = _decks(app_module, {
        "15-final-project": _title("AI Cyber Bootcamp 2026 — Final Project"),
        "02-data-visualization": _title("AI Cyber Bootcamp 2026 — Module 2: Data Visualization"),
        "09-artificial-intelligence-introduction-and-theory":
            _title("AI Cyber Bootcamp 2026 — Module 9: Artificial Intelligence Introduction and Theory"),
    })
    assert [d["id"] for d in decks] == [
        "02-data-visualization",
        "09-artificial-intelligence-introduction-and-theory",
        "15-final-project",
    ]


def test_a_title_with_an_html_entity_is_unescaped(app_module):
    decks = _decks(app_module, {
        "07-attacking-machine-learning-models":
            _title("AI Cyber Bootcamp 2026 &#8212; Module 7: Attacking Machine Learning Models")})
    assert decks[0]["title"] == "Module 7 — Attacking Machine Learning Models"


def test_a_deck_with_no_title_tag_falls_back_to_its_folder(app_module):
    decks = _decks(app_module, {"11-ai-components": b"<html><body>no head</body></html>"})
    assert decks[0]["title"] == "Module 11 — Ai Components"


def test_a_folder_with_no_index_html_is_skipped(app_module):
    app_module.w.files = FakeFiles({"03-feature-engineering": None})
    app_module.read_volume_file.cache_clear()
    app_module.list_decks.cache_clear()
    assert app_module.list_decks() == []


def test_deck_route_refuses_a_traversal_segment(app_module):
    app_module.w.files = FakeFiles({})
    client = app_module.app.test_client()
    assert client.get("/decks/../../etc/passwd").status_code in (404, 308)


def test_tutor_routes_answer_503_until_the_tutor_is_built(app_module):
    client = app_module.app.test_client()
    assert client.get("/api/tutor/me").status_code == 503


def test_the_shell_carries_the_course_title(app_module):
    client = app_module.app.test_client()
    body = client.get("/").get_data(as_text=True)
    assert "AI Cyber Bootcamp 2026" in body
    assert "__COURSE_TITLE__" not in body
