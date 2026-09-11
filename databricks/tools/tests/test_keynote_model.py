"""Unit tests for the pure logic in keynote/, plus an integration test over the
real course decks (skipped unless BOOTCAMP_KEYNOTE_DIR points at their folder).
"""

import os
import re
import zipfile
from pathlib import Path

import pytest

from keynote.model import (
    BuildEvent,
    _data_path,
    _geometry,
    _kind,
    _paragraphs,
    _video_id,
    _web_video_key,
    build_chunks,
    build_registry,
    load_deck,
    slide_numbers,
)
from keynote.package import flatten


# --------------------------------------------------------------- slide_numbers


def test_slide_numbers_counts_only_non_skipped():
    assert slide_numbers([False, False, False]) == [1, 2, 3]


def test_slide_numbers_skipped_slides_get_none_and_do_not_advance():
    assert slide_numbers([False, True, False, True, True]) == [1, None, 2, None, None]


def test_slide_numbers_empty():
    assert slide_numbers([]) == []


# -------------------------------------------------------------------- _kind


@pytest.mark.parametrize("pbtype, expected", [
    ("TSWP.ShapeInfoArchive", "ShapeInfoArchive"),
    ("TSD.ImageArchive", "ImageArchive"),
    ("TSD.GroupArchive", "GroupArchive"),
    ("TSD.MovieArchive", "MovieArchive"),
    ("TST.TableInfoArchive", "TableInfoArchive"),
    ("KN.PlaceholderArchive", "PlaceholderArchive"),
    ("", ""),
])
def test_kind_strips_namespace(pbtype, expected):
    assert _kind(pbtype) == expected


# ----------------------------------------------------------------- _geometry


def test_geometry_found_at_top_level():
    obj = {"geometry": {"angle": 0.0, "position": {"x": 1, "y": 2}, "size": {"width": 3, "height": 4}}}
    assert _geometry(obj) == obj["geometry"]


def test_geometry_walks_nested_super_chain():
    geometry = {"angle": 0.0, "position": {"x": 1, "y": 2}, "size": {"width": 3, "height": 4}}
    obj = {"super": {"super": {"super": {"geometry": geometry}}}}
    assert _geometry(obj) == geometry


def test_geometry_missing_returns_empty_dict():
    assert _geometry({"super": {"super": {}}}) == {}
    assert _geometry({}) == {}


# ---------------------------------------------------------------- _paragraphs


def test_paragraphs_splits_on_newline():
    assert _paragraphs("one\ntwo\nthree") == ("one", "two", "three")


def test_paragraphs_drops_one_trailing_empty_from_final_newline():
    assert _paragraphs("one\ntwo\n") == ("one", "two")


def test_paragraphs_keeps_interior_blank_lines():
    assert _paragraphs("one\n\ntwo") == ("one", "", "two")


def test_paragraphs_empty_text():
    assert _paragraphs("") == ()


# ------------------------------------------------------------------ web video


def test_web_video_key_matches_any_extension_key_containing_web_video_info():
    obj = {"_pbtype": "TSD.ImageArchive", "[TSA.WebVideoInfo.web_video_info]": {"url": "x"}}
    assert _web_video_key(obj) == "[TSA.WebVideoInfo.web_video_info]"


def test_web_video_key_absent_for_a_plain_image():
    assert _web_video_key({"_pbtype": "TSD.ImageArchive", "data": {"identifier": "1"}}) is None


@pytest.mark.parametrize("url, expected", [
    ("https://www.youtube.com/watch?v=T_0MjD-UGaE", "T_0MjD-UGaE"),
    ("https://youtu.be/qxMi-tLg4MA", "qxMi-tLg4MA"),
    ("", None),
    (None, None),
    ("https://example.com/not-a-video", None),
])
def test_video_id_extraction(url, expected):
    assert _video_id(url) == expected


# ------------------------------------------------------------------- _data_path


def test_data_path_matches_identifier_suffixed_filename(tmp_path):
    (tmp_path / "Data").mkdir()
    (tmp_path / "Data" / "port_scan-3715.m4v").write_bytes(b"")
    (tmp_path / "Data" / "posterImage-3716.png").write_bytes(b"")
    assert _data_path(tmp_path, {"identifier": "3715"}).name == "port_scan-3715.m4v"
    assert _data_path(tmp_path, {"identifier": "3716"}).name == "posterImage-3716.png"


def test_data_path_does_not_match_a_longer_identifier(tmp_path):
    (tmp_path / "Data").mkdir()
    (tmp_path / "Data" / "port_scan-3715.m4v").write_bytes(b"")
    assert _data_path(tmp_path, {"identifier": "371"}) is None


def test_data_path_none_ref_returns_none(tmp_path):
    assert _data_path(tmp_path, None) is None


# ------------------------------------------------------------------ build_chunks


def _build_archive(identifier, drawable, effect, animation_type="In", delivery="All at Once"):
    return identifier, {
        "_pbtype": "KN.BuildArchive",
        "drawable": {"identifier": drawable},
        "delivery": delivery,
        "attributes": {"animationAttributes": {"effect": effect, "animationType": animation_type}},
    }


def _chunk_archive(identifier, build, automatic):
    return identifier, {
        "_pbtype": "KN.BuildChunkArchive",
        "build": {"identifier": build},
        "automatic": automatic,
    }


def test_build_chunks_groups_automatic_onto_the_preceding_click():
    """3 builds, 2 clicks: b1 on its own click, b2+b3 riding in with it."""
    registry = dict([
        _build_archive("b1", "d1", "com.apple.iWork.Keynote.BUKAnvil"),
        _build_archive("b2", "d2", "com.apple.iWork.Keynote.BUKAnvil"),
        _build_archive("b3", "d3", "com.apple.iWork.Keynote.BUKAnvil"),
        _chunk_archive("c1", "b1", automatic=False),
        _chunk_archive("c2", "b2", automatic=False),
        _chunk_archive("c3", "b3", automatic=True),
    ])
    slide = {"buildChunks": [{"identifier": "c1"}, {"identifier": "c2"}, {"identifier": "c3"}]}

    chunks = build_chunks(registry, slide)

    assert len(chunks) == 2
    assert chunks[0] == (BuildEvent("d1", "in", "com.apple.iWork.Keynote.BUKAnvil", "All at Once"),)
    assert chunks[1] == (
        BuildEvent("d2", "in", "com.apple.iWork.Keynote.BUKAnvil", "All at Once"),
        BuildEvent("d3", "in", "com.apple.iWork.Keynote.BUKAnvil", "All at Once"),
    )


def test_build_chunks_every_chunk_on_click_gives_one_event_per_chunk():
    """'By Paragraph' delivery: every bullet is its own click, per the course data."""
    registry = dict([
        _build_archive("b1", "d1", "apple:dropbuild", delivery="By Paragraph"),
        _chunk_archive("c1", "b1", automatic=False),
        _chunk_archive("c2", "b1", automatic=False),
        _chunk_archive("c3", "b1", automatic=False),
    ])
    slide = {"buildChunks": [{"identifier": "c1"}, {"identifier": "c2"}, {"identifier": "c3"}]}

    chunks = build_chunks(registry, slide)

    assert len(chunks) == 3
    assert all(len(chunk) == 1 for chunk in chunks)


def test_build_chunks_leading_automatic_defensively_starts_its_own_click():
    """Never observed in the course, but must not raise or drop the event."""
    registry = dict([
        _build_archive("b1", "d1", "com.apple.iWork.Keynote.BUKAnvil"),
        _chunk_archive("c1", "b1", automatic=True),
    ])
    slide = {"buildChunks": [{"identifier": "c1"}]}

    chunks = build_chunks(registry, slide)

    assert chunks == ((BuildEvent("d1", "in", "com.apple.iWork.Keynote.BUKAnvil", "All at Once"),),)


def test_build_chunks_no_builds_is_empty():
    assert build_chunks({}, {}) == ()


# --------------------------------------------------------------------- flatten


def _write_zip(path, entries):
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)


def test_flatten_directory_package_expands_index_zip_and_copies_data(tmp_path):
    package = tmp_path / "Deck.key"
    package.mkdir()
    _write_zip(package / "Index.zip", {
        "Index/Document.iwa": b"doc",
        "Index/Slide-1.iwa": b"slide",
        "Index/OperationStorage.iwa": b"drop-me",
        "Index/ActivityStream.iwa": b"drop-me",
        "Index/AnnotationAuthorStorage.iwa": b"drop-me",
    })
    (package / "Data").mkdir()
    (package / "Data" / "image-1.png").write_bytes(b"png")
    (package / "Metadata").mkdir()
    (package / "Metadata" / "Properties.plist").write_bytes(b"plist")

    workdir = tmp_path / "flat"
    result = flatten(package, workdir)

    assert result == workdir
    assert (workdir / "Index" / "Document.iwa").read_bytes() == b"doc"
    assert (workdir / "Index" / "Slide-1.iwa").read_bytes() == b"slide"
    assert (workdir / "Data" / "image-1.png").read_bytes() == b"png"
    assert (workdir / "Metadata" / "Properties.plist").read_bytes() == b"plist"
    assert not (workdir / "Index" / "OperationStorage.iwa").exists()
    assert not (workdir / "Index" / "ActivityStream.iwa").exists()
    assert not (workdir / "Index" / "AnnotationAuthorStorage.iwa").exists()


def test_flatten_single_file_key_extracts_top_level_paths_and_drops_extras(tmp_path):
    package = tmp_path / "Deck.key"
    _write_zip(package, {
        "Index/Document.iwa": b"doc",
        "Data/image-1.png": b"png",
        "Metadata/Properties.plist": b"plist",
        "Index/OperationStorage.iwa": b"drop-me",
        "preview.jpg": b"unwanted",
    })

    workdir = tmp_path / "flat"
    flatten(package, workdir)

    assert (workdir / "Index" / "Document.iwa").read_bytes() == b"doc"
    assert (workdir / "Data" / "image-1.png").read_bytes() == b"png"
    assert (workdir / "Metadata" / "Properties.plist").read_bytes() == b"plist"
    assert not (workdir / "Index" / "OperationStorage.iwa").exists()
    assert not (workdir / "preview.jpg").exists()


def test_flatten_is_idempotent_and_drops_stale_files(tmp_path):
    package = tmp_path / "Deck.key"
    _write_zip(package, {"Index/Document.iwa": b"v1"})
    workdir = tmp_path / "flat"
    flatten(package, workdir)
    (workdir / "stale.txt").write_text("leftover from a previous, different source")

    _write_zip(package, {"Index/Document.iwa": b"v2"})
    flatten(package, workdir)

    assert (workdir / "Index" / "Document.iwa").read_bytes() == b"v2"
    assert not (workdir / "stale.txt").exists()


# --------------------------------------------------------------- integration


KEYNOTE_DIR = os.environ.get("BOOTCAMP_KEYNOTE_DIR")

# Per common.md: 63 build events on 31 slides across 9 decks.
EXPECTED_TOTAL_EVENTS = 63
EXPECTED_BUILD_SLIDES = 31
EXPECTED_EFFECT_COUNTS = {
    "com.apple.iWork.Keynote.BUKAnvil": 43,
    "com.apple.iWork.Keynote.KLNSparkle": 2,
    "apple:dissolve character": 10,
    "apple:dropbuild": 1,
    "apple:movie-start": 3,
    "apple:web-video-start": 4,
}
EXPECTED_WEB_VIDEO_IDS = {"qxMi-tLg4MA", "T_0MjD-UGaE", "vOnwIbS998U", "xMYm2d9bmEA"}


_COURSE_KEY_RE = re.compile(r"^(Module \d+ - .+|Final Project)\.key$")


def _iter_key_files(directory: Path):
    """The 16 course source decks -- not the '<slug>.flat.key' scratch
    artifacts extract_notes.py's own flatten() left alongside them."""
    for entry in sorted(Path(directory).iterdir()):
        if _COURSE_KEY_RE.match(entry.name):
            yield entry


@pytest.mark.skipif(not KEYNOTE_DIR, reason="set BOOTCAMP_KEYNOTE_DIR to run against the real decks")
def test_course_inventory_matches_known_totals(tmp_path):
    """common.md's "63 build events" counts distinct KN.BuildArchive objects
    (one per effect applied to a drawable), not clicks or chunks: a "By
    Paragraph"/"By Highlighted Bullet" build fires across several chunks --
    one per paragraph/bullet, each its own click -- but is one build. Since a
    BuildEvent carries no build identifier, distinct (drawable, type, effect,
    delivery) tuples stand in for it; within one slide that is exactly the
    granularity of a KN.BuildArchive (a drawable never carries two builds
    with the same type+effect+delivery in this course)."""
    total_events = 0
    total_chunks = 0
    build_slides = 0
    effect_counts: dict[str, int] = {}
    web_video_ids: set[str] = set()

    for key_path in _iter_key_files(KEYNOTE_DIR):
        deck = load_deck(key_path, workdir=tmp_path / f"{key_path.stem}.flat")
        for slide in deck.slides:
            if not slide.chunks:
                continue
            build_slides += 1
            total_chunks += len(slide.chunks)
            distinct_events = {event for chunk in slide.chunks for event in chunk}
            total_events += len(distinct_events)
            for event in distinct_events:
                effect_counts[event.effect] = effect_counts.get(event.effect, 0) + 1
            for video in slide.web_videos:
                if video.video_id:
                    web_video_ids.add(video.video_id)

    assert total_events == EXPECTED_TOTAL_EVENTS
    assert build_slides == EXPECTED_BUILD_SLIDES
    assert effect_counts == EXPECTED_EFFECT_COUNTS
    assert web_video_ids == EXPECTED_WEB_VIDEO_IDS
    # 53 clicks (len(slide.chunks) summed): fewer than the 63 builds because
    # several BUKAnvil builds in 11-ai-components group multiple drawables
    # onto one click ("With Previous"/"After Previous"), offset by the 4- and
    # 6-chunk "By Paragraph"/"By Highlighted Bullet" builds each being
    # several clicks (one per paragraph/bullet), not one.
    assert total_chunks == 53


@pytest.mark.skipif(not KEYNOTE_DIR, reason="set BOOTCAMP_KEYNOTE_DIR to run against the real decks")
def test_registry_has_no_unresolved_identifiers_across_the_course(tmp_path):
    for key_path in _iter_key_files(KEYNOTE_DIR):
        workdir = flatten(key_path, tmp_path / f"{key_path.stem}.flat")
        registry = build_registry(workdir / "Index")
        unresolved = [i for i, o in registry.items() if o.get("_pbtype") == "keynote_parser.UnknownArchive"]
        assert unresolved == [], f"{key_path.name}: unresolved identifiers {unresolved}"
