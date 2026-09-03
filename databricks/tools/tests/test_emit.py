"""Deck emission: one section per final slide, build stages as fragments."""

import re

from build_decks import UNRESOLVED, emit_deck


def _pages(kinds):
    from build_decks import group_ids
    return [{"page": n, "kind": k, "group": g, "text": f"page {n} words"}
            for n, (k, g) in enumerate(zip(kinds, group_ids(kinds)), start=1)]


def _emit(tmp_path, kinds, notes=None):
    path = emit_deck(tmp_path, "08-deep-learning", "Module 8: Deep Learning",
                     _pages(kinds), notes or {})
    return path.read_text(encoding="utf-8")


def test_the_file_lands_in_the_deck_directory(tmp_path):
    path = emit_deck(tmp_path, "08-deep-learning", "Module 8: Deep Learning",
                     _pages(["slide"]), {})
    assert path == tmp_path / "decks" / "08-deep-learning" / "index.html"
    assert path.is_file()


def test_one_section_per_final_slide(tmp_path):
    html = _emit(tmp_path, ["build", "build", "slide", "slide"])
    assert html.count("<section") == 2


def test_a_lone_slide_has_one_unfragmented_image(tmp_path):
    html = _emit(tmp_path, ["slide"])
    assert '<img class="page" src="pages/p001.webp"' in html
    assert "fragment" not in html


def test_build_stages_stack_with_the_finished_page_last(tmp_path):
    html = _emit(tmp_path, ["build", "build", "slide"])
    order = re.findall(r'<img class="(page(?: fragment)?)" src="pages/(p\d+\.webp)"', html)
    assert order == [("page", "p001.webp"),
                     ("page fragment", "p002.webp"),
                     ("page fragment", "p003.webp")]


def test_an_unsure_page_does_not_merge(tmp_path):
    html = _emit(tmp_path, ["unsure", "slide"])
    assert html.count("<section") == 2
    assert "fragment" not in html


def test_the_note_rides_in_an_aside(tmp_path):
    html = _emit(tmp_path, ["slide"], {1: "The note body."})
    assert '<aside class="notes">' in html
    assert "<p>The note body.</p>" in html


def test_the_note_is_keyed_by_the_final_page_of_the_group(tmp_path):
    html = _emit(tmp_path, ["build", "slide"], {2: "Keyed on page two."})
    assert "<p>Keyed on page two.</p>" in html


def test_unresolved_renders_as_a_visible_marker(tmp_path):
    html = _emit(tmp_path, ["slide"], {1: UNRESOLVED})
    assert f'<p class="unresolved">{UNRESOLVED}</p>' in html


def test_the_title_carries_the_course_name_and_an_em_dash(tmp_path):
    html = _emit(tmp_path, ["slide"])
    assert ("<title>AI Cyber Bootcamp 2026 &mdash; Module 8: Deep Learning</title>"
            in html)


def test_the_skeleton_links_the_shared_assets_and_pinned_reveal(tmp_path):
    html = _emit(tmp_path, ["slide"])
    assert "reveal.js@5.2.1/dist/reveal.js" in html
    assert '<link rel="stylesheet" href="../assets/course.css">' in html
    assert '<script src="../assets/deck.js"></script>' in html
    assert "CourseDeck.start();" in html


def test_every_image_carries_alt_text_from_the_page(tmp_path):
    html = _emit(tmp_path, ["slide"])
    assert 'alt="page 1 words"' in html


def test_alt_text_is_escaped(tmp_path):
    pages = [{"page": 1, "kind": "slide", "group": 1, "text": 'a < b & "c"'}]
    emit_deck(tmp_path, "08-x", "Module 8: X", pages, {})
    html = (tmp_path / "decks" / "08-x" / "index.html").read_text()
    assert 'alt="a &lt; b &amp; &quot;c&quot;"' in html


def test_the_section_carries_the_pdf_page_number_of_its_final_page(tmp_path):
    """The tutor reads data-page to know which PDF page is on screen."""
    html = _emit(tmp_path, ["build", "build", "slide"])
    assert '<section data-page="3">' in html


def test_data_page_is_the_finished_page_not_the_first_stage(tmp_path):
    html = _emit(tmp_path, ["build", "slide", "unsure", "slide"])
    assert re.findall(r'data-page="(\d+)"', html) == ["2", "3", "4"]
