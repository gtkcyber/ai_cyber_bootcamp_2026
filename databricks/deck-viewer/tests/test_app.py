import importlib
import re
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
        self.downloads = []
        self.listings = 0

    def list_directory_contents(self, path):
        self.listings += 1
        return [SimpleNamespace(path=f"{path}/{name}", is_directory=True) for name in self.decks]

    def download(self, path):
        self.downloads.append(path)
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
    app.clear_caches()
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
    app_module.clear_caches()
    assert app_module.list_decks() == []


# --- caches --------------------------------------------------------------

def test_a_deck_file_is_read_from_the_volume_only_once(app_module):
    _decks(app_module, {"00-introduction": _title("x")})
    before = len(app_module.w.files.downloads)
    app_module.read_volume_file(f"{DECKS}/00-introduction/index.html")
    assert len(app_module.w.files.downloads) == before


def test_the_deck_cache_evicts_the_oldest_once_it_passes_its_byte_cap(app_module, monkeypatch):
    """512 decks at 20 MB each would be 10 GB of app memory; bound the bytes."""
    monkeypatch.setattr(app_module, "DECK_CACHE_MAX_BYTES", 300)
    app_module.w.files = FakeFiles({name: b"x" * 100 for name in ("a", "b", "c", "d")})
    app_module.clear_caches()
    for name in ("a", "b", "c", "d"):
        app_module.read_volume_file(f"{DECKS}/{name}/index.html")
    assert app_module.deck_cache_bytes() <= 300
    before = len(app_module.w.files.downloads)
    app_module.read_volume_file(f"{DECKS}/a/index.html")  # evicted first
    assert len(app_module.w.files.downloads) == before + 1
    before = len(app_module.w.files.downloads)
    app_module.read_volume_file(f"{DECKS}/d/index.html")  # still resident
    assert len(app_module.w.files.downloads) == before


def test_a_file_bigger_than_the_whole_cap_is_served_but_not_cached(app_module, monkeypatch):
    monkeypatch.setattr(app_module, "DECK_CACHE_MAX_BYTES", 50)
    app_module.w.files = FakeFiles({"big": b"x" * 500})
    app_module.clear_caches()
    assert len(app_module.read_volume_file(f"{DECKS}/big/index.html")) == 500
    assert app_module.deck_cache_bytes() == 0


def test_the_deck_list_is_cached_between_requests(app_module):
    _decks(app_module, {"00-introduction": _title("x")})
    client = app_module.app.test_client()
    client.get("/api/decks")
    before = app_module.w.files.listings
    client.get("/api/decks")
    assert app_module.w.files.listings == before


def test_refresh_rereads_the_deck_list_and_the_deck_files(app_module):
    """A newly uploaded deck must not need an app restart to appear."""
    _decks(app_module, {"00-introduction": _title("x")})
    client = app_module.app.test_client()
    client.get("/api/decks")
    app_module.w.files.decks["01-exploratory-data-analysis"] = _title(
        "AI Cyber Bootcamp 2026 — Module 1: Exploratory Data Analysis")
    assert len(client.get("/api/decks").get_json()) == 1
    refreshed = client.get("/api/decks?refresh=1").get_json()
    assert [d["id"] for d in refreshed] == ["00-introduction", "01-exploratory-data-analysis"]
    assert app_module.deck_cache_bytes() > 0  # refilled by the listing it just did


def test_deck_route_refuses_a_traversal_segment(app_module):
    app_module.w.files = FakeFiles({})
    client = app_module.app.test_client()
    assert client.get("/decks/../../etc/passwd").status_code in (404, 308)


def test_a_skills_load_failure_still_leaves_the_deck_viewer_serving(app_module):
    """The tutor is an add-on; its setup failing must not take the viewer down.

    The app fixture's fake WorkspaceClient has no workspace API, so the real
    _setup_tutor_blueprint raises when it reads index.json -- which is the
    failure this asserts on, without needing to simulate one.
    """
    _decks(app_module, {"00-introduction":
                        _title("AI Cyber Bootcamp 2026 — Module 0: Introduction")})
    client = app_module.app.test_client()
    assert client.get("/api/tutor/me").status_code == 503
    assert client.get("/api/decks").get_json() == [
        {"id": "00-introduction", "title": "Module 0 — Introduction"}]


def test_the_tutor_blueprint_is_the_real_one_when_setup_succeeds(app_module, monkeypatch):
    from flask import Blueprint
    monkeypatch.setattr(app_module, "_setup_tutor_blueprint",
                        lambda: Blueprint("tutor", __name__))
    from tutor.fallback import setup_or_fallback
    bp = setup_or_fallback(app_module._setup_tutor_blueprint)
    assert bp.name == "tutor"
    assert not any("unavailable" in str(r) for r in bp.deferred_functions)


def test_the_shell_carries_the_course_title(app_module):
    client = app_module.app.test_client()
    body = client.get("/").get_data(as_text=True)
    assert "AI Cyber Bootcamp 2026" in body
    assert "__COURSE_TITLE__" not in body


def test_the_request_body_is_capped_at_64_kb(app_module):
    """Unset, Flask reads a body of any size before a route ever sees it."""
    assert app_module.app.config["MAX_CONTENT_LENGTH"] == 64 * 1024


def test_every_app_requirement_is_pinned():
    """tutor/llm.py hand-builds its OpenAI client because databricks-sdk 0.133's
    helper imports httpx while openai 3.x installs httpx2 instead. An unpinned
    resolve changes which versions meet, and that workaround with them."""
    lines = [ln.strip() for ln in (APP_DIR / "requirements.txt").read_text(
        encoding="utf-8").splitlines()]
    pins = [ln for ln in lines if ln and not ln.startswith("#")]
    assert {ln.split("==")[0].lower() for ln in pins} == {
        "flask", "gunicorn", "databricks-sdk", "openai"}
    for pin in pins:
        assert re.fullmatch(r"[A-Za-z0-9_.-]+==\d+(\.\d+)*", pin), f"{pin!r} is not pinned"


def test_a_media_range_request_is_served_from_one_cached_download(app_module):
    app_module.w.files = FakeFiles({"08-deep-learning": b"0123456789"})
    app_module.clear_caches()
    client = app_module.app.test_client()
    first = client.get("/decks/08-deep-learning/media/slide-012.mp4",
                       headers={"Range": "bytes=2-4"})
    second = client.get("/decks/08-deep-learning/media/slide-012.mp4",
                        headers={"Range": "bytes=5-"})
    assert (first.status_code, first.data) == (206, b"234")
    assert first.headers["Content-Range"] == "bytes 2-4/10"
    assert (second.status_code, second.data) == (206, b"56789")
    assert first.mimetype == "video/mp4"
    assert len(app_module.w.files.downloads) == 1


def test_a_deck_file_without_a_range_is_still_the_whole_file(app_module):
    app_module.w.files = FakeFiles({"08-deep-learning": _title("Module 8: Deep Learning")})
    app_module.clear_caches()
    r = app_module.app.test_client().get("/decks/08-deep-learning/index.html")
    assert r.status_code == 200
    assert b"<title>Module 8: Deep Learning</title>" in r.data
    assert r.headers["Accept-Ranges"] == "bytes"
