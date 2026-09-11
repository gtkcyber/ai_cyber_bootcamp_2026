"""The Keynote build: click stages, ODP surgery, media entries, PDF placement.

Everything but the last test runs without Docker on synthetic ODP fragments;
the integration test needs BOOTCAMP_KEYNOTE_DIR and a working `docker`.
"""

import copy
import os
import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

import pymupdf
import pytest

from keynote import odp
from keynote.build import flat_key, replace_pdf, table_losses
from keynote.media import box_of, youtube_entries
from keynote.model import BuildEvent, Deck, Drawable, Slide, Table, WebVideo
from keynote.stages import Stage, stages


def event(drawable, delivery="All at Once", kind="in"):
    return BuildEvent(drawable=drawable, type=kind, effect="BUKAnvil", delivery=delivery)


def drawable(identifier, x, y, w, h, z=0, angle=0.0, kind="ShapeInfoArchive"):
    return Drawable(identifier=identifier, kind=kind, x=x, y=y, width=w, height=h,
                    angle=angle, z=z)


def slide(number, drawables, chunks=(), **extra):
    fields = dict(identifier=f"s{number}", number=number, skipped=False, title="",
                  body=(), note="", drawables=tuple(drawables), chunks=tuple(chunks),
                  movies=(), web_videos=(), tables=())
    fields.update(extra)
    return Slide(**fields)


# ------------------------------------------------------------------ stages

def test_a_slide_without_builds_is_one_stage():
    assert stages(["a", "b"], []) == [Stage(frozenset({"a", "b"}))]


def test_built_objects_are_absent_until_their_click():
    result = stages(["a", "b", "c"], [(event("b"),), (event("c"),)])
    assert [set(s.visible) for s in result] == [{"a"}, {"a", "b"}, {"a", "b", "c"}]


def test_events_in_one_chunk_arrive_together():
    result = stages(["a", "b", "c"], [(event("b"), event("c"))])
    assert [set(s.visible) for s in result] == [{"a"}, {"a", "b", "c"}]


def test_a_build_out_removes_the_object_again():
    result = stages(["a", "b"], [(event("b", kind="out"),)])
    assert [set(s.visible) for s in result] == [{"a", "b"}, {"a"}]


def test_a_click_that_changes_nothing_adds_no_page():
    result = stages(["a"], [(event("a", kind="action"),)])
    assert len(result) == 1


def test_paragraph_delivery_counts_up_one_per_click():
    chunks = [(event("t", "By Paragraph"),)] * 3
    result = stages(["a", "t"], chunks)
    assert [s.paragraphs.get("t") for s in result] == [None, 1, 2, 3]
    assert all("t" in s.visible for s in result[1:])


def test_highlighted_bullet_delivery_is_paragraph_delivery():
    result = stages(["t"], [(event("t", "By Highlighted Bullet"),)] * 2)
    assert [s.paragraphs.get("t") for s in result] == [None, 1, 2]


# --------------------------------------------------------------- geometry

def test_lengths_convert_to_points():
    assert odp.points("1in") == 72
    assert odp.points("2.54cm") == pytest.approx(72)
    assert odp.points("10pt") == 10


def test_a_rotated_line_becomes_its_axis_aligned_box():
    # 80 points long, vertical: the box is zero wide, centred where it was.
    box = odp.drawable_box(drawable("l", 612.9, 778.9, 80.8, 0, angle=270))
    assert (box.x, box.y, box.width, box.height) == pytest.approx((653.3, 738.5, 0, 80.8), abs=0.01)


CM = odp.points("1cm")


def _element(xml):
    return ET.fromstring(
        f'<root xmlns:draw="{odp.NS["draw"]}" xmlns:svg="{odp.NS["svg"]}">{xml}</root>')[0]


def test_element_boxes_come_from_frames_lines_and_groups():
    frame = _element('<draw:frame svg:x="1cm" svg:y="2cm" svg:width="3cm" svg:height="4cm"/>')
    assert odp.element_box(frame) == odp.Box(*[odp.points(v) for v in ("1cm", "2cm", "3cm", "4cm")])
    line = _element('<draw:line svg:x1="3cm" svg:y1="1cm" svg:x2="1cm" svg:y2="1cm"/>')
    box = odp.element_box(line)
    assert (box.x, box.y, box.width, box.height) == pytest.approx((CM, CM, 2 * CM, 0))
    group = _element('<draw:g><draw:frame svg:x="0cm" svg:y="0cm" svg:width="1cm" svg:height="1cm"/>'
                     '<draw:frame svg:x="2cm" svg:y="3cm" svg:width="1cm" svg:height="1cm"/></draw:g>')
    assert odp.element_box(group) == odp.Box(0, 0, odp.points("3cm"), odp.points("4cm"))
    assert odp.element_box(_element("<draw:g/>")) is None


def test_matching_prefers_the_drawable_at_the_same_origin_and_size():
    shapes = [drawable("big", 100, 100, 300, 300), drawable("small", 100, 100, 50, 50),
              drawable("label", 100, 100, 0, 0)]
    assert odp.match_element(odp.Box(101, 100, 50, 51), shapes).identifier == "small"
    assert odp.match_element(odp.Box(100, 100, 300, 300), shapes).identifier == "big"
    # An auto-sized text shape stores no size; its frame has one.
    assert odp.match_element(odp.Box(100, 100, 120, 40), shapes).identifier == "label"


def test_matching_falls_back_to_the_smallest_containing_drawable():
    shapes = [drawable("big", 0, 0, 1000, 1000), drawable("box", 100, 100, 300, 300)]
    assert odp.match_element(odp.Box(150, 150, 20, 20), shapes).identifier == "box"
    assert odp.match_element(odp.Box(5000, 5000, 1, 1), shapes) is None


# ------------------------------------------------------------- odp pages

CONTENT = f'''<office:document-content xmlns:office="{odp.NS["office"]}" xmlns:draw="{odp.NS["draw"]}"
  xmlns:svg="{odp.NS["svg"]}" xmlns:text="{odp.NS["text"]}" xmlns:presentation="{odp.NS["presentation"]}">
<office:body><office:presentation>
<draw:page draw:name="page1">
  <draw:frame svg:x="1cm" svg:y="1cm" svg:width="2cm" svg:height="1cm"><draw:text-box><text:p>Title</text:p></draw:text-box></draw:frame>
  <draw:path svg:x="5cm" svg:y="5cm" svg:width="2cm" svg:height="2cm"/>
  <draw:frame svg:x="5cm" svg:y="5cm" svg:width="2cm" svg:height="2cm"><draw:text-box><text:p>Box</text:p></draw:text-box></draw:frame>
  <draw:frame svg:x="10cm" svg:y="5cm" svg:width="4cm" svg:height="4cm"><draw:text-box>
    <text:list><text:list-item><text:p>one</text:p></text:list-item><text:list-item><text:p>two</text:p></text:list-item></text:list>
    <text:p>three</text:p></draw:text-box></draw:frame>
  <presentation:notes><draw:page-thumbnail/></presentation:notes>
</draw:page>
<draw:page draw:name="page2"><draw:frame svg:x="1cm" svg:y="1cm" svg:width="2cm" svg:height="1cm"/></draw:page>
<draw:page draw:name="page3"><draw:frame svg:x="1cm" svg:y="1cm" svg:width="2cm" svg:height="1cm"/></draw:page>
</office:presentation></office:body></office:document-content>'''

def _deck_for_content():
    first = slide(1, [drawable("title", CM, CM, 2 * CM, CM), drawable("box", 5 * CM, 5 * CM, 2 * CM, 2 * CM),
                      drawable("text", 10 * CM, 5 * CM, 4 * CM, 4 * CM)],
                  chunks=[(event("box"),), (event("text", "By Paragraph"),),
                          (event("text", "By Paragraph"),), (event("text", "By Paragraph"),)])
    skipped = slide(None, [drawable("x", CM, CM, 2 * CM, CM)], skipped=True)
    last = slide(2, [drawable("y", CM, CM, 2 * CM, CM)])
    return [first, skipped, last]


def _pages(root):
    return root.find("office:body/office:presentation", odp.NS).findall("draw:page", odp.NS)


def test_expand_makes_one_page_per_stage_and_drops_skipped_slides():
    root = ET.fromstring(CONTENT)
    slides = _deck_for_content()
    stage_lists = [stages([d.identifier for d in s.drawables], s.chunks) for s in slides]
    records, losses = odp.expand(root, slides, stage_lists)
    assert losses == []
    assert [(r.slide, r.stage, r.stages) for r in records] == \
        [(1, 0, 5), (1, 1, 5), (1, 2, 5), (1, 3, 5), (1, 4, 5), (2, 0, 1)]
    pages = _pages(root)
    assert [p.get(odp._q("draw:name")) for p in pages] == \
        ["page1-s0", "page1-s1", "page1-s2", "page1-s3", "page1-s4", "page3"]
    # Stage 0: the box (path + label) and the text are off the canvas.
    assert [n.tag.split("}")[1] for n in odp.page_elements(pages[0])] == ["frame"]
    # Stage 1: the box's two elements are back.
    assert len(odp.page_elements(pages[1])) == 3
    # Stages 2..4: the text frame shows one, two, three paragraphs.
    for index, expected in ((2, ["one"]), (3, ["one", "two"]), (4, ["one", "two", "three"])):
        text = odp.page_elements(pages[index])[3]
        assert ["".join(p.itertext()) for p in text.iter(odp._q("text:p"))] == expected
    # The trimmed list keeps no empty items behind.
    assert len(list(odp.page_elements(pages[2])[3].iter(odp._q("text:list-item")))) == 1


def test_expand_reports_a_build_target_the_importer_did_not_draw():
    root = ET.fromstring(CONTENT)
    slides = _deck_for_content()
    ghost = drawable("ghost", 30 * CM, 30 * CM, CM, CM)
    slides[0] = slide(1, list(slides[0].drawables) + [ghost], chunks=[(event("ghost"),)])
    stage_lists = [stages([d.identifier for d in s.drawables], s.chunks) for s in slides]
    records, losses = odp.expand(root, slides, stage_lists)
    assert losses == [{"slide": 1, "kind": "build target",
                       "detail": "drawable ghost has no rendered element"},
                      {"slide": 1, "kind": "stage",
                       "detail": "stage 1 renders identically to an earlier one"}]
    assert [(r.slide, r.stage, r.stages) for r in records] == [(1, 0, 1), (2, 0, 1)]


def test_expand_refuses_a_page_count_that_does_not_match():
    root = ET.fromstring(CONTENT)
    with pytest.raises(ValueError):
        odp.expand(root, _deck_for_content()[:2], [[Stage(frozenset())]] * 2)


def test_bullets_are_patched():
    xml = ('<text:list-level-style-bullet text:bullet-char=""><style:text-properties '
           'fo:font-size="45%"/></text:list-level-style-bullet>')
    assert odp.patch_bullets(xml) == ('<text:list-level-style-bullet text:bullet-char="•">'
                                      '<style:text-properties fo:font-size="100%"/>'
                                      '</text:list-level-style-bullet>')


def test_write_odp_replaces_content_and_keeps_mimetype_first(tmp_path):
    import zipfile
    source = tmp_path / "a.odp"
    with zipfile.ZipFile(source, "w") as z:
        z.writestr("mimetype", "application/vnd.oasis.opendocument.presentation",
                   compress_type=zipfile.ZIP_STORED)
        z.writestr("content.xml", CONTENT)
        z.writestr("styles.xml", '<a text:bullet-char=""/>')
    root = odp.read_content(source)
    root.find("office:body/office:presentation", odp.NS).remove(_pages(root)[2])
    odp.write_odp(source, tmp_path / "b.odp", root)
    with zipfile.ZipFile(tmp_path / "b.odp") as z:
        assert z.namelist()[0] == "mimetype"
        assert z.read("content.xml").count(b"<draw:page ") == 2
        assert b'text:bullet-char="\xe2\x80\xa2"' in z.read("styles.xml")


# ------------------------------------------------------------------ media

def test_media_boxes_are_canvas_fractions():
    s = slide(3, [drawable("m", 192, 108, 960, 540, kind="MovieArchive")],
              web_videos=(WebVideo(drawable="m", url="https://youtu.be/abc", video_id="abc"),))
    assert box_of(s, "m") == [0.1, 0.1, 0.5, 0.5]
    assert youtube_entries(s) == [{"slide": 3, "kind": "youtube", "id": "abc",
                                   "box": [0.1, 0.1, 0.5, 0.5]}]


def test_tables_are_listed_as_losses():
    s = slide(4, [], tables=(Table(drawable="t", rows=3, columns=2, header_rows=1, header_columns=0),))
    deck = Deck(name="x", source=Path("x.key"), slides=(s, slide(None, [], skipped=True, tables=s.tables)))
    assert table_losses(deck) == [{"slide": 4, "kind": "table", "detail": "3x2 table not rendered"}]


def test_replace_pdf_drops_the_older_export_of_the_same_deck(tmp_path):
    (tmp_path / "slides").mkdir()
    (tmp_path / "slides" / "Module 10 Prompt Engineering.pdf").write_bytes(b"old")
    (tmp_path / "slides" / "Module 9 - Theory.pdf").write_bytes(b"other")
    new = tmp_path / "new.pdf"
    new.write_bytes(b"new")
    target = replace_pdf(tmp_path, "10-prompt-engineering", new, "Module 10 - Prompt Engineering.pdf")
    assert sorted(p.name for p in (tmp_path / "slides").glob("*.pdf")) == \
        ["Module 10 - Prompt Engineering.pdf", "Module 9 - Theory.pdf"]
    assert target.read_bytes() == b"new"


def test_flat_key_zips_the_package_with_relative_paths(tmp_path):
    import zipfile
    (tmp_path / "flat" / "Index").mkdir(parents=True)
    (tmp_path / "flat" / "Index" / "Slide-1.iwa").write_bytes(b"x")
    flat_key(tmp_path / "flat", tmp_path / "deck.key")
    with zipfile.ZipFile(tmp_path / "deck.key") as z:
        assert z.namelist() == ["Index/Slide-1.iwa"]


# ------------------------------------------------------------ integration

KEYNOTE_DIR = os.environ.get("BOOTCAMP_KEYNOTE_DIR")


@pytest.mark.skipif(not KEYNOTE_DIR or shutil.which("docker") is None,
                    reason="needs BOOTCAMP_KEYNOTE_DIR and docker")
def test_deck_11_builds_with_its_three_build_slides_staged(tmp_path):
    from keynote.build import build
    (tmp_path / "decks" / "assets").mkdir(parents=True)
    result = build(Path(KEYNOTE_DIR) / "Module 11 - AI Components.key", tmp_path, tmp_path / "work")
    assert (result["final_slides"], result["fragments"]) == (85, 13)
    assert result["losses"] == []
    manifest = (tmp_path / "databricks" / "keynote" / "11-ai-components.json").read_text()
    assert '"stages": 5' in manifest and '"stages": 6' in manifest
    with pymupdf.open(tmp_path / "slides" / "Module 11 - AI Components.pdf") as doc:
        assert doc.page_count == 98
