"""Decks built from a Keynote manifest: the manifest says which pages are
stages of one slide and where the movies and embeds sit."""

import json
import re

import pymupdf
import pytest

from build_decks import (build_deck, emit_deck, load_manifest, load_pages,
                         manifest_kinds, manifest_media, manifest_pages,
                         manifest_path, pages_path, pdf_for)

SLUG = "08-deep-learning"
PDF = "Module 8 - Deep Learning.pdf"


def _pdf(root, texts):
    (root / "slides").mkdir(exist_ok=True)
    doc = pymupdf.open()
    for body in texts:
        page = doc.new_page(width=1920, height=1080)
        page.insert_text((100, 200), body, fontsize=40)
    doc.save(root / "slides" / PDF)
    doc.close()


def _manifest(pages, media=()):
    return {"slug": SLUG, "source": "Module 8 - Deep Learning.key", "pdf": PDF,
            "page_count": len(pages), "media": list(media),
            "pages": [{"page": n, "slide": s, "stage": st, "stages": of}
                      for n, (s, st, of) in enumerate(pages, start=1)]}


def _write(root, manifest):
    path = manifest_path(root, SLUG)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


MOVIE = {"slide": 1, "kind": "movie", "src": "media/slide-001.mp4",
         "poster": "media/slide-001.webp", "box": [0.1, 0.2, 0.8, 0.6]}
CLIP = {"slide": 2, "kind": "youtube", "id": "qxMi-tLg4MA",
        "box": [0.25, 0.25, 0.5, 0.5]}

# Three pages whose words share nothing, so the text classifier would call
# them three slides; the manifest says the first two are one build.
UNRELATED = ("alpha beta gamma delta", "epsilon zeta eta theta",
             "iota kappa lambda mu")
TWO_THEN_ONE = [(1, 0, 2), (1, 1, 2), (2, 0, 1)]


def test_no_manifest_is_none(tmp_path):
    assert load_manifest(tmp_path, SLUG) is None


def test_a_manifest_loads_when_it_is_consistent(tmp_path):
    _write(tmp_path, _manifest(TWO_THEN_ONE, [MOVIE, CLIP]))
    assert load_manifest(tmp_path, SLUG)["page_count"] == 3


@pytest.mark.parametrize("broken", [
    lambda m: m["pages"].pop(),                              # page_count lies
    lambda m: m["pages"].__setitem__(1, {"page": 2, "slide": 1, "stage": 0, "stages": 2}),
    lambda m: m["pages"].__setitem__(2, {"page": 3, "slide": 0, "stage": 0, "stages": 1}),
    lambda m: m["media"].append({**MOVIE, "kind": "gif"}),
    lambda m: m["media"].append({**MOVIE, "slide": 9}),
    lambda m: m["media"].append({**MOVIE, "box": [0, 0, 2, 1]}),
    lambda m: m["media"].append({**MOVIE, "src": ""}),
    lambda m: m["media"].append({**CLIP, "id": ""}),
])
def test_an_inconsistent_manifest_is_refused(tmp_path, broken):
    manifest = _manifest(TWO_THEN_ONE)
    broken(manifest)
    _write(tmp_path, manifest)
    with pytest.raises(ValueError):
        load_manifest(tmp_path, SLUG)


def test_kinds_come_from_the_stage_position():
    assert manifest_kinds(_manifest(TWO_THEN_ONE)) == ["build", "slide", "slide"]


def test_manifest_pages_carry_the_slide_and_the_pdf_text(tmp_path):
    _pdf(tmp_path, UNRELATED)
    pages = manifest_pages(_manifest(TWO_THEN_ONE), tmp_path / "slides" / PDF)
    assert [(p["page"], p["kind"], p["group"], p["slide"]) for p in pages] == \
        [(1, "build", 1, 1), (2, "slide", 1, 1), (3, "slide", 2, 2)]
    assert pages[2]["text"] == "iota kappa lambda mu"


def test_a_pdf_of_the_wrong_length_is_refused(tmp_path):
    _pdf(tmp_path, UNRELATED[:2])
    with pytest.raises(ValueError):
        manifest_pages(_manifest(TWO_THEN_ONE), tmp_path / "slides" / PDF)


def test_media_are_keyed_by_slide():
    assert manifest_media(_manifest(TWO_THEN_ONE, [MOVIE, CLIP])) == {1: [MOVIE], 2: [CLIP]}


def test_build_deck_groups_by_the_manifest_not_the_words(tmp_path):
    _pdf(tmp_path, UNRELATED)
    _write(tmp_path, _manifest(TWO_THEN_ONE))
    result = build_deck(tmp_path, pdf_for(tmp_path, SLUG))
    assert (result["final_slides"], result["fragments"], result["manifest"]) == (2, 1, True)
    html = result["index"].read_text(encoding="utf-8")
    assert html.count("<section") == 2
    assert '<img class="page fragment" src="pages/p002.webp"' in html


def test_build_deck_rewrites_a_stale_classification_for_a_manifest_deck(tmp_path):
    _pdf(tmp_path, UNRELATED)
    _write(tmp_path, _manifest(TWO_THEN_ONE))
    stale = pages_path(tmp_path, SLUG)
    stale.parent.mkdir(parents=True)
    stale.write_text(json.dumps({"slug": SLUG, "pdf": PDF, "page_count": 1,
                                 "pages": [{"page": 1, "kind": "slide", "group": 1,
                                            "text": "old"}]}))
    build_deck(tmp_path, pdf_for(tmp_path, SLUG))
    payload = load_pages(tmp_path, SLUG)
    assert payload["manifest"] is True
    assert [p["kind"] for p in payload["pages"]] == ["build", "slide", "slide"]


def test_without_a_manifest_the_classification_is_still_preserved(tmp_path):
    _pdf(tmp_path, UNRELATED)
    build_deck(tmp_path, pdf_for(tmp_path, SLUG))
    kept = pages_path(tmp_path, SLUG)
    kept.write_text(kept.read_text().replace('"kind": "slide"', '"kind": "build"', 1))
    build_deck(tmp_path, pdf_for(tmp_path, SLUG))
    assert load_pages(tmp_path, SLUG)["pages"][0]["kind"] == "build"
    assert load_pages(tmp_path, SLUG)["manifest"] is False


def _emit(tmp_path, pages, media):
    path = emit_deck(tmp_path, SLUG, "Module 8: Deep Learning", pages, {}, media)
    return path.read_text(encoding="utf-8")


def _pages(spec):
    kinds = manifest_kinds(_manifest(spec))
    from build_decks import group_ids
    return [{"page": n, "kind": k, "group": g, "slide": s[0], "text": f"page {n}"}
            for n, (k, g, s) in enumerate(zip(kinds, group_ids(kinds), spec), start=1)]


def test_a_movie_rides_on_its_slide_as_lazy_video_with_poster_and_box(tmp_path):
    html = _emit(tmp_path, _pages([(1, 0, 1), (2, 0, 1)]), manifest_media(_manifest([(1, 0, 1), (2, 0, 1)], [MOVIE])))
    video = re.search(r"<video[^>]*>", html).group(0)
    assert 'class="media"' in video
    assert 'data-src="media/slide-001.mp4"' in video
    assert 'poster="media/slide-001.webp"' in video
    assert 'preload="none"' in video
    assert 'style="left:10.00%;top:20.00%;width:80.00%;height:60.00%"' in video
    assert html.count("<video") == 1
    assert html.index("<video") < html.index("<section", html.index("<section") + 1)


def test_a_youtube_clip_is_a_lazy_nocookie_iframe(tmp_path):
    html = _emit(tmp_path, _pages([(1, 0, 1), (2, 0, 1)]),
                 manifest_media(_manifest([(1, 0, 1), (2, 0, 1)], [CLIP])))
    frame = re.search(r"<iframe[^>]*>", html).group(0)
    assert 'data-src="https://www.youtube-nocookie.com/embed/qxMi-tLg4MA"' in frame
    assert 'loading="lazy"' in frame
    assert "allowfullscreen" in frame
    assert html.index("<iframe") > html.index("<section", html.index("<section") + 1)


def test_media_on_a_build_slide_arrive_with_the_finished_stage(tmp_path):
    spec = [(1, 0, 3), (1, 1, 3), (1, 2, 3)]
    html = _emit(tmp_path, _pages(spec), manifest_media(_manifest(spec, [MOVIE])))
    assert re.findall(r'data-fragment-index="(\d)"', html) == ["0", "1", "1"]
    assert 'class="media fragment"' in html
    assert re.search(r'<img class="page" src="pages/p001.webp" alt=', html)


def test_a_slide_without_media_keeps_the_unindexed_fragments(tmp_path):
    spec = [(1, 0, 2), (1, 1, 2)]
    html = _emit(tmp_path, _pages(spec), {})
    assert "data-fragment-index" not in html
    assert "media" not in html
