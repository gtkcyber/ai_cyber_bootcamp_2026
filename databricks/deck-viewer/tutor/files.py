"""Byte-level file access behind one small interface.

The app talks to a Unity Catalog volume through the Files API; tests and the
index builder talk to a local directory. Paths are always volume-shaped
(`/Volumes/<catalog>/<schema>/<volume>/...`); LocalFiles maps them under its base.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Protocol

from databricks.sdk.errors import NotFound


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
