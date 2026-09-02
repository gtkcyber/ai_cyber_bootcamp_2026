"""Databricks App: the AI Cyber Bootcamp 2026 deck viewer and its tutor.

Configuration (values come from the bundle's app resource config.env, see
../../databricks.yml; app.yaml carries only the command):

  DECKS_VOLUME_PATH    volume dir holding one folder per deck, each with an
                       index.html, e.g. /Volumes/ai_cyber_bootcamp/course/app/decks
  COURSE_TITLE         title shown in the app's top bar
  TUTOR_STATE_PATH     volume dir holding per-user conversation JSON
  TUTOR_CHAT_ENDPOINT  serving endpoint for chat
  TUTOR_SKILLS_PATH    workspace files dir holding the generated tutor-skills tree
  TUTOR_LABS_PATH      workspace files dir holding the worksheet notebooks
  TUTOR_ANSWERS_PATH   workspace files dir holding the answer notebooks
  TUTOR_HOME_LABS_DIR  folder name of a student's own lab copy under /Workspace/Users/<user>/
  TUTOR_DEV_USER       identity fallback with no forwarded header (local runs only)
"""
import html
import mimetypes
import os
import re
from functools import lru_cache
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound
from flask import Blueprint, Flask, Response, abort, jsonify

from tutor.fallback import setup_or_fallback

VOLUME_ROOT = os.environ["DECKS_VOLUME_PATH"].rstrip("/")
COURSE_TITLE = os.environ.get("COURSE_TITLE", "AI Cyber Bootcamp 2026")

app = Flask(__name__)
w = WorkspaceClient()

_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
_MODULE_RE = re.compile(r"^Module\s+(\d+)\s*:\s*(.+)$")


@lru_cache(maxsize=512)
def read_volume_file(path: str) -> bytes:
    resp = w.files.download(path)
    return resp.contents.read()


def _deck_label(folder: str, title: str | None) -> str:
    """Sidebar label for a deck.

    Deck titles are "AI Cyber Bootcamp 2026 — Module N: Name", so the segment
    after the em dash already carries its own module number; the Final Project's
    tail is just "Final Project" and is used as it stands. A deck with no <title>
    falls back to its folder slug.
    """
    if title:
        tail = title.rsplit("—", 1)[-1].strip() if "—" in title else title.strip()
        m = _MODULE_RE.match(tail)
        if m:
            return f"Module {int(m.group(1))} — {m.group(2).strip()}"
        if tail:
            return tail
    slug = re.sub(r"^\d+-", "", folder).replace("-", " ").strip().title()
    num = re.match(r"(\d+)", folder)
    return f"Module {int(num.group(1))} — {slug}" if num else slug


@lru_cache(maxsize=1)
def list_decks():
    decks = []
    for entry in w.files.list_directory_contents(VOLUME_ROOT):
        if not entry.is_directory:
            continue
        name = os.path.basename(entry.path.rstrip("/"))
        try:
            index = read_volume_file(f"{VOLUME_ROOT}/{name}/index.html")
        except NotFound:
            continue
        m = _TITLE_RE.search(index.decode("utf-8", "replace"))
        title = html.unescape(m.group(1)).strip() if m else None
        decks.append({"id": name, "title": _deck_label(name, title)})
    decks.sort(key=lambda d: d["id"])
    return decks


@app.route("/api/decks")
def api_decks():
    return jsonify(list_decks())


@app.route("/decks/<path:subpath>")
def serve_deck_file(subpath: str):
    if ".." in subpath.split("/"):
        abort(404)
    try:
        data = read_volume_file(f"{VOLUME_ROOT}/{subpath}")
    except NotFound:
        abort(404)
    mime = mimetypes.guess_type(subpath)[0] or "application/octet-stream"
    return Response(data, mimetype=mime)


_INDEX_HTML_PATH = Path(__file__).parent / "static" / "index.html"
try:
    INDEX_HTML = _INDEX_HTML_PATH.read_text(encoding="utf-8")
except FileNotFoundError as e:
    raise RuntimeError(
        f"App shell not found at {_INDEX_HTML_PATH}. "
        "Deploy static/index.html alongside app.py before starting the app."
    ) from e


@app.route("/")
def index():
    return INDEX_HTML.replace("__COURSE_TITLE__", html.escape(COURSE_TITLE))


def _setup_tutor_blueprint() -> Blueprint:
    raise NotImplementedError("the tutor is not wired up yet")


# A tutor-side failure -- a missing skills tree, a grant not yet propagated, a
# bad endpoint name -- must not take the deck viewer down with it. The viewer is
# the primary deliverable and works without the tutor. setup_or_fallback logs the
# failure and hands back a blueprint answering 503 on every /api/tutor route.
app.register_blueprint(setup_or_fallback(_setup_tutor_blueprint), url_prefix="/api/tutor")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("DATABRICKS_APP_PORT", 8000)))
