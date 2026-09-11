"""Run the whole app locally: local directories for the volume and workspace files.

    DATABRICKS_CONFIG_PROFILE=gtk-workspace .venv/bin/python local_run.py \
        --volume /path/to/fake/volume --workspace /path/to/fake/workspace

The model calls are real -- they go to the workspace serving endpoint through
the CLI profile's credentials -- so this exercises the tool loop, the prompt and
the routes end to end. Only the Databricks Apps runtime and its forwarded
identity headers are simulated, by TUTOR_DEV_USER.

Not deployed: the bundle's app source is app.py, and this file is a developer
entry point that lives beside it.
"""
import argparse
import logging
import mimetypes
import os
import sys
from pathlib import Path

from databricks.sdk import WorkspaceClient
from flask import Flask, abort, jsonify, request

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ranges import partial_response  # noqa: E402
from tutor.files import LocalFiles  # noqa: E402
from tutor.llm import Toolbox, Tutor  # noqa: E402
from tutor.routes import make_blueprint  # noqa: E402
from tutor.sessions import SessionStore  # noqa: E402
from tutor.skills import CourseMaterial, SkillLibrary  # noqa: E402
from tutor.throttle import Throttle  # noqa: E402


def build(volume: Path, workspace: Path, endpoint: str, dev_user: str) -> Flask:
    # Same reason as app.py: the per-answer usage line is the point of the run.
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    w = WorkspaceClient()
    vol = LocalFiles(volume)
    ws = LocalFiles(workspace)
    library = SkillLibrary.load(ws, "/tutor-skills")
    material = CourseMaterial(files=ws, labs_path="/notebooks", answers_path="/answers",
                              decks_path="/decks", deck_files=vol)
    tutor = Tutor.from_workspace(w, endpoint, Toolbox(library, material))

    app = Flask(__name__, static_folder="static", static_url_path="/static")

    @app.route("/")
    def index():
        html = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
        return html.replace("__COURSE_TITLE__", "AI Cyber Bootcamp 2026")

    @app.route("/api/decks")
    def decks():
        names = sorted(p.name for p in (volume / "decks").iterdir() if p.is_dir())
        return jsonify([{"id": n, "title": n} for n in names])

    @app.route("/decks/<path:subpath>")
    def deck_file(subpath):
        if ".." in subpath.split("/"):
            abort(404)
        p = volume / "decks" / subpath
        if not p.is_file():
            abort(404)
        return partial_response(p.read_bytes(),
                                mimetypes.guess_type(subpath)[0] or "application/octet-stream",
                                request.headers.get("Range"))

    app.register_blueprint(
        make_blueprint(library, material, tutor, SessionStore(vol, "/tutor_state"), Throttle(),
                       dev_user=dev_user, workspace_host=w.config.host,
                       labs_shared="/Workspace/Users/local/notebooks",
                       home_labs_dir="AI Cyber Bootcamp 2026", lab_exists=lambda p: False),
        url_prefix="/api/tutor")
    return app


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--volume", type=Path, required=True)
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--endpoint", default="databricks-deepseek-v4-flash-0731")
    ap.add_argument("--user", default=os.environ.get("TUTOR_DEV_USER", "dev@example.com"))
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    build(a.volume, a.workspace, a.endpoint, a.user).run(host="127.0.0.1", port=a.port)
