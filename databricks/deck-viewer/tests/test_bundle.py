"""The bundle ships the app's runtime files and nothing else.

`sync.paths` pulls the whole deck-viewer directory in, so every entry that is
not part of the running app has to be named in `sync.exclude`. A new file that
is neither runtime nor excluded fails here until someone classifies it.
"""
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
APP_DIR = REPO / "databricks" / "deck-viewer"
RUNTIME = {"app.py", "app.yaml", "ranges.py", "requirements.txt", "static", "tutor"}
IGNORED = {"__pycache__", ".venv", ".pytest_cache"}


def _excluded():
    return set(yaml.safe_load((REPO / "databricks.yml").read_text(encoding="utf-8"))["sync"]["exclude"])


def test_every_non_runtime_file_in_the_app_directory_is_excluded():
    excluded = _excluded()
    for entry in APP_DIR.iterdir():
        if entry.name in RUNTIME or entry.name in IGNORED:
            continue
        rel = f"databricks/deck-viewer/{entry.name}" + ("/" if entry.is_dir() else "")
        assert rel in excluded, f"{rel} would deploy with the app"


def test_the_runtime_files_are_not_excluded():
    excluded = _excluded()
    for name in RUNTIME:
        assert not any(x.rstrip("/").endswith(name) for x in excluded), name
