"""Per-user conversation history as JSON files on the file backend."""
from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone

from tutor.files import FileBackend, MissingFile

logger = logging.getLogger(__name__)

_UNSAFE = re.compile(r"[^a-z0-9._-]")
CONV_ID_RE = re.compile(r"^[a-f0-9]{12}$")  # the shape uuid4().hex[:12] produces


def user_slug(email: str) -> str:
    return _UNSAFE.sub("_", email.lower())


def _valid_conv_id(conv_id) -> bool:
    return isinstance(conv_id, str) and bool(CONV_ID_RE.match(conv_id))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _title(question: str) -> str:
    return " ".join(question.split())[:60]


class SessionStore:
    def __init__(self, files: FileBackend, root: str):
        self.files = files
        self.root = root.rstrip("/")

    def _dir(self, user: str) -> str:
        return f"{self.root}/{user_slug(user)}"

    def _path(self, user: str, conv_id: str) -> str:
        # conv_id reaches here from a URL segment (safe: Flask's default
        # converter won't match "/") and from the JSON body of POST /chat
        # (unsafe: a "/" there is a legal string). Validating the shape
        # create() actually produces closes a path-traversal read of another
        # user's conversation file (e.g. "../<victim-slug>/<conv-id>").
        if not _valid_conv_id(conv_id):
            raise MissingFile(f"{self._dir(user)}/<invalid conversation id>")
        return f"{self._dir(user)}/{conv_id}.json"

    def list(self, user: str) -> list[dict]:
        summaries = []
        for name in self.files.list(self._dir(user)):
            if not name.endswith(".json"):
                continue
            path = f"{self._dir(user)}/{name}"
            try:
                conv = json.loads(self.files.read(path))
                summary = {
                    "id": conv["id"], "title": conv["title"],
                    "scope": conv["scope"], "updated": conv["updated"],
                }
            except (MissingFile, ValueError, KeyError) as e:
                logger.warning("skipping unreadable conversation %s: %s", path, e)
                continue
            summaries.append(summary)
        summaries.sort(key=lambda s: s["updated"], reverse=True)
        return summaries

    def create(self, user: str, scope: str) -> dict:
        now = _now_iso()
        conv = {
            "id": uuid.uuid4().hex[:12],
            "user": user,
            "scope": scope,
            "created": now,
            "updated": now,
            "title": "",
            "messages": [],
        }
        self._write(user, conv)
        return conv

    def get(self, user: str, conv_id: str) -> dict | None:
        try:
            path = self._path(user, conv_id)
            data = self.files.read(path)
        except MissingFile:
            return None
        try:
            return json.loads(data)
        except ValueError as e:
            logger.warning("skipping unreadable conversation %s: %s", path, e)
            return None

    def append(self, user: str, conv_id: str, question: str, answer: str, citations: list[dict]) -> dict:
        conv = self.get(user, conv_id)
        if conv is None:
            raise MissingFile(self._path(user, conv_id))
        now = _now_iso()
        if not conv["messages"]:
            conv["title"] = _title(question)
        conv["messages"].append({"role": "user", "content": question, "citations": [], "ts": now})
        conv["messages"].append({"role": "assistant", "content": answer, "citations": citations, "ts": now})
        conv["updated"] = now
        self._write(user, conv)
        return conv

    def delete(self, user: str, conv_id: str) -> None:
        try:
            path = self._path(user, conv_id)
        except MissingFile:
            return  # an invalid id never referred to a file; deleting nothing is correct
        self.files.delete(path)

    def _write(self, user: str, conv: dict) -> None:
        self.files.write(self._path(user, conv["id"]), json.dumps(conv, ensure_ascii=False).encode("utf-8"))
