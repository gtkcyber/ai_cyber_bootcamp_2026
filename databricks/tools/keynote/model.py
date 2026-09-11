"""Decode a flattened Keynote deck into a plain-Python model.

Uses keynote_parser's Python API directly -- `IWAFile.from_buffer(...).to_dict()`
on each Index/*.iwa file -- never the `keynote-parser` CLI and never a
pre-existing YAML dump, so the model always reflects the .key file on disk.
`IWAFile.from_file()` looks like the natural entry point but opens the file in
text mode and raises `UnicodeDecodeError` on real (binary, snappy-compressed)
.iwa data; every reader in keynote_parser's own file_utils.py opens `"rb"` and
calls `from_buffer()` instead, which is what this module does too.

Object graph
------------
A decoded .iwa file is `{"chunks": [{"archives": [{"header": {"identifier":
...}, "objects": [...]}]}]}`. Cross-references elsewhere in the document
(`{"identifier": "123"}`) are resolved against a single per-deck registry
built by merging every Index/*.iwa file, because a slide's own archives can be
split across more than one physical file and its drawables, builds and note
storage commonly live in whichever file happened to get the identifier.

A handful of archive segments hold more than one object for the same
identifier: Apple's diff format lets a later save patch an earlier one instead
of rewriting it whole. `keynote_parser.codec.ProtobufPatch` only handles a
patch with exactly one `diff_field_path` and raises on `fields_to_remove`
(codec.py's `FromString`); when that happens the segment falls back to an
`UnknownArchive` placeholder for that object rather than raising. This shows
up in this course in `Module 14 - Red Teaming AI.key`, where a `KN.SlideArchive`
carries two such unrecoverable patches that both target its `builds` (field 2)
and `buildChunks` (field 43). The registry keeps the first successfully
decoded object for an identifier and discards any `UnknownArchive` sharing
it -- confirmed correct by cross-checking the resulting build inventory
against the counts in the integration test below; ignoring the failed patches
does not lose any build in this course.

Slide order and skipping: `KN.ShowArchive.slideTree.slides` gives the show
order as a list of `KN.SlideNodeArchive` identifiers; `isSkipped` marks a
slide Keynote will not present, and `slide.identifier` is the actual
`KN.SlideArchive`. `Slide.number` is the 1-based position among slides where
`isSkipped` is false, `None` for a skipped slide -- but a skipped slide's own
builds still count in this course's known inventory, so it is decoded like
any other slide and simply carries no number.

Text: a slide's `titlePlaceholder`/`bodyPlaceholder` are themselves drawables
(`KN.PlaceholderArchive`, `kind` `kKindTitlePlaceholder`/`kKindBodyPlaceholder`)
whose `super.ownedStorage` identifies a `TSWP.StorageArchive`; its `text` field
is a list of runs (Keynote splits a paragraph into more than one run wherever
formatting changes within it) that concatenate into the full plain text, with
"\n" marking paragraph breaks. `note` is `KN.NoteArchive.containedStorage`,
resolved the same way but left as one string (a presenter note's internal line
breaks are not split into paragraphs here). `TSWP.StorageArchive.kind` is
`"NOTE"` for a note's storage and unset for everything else -- it does not
distinguish title from body, which is why title/body come from the
slide's own `titlePlaceholder`/`bodyPlaceholder` fields instead of scanning
every storage archive for a "Title"/"Body" `kind` (there isn't one).

Geometry: every drawable's base class (`TSD.GeometryArchive`) carries
`{position: {x, y}, size: {width, height}, angle, flags}`, stored directly
(no separate transform matrix was found anywhere in this course's decks;
`position`/`size`/`angle` are read as-is, on the 1920x1080-point canvas
common.md records). `flags` is a plain int32 with no enum in the bundled
schema and is not decoded here -- it is not read for position/size/angle, so
its bits (likely mirroring the `locked`/`aspectRatioLocked` booleans found
alongside it) do not affect this module's output. Each concrete archive type
wraps `geometry` a different number of `super` levels deep (observed:
`TSWP.ShapeInfoArchive` and `TSD.GroupArchive` at one level,
`KN.PlaceholderArchive` at three, because Apple models this as protobuf
message nesting rather than a flat inheritance chain). Rather than hardcode a
depth per type, `_geometry()` walks `obj["super"]` until it finds a dict
carrying a `"geometry"` key.

Chunks (click grouping): `KN.SlideArchive.buildChunks` is the slide's builds
in firing order, each a `KN.BuildChunkArchive` referencing one
`KN.BuildArchive` (an effect on a drawable: `attributes.animationAttributes`
carries `effect`, `animationType` -- `in`/`out`/`action`, taken verbatim
lowercased -- and `delay`/`duration`) via `build.identifier`, plus `delivery`
("All at Once", "By Paragraph", "By Highlighted Bullet", ...) directly on the
build. A chunk's own `automatic` flag is the click-grouping rule: `automatic`
false is a build that waits for an actual click and starts a new entry in
`Slide.chunks`; `automatic` true fires automatically alongside the nearest
preceding chunk ("With Previous"/"After Previous", which both play without a
further click and are not distinguished here) and is appended to that same
entry. `KN.BuildChunkArchive.referent` tracks the same thing in every case
observed in this course but one (a slide in 05-unsupervised-learning has a
chunk with `automatic=True, referent=True`), so `automatic` -- not `referent`
-- is what this module groups on. A build with "By Paragraph"/"By Highlighted
Bullet" delivery decomposes into one `KN.BuildChunkArchive` per paragraph/
bullet (`buildChunkIdentifier.buildChunkId` counts them, seen up to 6 in this
course) and each such follow-on chunk is itself `automatic=False`, i.e. each
paragraph/bullet is its own click -- so no special-casing of `delivery` is
needed beyond following `automatic` in `buildChunks` order.

Movies and web videos: an embedded movie is a `TSD.MovieArchive` drawable
whose `movieData`/`posterImageData` identifiers name files in `Data/` as
`<name>-<identifier>.<ext>`. A web video (YouTube embed) is not a distinct
archive type -- it is an ordinary `TSD.ImageArchive` (the thumbnail Keynote
shows in the deck) carrying an extension field whose to_dict() key contains
"WebVideoInfo", holding `url`/`attribution.externalUrl` and its own
`posterImageData` (in this course, the same identifier as the image's own
`data`, i.e. the thumbnail *is* the poster -- there is no separately fetched
video file). `video_id` is parsed from the URL's `v=` query parameter or a
`youtu.be/` path segment.

Tables: `TST.TableInfoArchive.tableModel` names a `TST.TableModelArchive`
carrying `numberOfRows`/`numberOfColumns`/`numberOfHeaderRows`/
`numberOfHeaderColumns`. Keynote omits the header fields entirely for a table
with zero header rows/columns (proto2 field presence), which this module
reads back as 0. The cells, sizes and look come from the archives under
`Index/Tables/` and are decoded by tables.py into `Table.grid`.
"""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from keynote_parser.codec import IWAFile

from keynote import tables
from keynote.package import SKIP_ARCHIVES, flatten

UNKNOWN_PBTYPE = "keynote_parser.UnknownArchive"

_YOUTUBE_ID_RE = re.compile(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{6,})")


# --------------------------------------------------------------- dataclasses


@dataclass(frozen=True)
class BuildEvent:
    drawable: str
    type: str
    effect: str
    delivery: str


@dataclass(frozen=True)
class Drawable:
    identifier: str
    kind: str
    x: float
    y: float
    width: float
    height: float
    angle: float
    z: int
    children: tuple[str, ...] = ()


@dataclass(frozen=True)
class Movie:
    drawable: str
    data_path: Optional[Path]
    poster_path: Optional[Path]


@dataclass(frozen=True)
class WebVideo:
    drawable: str
    url: str
    video_id: Optional[str]


@dataclass(frozen=True)
class Table:
    drawable: str
    rows: int
    columns: int
    header_rows: int
    header_columns: int
    grid: Optional[tables.Grid] = None


@dataclass(frozen=True)
class Slide:
    identifier: str
    number: Optional[int]
    skipped: bool
    title: str
    body: tuple[str, ...]
    note: str
    drawables: tuple[Drawable, ...]
    chunks: tuple[tuple[BuildEvent, ...], ...]
    movies: tuple[Movie, ...]
    web_videos: tuple[WebVideo, ...]
    tables: tuple[Table, ...]


@dataclass(frozen=True)
class Deck:
    name: str
    source: Path
    slides: tuple[Slide, ...]


# ------------------------------------------------------------------ registry


def _archives(iwa_dict: dict):
    for chunk in iwa_dict.get("chunks", []):
        for archive in chunk.get("archives", []):
            identifier = archive.get("header", {}).get("identifier")
            for obj in archive.get("objects", []):
                yield identifier, obj


def build_registry(index_dir: Path) -> dict[str, dict]:
    """One identifier -> decoded-object dict, merged across Index/**/*.iwa.

    Index/Tables/ holds the table cell storage (tiles, string tables, header
    buckets) and is read too; nothing else lives below Index/.
    """
    registry: dict[str, dict] = {}
    for path in sorted(Path(index_dir).rglob("*.iwa")):
        if f"Index/{path.name}" in SKIP_ARCHIVES:
            continue
        data = IWAFile.from_buffer(path.read_bytes(), str(path)).to_dict()
        for identifier, obj in _archives(data):
            existing = registry.get(identifier)
            is_unknown = obj.get("_pbtype") == UNKNOWN_PBTYPE
            if is_unknown:
                registry.setdefault(identifier, obj)
                continue
            if existing is None or existing.get("_pbtype") == UNKNOWN_PBTYPE:
                registry[identifier] = obj
    return registry


# ------------------------------------------------------------------- helpers


def _kind(pbtype: str) -> str:
    return pbtype.rsplit(".", 1)[-1] if pbtype else ""


def _geometry(obj) -> dict:
    while isinstance(obj, dict):
        geometry = obj.get("geometry")
        if geometry is not None:
            return geometry
        obj = obj.get("super")
    return {}


def _paragraphs(text: str) -> tuple[str, ...]:
    if not text:
        return ()
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return tuple(parts)


def _storage_text(registry: dict, ref) -> str:
    if not ref:
        return ""
    storage = registry.get(ref["identifier"])
    if not storage:
        return ""
    return "".join(storage.get("text") or [])


def _placeholder_text(registry: dict, ref) -> str:
    if not ref:
        return ""
    placeholder = registry.get(ref["identifier"])
    if not placeholder:
        return ""
    storage_ref = placeholder.get("super", {}).get("ownedStorage")
    return _storage_text(registry, storage_ref)


def _note_text(registry: dict, ref) -> str:
    if not ref:
        return ""
    note = registry.get(ref["identifier"])
    if not note:
        return ""
    return _storage_text(registry, note.get("containedStorage"))


def _data_path(workdir: Path, ref) -> Optional[Path]:
    if not ref:
        return None
    matches = sorted((workdir / "Data").glob(f"*-{ref['identifier']}.*"))
    return matches[0] if matches else None


def _video_id(url: str) -> Optional[str]:
    if not url:
        return None
    match = _YOUTUBE_ID_RE.search(url)
    return match.group(1) if match else None


def _web_video_key(obj: dict) -> Optional[str]:
    return next((key for key in obj if "WebVideoInfo" in key), None)


def _drawable(registry: dict, identifier: str, z: int) -> Drawable:
    obj = registry[identifier]
    geometry = _geometry(obj)
    position = geometry.get("position", {})
    size = geometry.get("size", {})
    children = tuple(child["identifier"] for child in (obj.get("children") or []))
    return Drawable(
        identifier=identifier,
        kind=_kind(obj.get("_pbtype", "")),
        x=position.get("x", 0.0),
        y=position.get("y", 0.0),
        width=size.get("width", 0.0),
        height=size.get("height", 0.0),
        angle=geometry.get("angle", 0.0),
        z=z,
        children=children,
    )


def _movie(workdir: Path, identifier: str, obj: dict) -> Movie:
    return Movie(
        drawable=identifier,
        data_path=_data_path(workdir, obj.get("movieData")),
        poster_path=_data_path(workdir, obj.get("posterImageData")),
    )


def _web_video(identifier: str, obj: dict, key: str) -> WebVideo:
    info = obj[key]
    url = info.get("url") or info.get("attribution", {}).get("externalUrl", "")
    return WebVideo(drawable=identifier, url=url, video_id=_video_id(url))


def _table(registry: dict, identifier: str, obj: dict) -> Table:
    model_ref = obj.get("tableModel")
    table_model = registry[model_ref["identifier"]] if model_ref else {}
    return Table(
        drawable=identifier,
        rows=table_model.get("numberOfRows") or 0,
        columns=table_model.get("numberOfColumns") or 0,
        header_rows=table_model.get("numberOfHeaderRows") or 0,
        header_columns=table_model.get("numberOfHeaderColumns") or 0,
        grid=tables.decode(registry, table_model) if table_model else None,
    )


def build_chunks(registry: dict, slide_obj: dict) -> tuple[tuple[BuildEvent, ...], ...]:
    """The slide's click steps, grouped per the rule in the module docstring."""
    chunk_refs = [c["identifier"] for c in (slide_obj.get("buildChunks") or [])]
    clicks: list[list[BuildEvent]] = []
    for chunk_id in chunk_refs:
        chunk = registry[chunk_id]
        build = registry[chunk["build"]["identifier"]]
        attributes = build.get("attributes", {}) or {}
        animation = attributes.get("animationAttributes", {}) or {}
        event = BuildEvent(
            drawable=build.get("drawable", {}).get("identifier", ""),
            type=(animation.get("animationType") or "").lower(),
            effect=animation.get("effect") or "",
            delivery=build.get("delivery") or "",
        )
        if not chunk.get("automatic") or not clicks:
            clicks.append([event])
        else:
            clicks[-1].append(event)
    return tuple(tuple(click) for click in clicks)


def slide_numbers(skipped_flags: list[bool]) -> list[Optional[int]]:
    """1-based position among non-skipped slides, in show order; None if skipped."""
    numbers: list[Optional[int]] = []
    number = 0
    for skipped in skipped_flags:
        if not skipped:
            number += 1
        numbers.append(None if skipped else number)
    return numbers


def _slide(registry: dict, workdir: Path, node_obj: dict, number: Optional[int]) -> Slide:
    slide_identifier = node_obj["slide"]["identifier"]
    slide_obj = registry[slide_identifier]

    z_order = [d["identifier"] for d in (slide_obj.get("drawablesZOrder") or [])]
    drawables = tuple(_drawable(registry, identifier, z) for z, identifier in enumerate(z_order))

    movies: list[Movie] = []
    web_videos: list[WebVideo] = []
    tables: list[Table] = []
    for identifier in z_order:
        obj = registry[identifier]
        webvideo_key = _web_video_key(obj)
        if webvideo_key:
            web_videos.append(_web_video(identifier, obj, webvideo_key))
        elif obj.get("_pbtype") == "TSD.MovieArchive":
            movies.append(_movie(workdir, identifier, obj))
        elif obj.get("_pbtype") == "TST.TableInfoArchive":
            tables.append(_table(registry, identifier, obj))

    return Slide(
        identifier=slide_identifier,
        number=number,
        skipped=bool(node_obj.get("isSkipped")),
        title=_placeholder_text(registry, slide_obj.get("titlePlaceholder")),
        body=_paragraphs(_placeholder_text(registry, slide_obj.get("bodyPlaceholder"))),
        note=_note_text(registry, slide_obj.get("note")),
        drawables=drawables,
        chunks=build_chunks(registry, slide_obj),
        movies=tuple(movies),
        web_videos=tuple(web_videos),
        tables=tuple(tables),
    )


# --------------------------------------------------------------------- load


def load_deck(key_path: Path, workdir: Optional[Path] = None) -> Deck:
    """Decode `key_path` (directory package or single-file .key) into a Deck.

    `workdir` is where the flattened package is written (see `package.flatten`).
    When omitted, a fresh directory under the system temp dir is used and left
    on disk after this call returns -- not cleaned up -- because
    `Movie.data_path`/`Movie.poster_path` must remain valid to the caller.
    """
    key_path = Path(key_path)
    if workdir is None:
        workdir = Path(tempfile.mkdtemp(prefix=f"keynote-{key_path.stem}-"))
    workdir = flatten(key_path, workdir)

    registry = build_registry(workdir / "Index")
    show = next(obj for obj in registry.values() if obj.get("_pbtype") == "KN.ShowArchive")
    node_ids = [s["identifier"] for s in show["slideTree"]["slides"]]

    node_objs = [registry[node_id] for node_id in node_ids]
    numbers = slide_numbers([bool(obj.get("isSkipped")) for obj in node_objs])
    slides = [
        _slide(registry, workdir, node_obj, number)
        for node_obj, number in zip(node_objs, numbers)
    ]

    return Deck(name=key_path.stem, source=key_path, slides=tuple(slides))
