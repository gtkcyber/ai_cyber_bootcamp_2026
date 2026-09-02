"""The tutor's knowledge: a skill library and the course's own material.

Spec decision 6: the tutor is an agent with a skill index in its prompt and a
load tool, not a retrieval system. Nothing here embeds, scores or ranks. The
index -- every skill's name and one-line description -- is small enough to ride
in every system prompt; the bodies are behind `load_skill`, `read_reference`,
`read_lab` and `read_deck_notes`, which the model calls when it needs them.

Two stores, because the app reads two:
  * skills, worksheets, answers -- workspace files, synced by the bundle
  * decks, conversations        -- the Unity Catalog app volume
"""
from __future__ import annotations

import difflib
import json
import re
from functools import lru_cache
from html.parser import HTMLParser

from tutor.files import FileBackend, MissingFile

# One tool result never costs the prompt more than this. Four calls at the cap
# is 48K characters, roughly 12K tokens, inside prompt.py's budget.
MAX_MATERIAL_CHARS = 12_000

_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _cap(text: str, what: str) -> str:
    if len(text) <= MAX_MATERIAL_CHARS:
        return text
    return text[:MAX_MATERIAL_CHARS] + f"\n\n[{what} truncated at {MAX_MATERIAL_CHARS} characters]"


def _suggest(name: str, candidates) -> str:
    close = difflib.get_close_matches(name, list(candidates), n=3, cutoff=0.5)
    return f" Closest names: {', '.join(close)}." if close else ""


class SkillLibrary:
    """The generated tutor-skills tree, read through a FileBackend.

    Startup reads exactly one file, `index.json`, written by
    databricks/tools/build_tutor_skills.py. Bodies are read on demand and
    cached, so a repeated `load_skill` in one conversation costs nothing.
    """

    def __init__(self, files: FileBackend, root: str, entries: list[dict]):
        self.files = files
        self.root = root.rstrip("/")
        self._entries = entries
        self._by_name = {e["name"]: e for e in entries}
        self.names = frozenset(self._by_name)
        self._read = lru_cache(maxsize=128)(self._read_uncached)

    @classmethod
    def load(cls, files: FileBackend, root: str) -> "SkillLibrary":
        root = root.rstrip("/")
        raw = files.read(f"{root}/index.json")
        entries = json.loads(raw.decode("utf-8"))
        if not entries:
            raise MissingFile(f"{root}/index.json is empty")
        return cls(files, root, entries)

    def index(self) -> list[dict]:
        """Name, kind and description of everything loadable. Goes in the prompt."""
        return [{"kind": e["kind"], "name": e["name"], "description": e["description"]}
                for e in self._entries]

    def _read_uncached(self, path: str) -> str:
        return self.files.read(f"{self.root}/{path}").decode("utf-8", "replace")

    def _entry(self, name: str, kind: str) -> dict:
        if not _SAFE_NAME.match(name or ""):
            raise MissingFile(f"not a valid {kind} name: {name!r}")
        entry = self._by_name.get(name)
        if entry is None or entry["kind"] != kind:
            raise MissingFile(
                f"no {kind} named {name!r}." + _suggest(name, (
                    e["name"] for e in self._entries if e["kind"] == kind)))
        return entry

    def load_skill(self, name: str) -> str:
        """A skill's body, frontmatter stripped."""
        text = self._read(self._entry(name, "skill")["path"])
        if text.startswith("---"):
            text = text.split("---", 2)[-1].lstrip("\n")
        return _cap(text, f"skill {name}")

    def read_reference(self, name: str) -> str:
        return _cap(self._read(self._entry(name, "reference")["path"]), f"reference {name}")


class _NotesParser(HTMLParser):
    """Pull `<aside class="notes">` text out of a reveal deck, page by page.

    A page number comes from the enclosing top-level `<section>`'s `data-page`
    when the deck builder emitted one, and from the section's 1-based ordinal
    when it did not -- these decks are one section per page, so the two agree.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.notes: list[tuple[int, str]] = []
        self._depth = 0
        self._page = 0
        self._in_notes = False
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self._depth += 1
            if self._depth == 1:
                page = attrs.get("data-page", "")
                self._page = int(page) if page.isdigit() else self._page + 1
        elif tag == "aside" and "notes" in (attrs.get("class") or "").split():
            self._in_notes = True
            self._buf = []

    def handle_startendtag(self, tag, attrs):
        if self._in_notes and tag == "br":
            self._buf.append(" ")

    def handle_endtag(self, tag):
        if tag == "aside" and self._in_notes:
            self._in_notes = False
            text = " ".join("".join(self._buf).split())
            if text:
                self.notes.append((self._page, text))
        elif tag == "section":
            self._depth = max(0, self._depth - 1)

    def handle_data(self, data):
        if self._in_notes:
            self._buf.append(data)


class CourseMaterial:
    """The bootcamp's own text: worksheet notebooks, answer notebooks, deck notes."""

    def __init__(self, files: FileBackend, labs_path: str, answers_path: str,
                 decks_path: str, deck_files: FileBackend):
        self.files = files
        self.labs_path = labs_path.rstrip("/")
        self.answers_path = answers_path.rstrip("/")
        self.decks_path = decks_path.rstrip("/")
        self.deck_files = deck_files
        self._notes = lru_cache(maxsize=32)(self._read_deck_notes_uncached)

    # --- decks -----------------------------------------------------------

    def _read_deck_notes_uncached(self, deck: str) -> tuple[tuple[int, str], ...]:
        if not _SAFE_NAME.match(deck or ""):
            raise MissingFile(f"not a valid deck id: {deck!r}")
        raw = self.deck_files.read(f"{self.decks_path}/{deck}/index.html")
        parser = _NotesParser()
        parser.feed(raw.decode("utf-8", "replace"))
        parser.close()
        return tuple(parser.notes)

    def read_deck_notes(self, deck: str) -> list[tuple[int, str]]:
        return list(self._notes(deck))

    def note_for_slide(self, deck: str, slide: int) -> str | None:
        for page, text in self._notes(deck):
            if page == slide:
                return text
        return None

    def render_deck_notes(self, deck: str) -> str:
        lines = [f"Slide {page}: {text}" for page, text in self._notes(deck)]
        return _cap("\n\n".join(lines) if lines else "This deck has no speaker notes.",
                    f"notes for {deck}")

    # --- labs ------------------------------------------------------------

    def _list(self, path: str) -> list[str]:
        return self.files.list(path)

    def _read_notebook_json(self, path: str) -> dict:
        return json.loads(self.files.read(path).decode("utf-8", "replace"))

    def _resolve(self, worksheet: str, root: str) -> str:
        """Match "4.2", a full filename, or any case variant of either."""
        if "/" in worksheet or ".." in worksheet:
            raise MissingFile(f"not a valid worksheet: {worksheet!r}")
        names = [n for n in self._list(root) if n.endswith(".ipynb")]
        wanted = worksheet.strip().lower()
        for name in names:
            if name.lower() == wanted:
                return f"{root}/{name}"
        number = wanted[:-6] if wanted.endswith(".ipynb") else wanted
        number = re.sub(r"^worksheet[_ ]", "", number)
        number = number.split("_", 1)[0]
        for name in names:
            if name.lower().startswith(f"worksheet_{number}_"):
                return f"{root}/{name}"
        available = sorted({re.sub(r"^Worksheet_([\d.]+)_.*", r"\1", n) for n in names})
        raise MissingFile(
            f"no worksheet {worksheet!r} under {root}. Available: {', '.join(available)}")

    def read_lab(self, worksheet: str, answers: bool = False) -> str:
        """A notebook as text: markdown and code cells, in order, outputs dropped.

        Answers are not secret in this course (spec decision 3), so
        `answers=True` reads the matching notebook from the answers tree.
        """
        root = self.answers_path if answers else self.labs_path
        path = self._resolve(worksheet, root)
        nb = self._read_notebook_json(path)
        parts = [f"# {path.rsplit('/', 1)[-1]}"]
        for cell in nb.get("cells", []):
            kind = cell.get("cell_type")
            if kind not in ("markdown", "code"):
                continue
            source = cell.get("source")
            body = "".join(source) if isinstance(source, list) else (source or "")
            if body.strip():
                parts.append(f"[{kind}]\n{body.rstrip()}")
        return _cap("\n\n".join(parts), f"notebook {path.rsplit('/', 1)[-1]}")
