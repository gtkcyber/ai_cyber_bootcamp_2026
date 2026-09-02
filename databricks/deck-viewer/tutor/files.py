"""Byte-level file access behind one small interface.

Three backends. The app reads decks and writes conversation state on a Unity
Catalog volume through the Files API (`VolumeFiles`); it reads the tutor's
skills, the worksheets and the answers out of workspace files, which are on no
volume, through the workspace API (`WorkspaceTextFiles`); tests and local runs
use a directory (`LocalFiles`). Paths are always store-shaped
(`/Volumes/<catalog>/<schema>/<volume>/...` or `/Workspace/...`); LocalFiles
maps them under its base.
"""
from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Protocol

from databricks.sdk.errors import DatabricksError, NotFound


class MissingFile(Exception):
    """Read of a path that does not exist, on either backend."""


class FileBackend(Protocol):
    def read(self, path: str) -> bytes: ...
    def write(self, path: str, data: bytes) -> None: ...
    def list(self, path: str) -> list[str]: ...
    def delete(self, path: str) -> None: ...
    def exists(self, path: str) -> bool: ...


class LocalFiles:
    def __init__(self, base: Path):
        self.base = Path(base)

    def _p(self, path: str) -> Path:
        return self.base / path.lstrip("/")

    def read(self, path: str) -> bytes:
        try:
            return self._p(path).read_bytes()
        except FileNotFoundError as e:
            raise MissingFile(path) from e

    def write(self, path: str, data: bytes) -> None:
        p = self._p(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def list(self, path: str) -> list[str]:
        p = self._p(path)
        if not p.is_dir():
            return []
        return sorted(c.name for c in p.iterdir() if c.is_file())

    def delete(self, path: str) -> None:
        p = self._p(path)
        if p.is_file():
            p.unlink()

    def exists(self, path: str) -> bool:
        return self._p(path).is_file()


class VolumeFiles:
    """A UC volume through the workspace Files API, as whichever principal `w` is."""

    def __init__(self, w):
        self.w = w

    def read(self, path: str) -> bytes:
        try:
            return self.w.files.download(path).contents.read()
        except NotFound as e:
            raise MissingFile(path) from e

    def write(self, path: str, data: bytes) -> None:
        self.w.files.create_directory(path.rsplit("/", 1)[0])
        self.w.files.upload(path, io.BytesIO(data), overwrite=True)

    def list(self, path: str) -> list[str]:
        try:
            entries = self.w.files.list_directory_contents(path)
            return sorted(e.name for e in entries if not e.is_directory)
        except NotFound:
            return []

    def delete(self, path: str) -> None:
        try:
            self.w.files.delete(path)
        except NotFound:
            pass

    def exists(self, path: str) -> bool:
        try:
            self.w.files.get_metadata(path)
            return True
        except NotFound:
            return False


class WorkspaceTextFiles:
    """Workspace files (`/Workspace/...`) through the workspace API, read-only.

    The bundle syncs the tutor's skills, the worksheets and the answers into
    `${workspace.file_path}`; none of them is on a volume, so `VolumeFiles`
    cannot reach them. Nothing in the app writes to workspace files -- the
    bundle owns that tree -- so `write` and `delete` raise rather than
    pretending to be a general backend.

    `export` is the only read call there is: databricks-sdk 0.133 has no
    `WorkspaceAPI.download`, and export hands back the bytes base64-encoded in
    `ExportResponse.content`. A notebook is asked for as JUPYTER, which is the
    format `CourseMaterial.read_lab` parses as JSON; anything else, and a
    notebook the workspace holds as a plain file rather than a notebook object,
    goes through AUTO.
    """

    def __init__(self, w):
        self.w = w

    def _export(self, path: str, fmt) -> bytes:
        return base64.b64decode(self.w.workspace.export(path, format=fmt).content)

    def read(self, path: str) -> bytes:
        from databricks.sdk.service.workspace import ExportFormat
        if not path.endswith(".ipynb"):
            try:
                return self._export(path, ExportFormat.AUTO)
            except NotFound as e:
                raise MissingFile(path) from e
        try:
            return self._export(path, ExportFormat.JUPYTER)
        except NotFound as e:
            raise MissingFile(path) from e
        except DatabricksError:
            try:
                return self._export(path, ExportFormat.AUTO)
            except NotFound as e:
                raise MissingFile(path) from e

    def write(self, path: str, data: bytes) -> None:
        raise NotImplementedError("the app never writes to workspace files; the bundle owns that tree")

    def list(self, path: str) -> list[str]:
        try:
            return sorted(e.path.rsplit("/", 1)[-1] for e in self.w.workspace.list(path))
        except NotFound:
            return []

    def delete(self, path: str) -> None:
        raise NotImplementedError("the app never writes to workspace files; the bundle owns that tree")

    def exists(self, path: str) -> bool:
        try:
            self.w.workspace.get_status(path)
            return True
        except NotFound:
            return False
