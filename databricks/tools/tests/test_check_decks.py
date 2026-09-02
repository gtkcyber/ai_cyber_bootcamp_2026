"""The deck gate."""

import json

import pytest
from PIL import Image

from build_decks import UNRESOLVED
from check_decks import check_deck, main, unresolved_rows


@pytest.fixture
def deck(tmp_path):
    """A two-page deck: page 1 builds into page 2, one final slide."""
    slug = "08-deep-learning"
    pages_dir = tmp_path / "decks" / slug / "pages"
    pages_dir.mkdir(parents=True)
    for name in ("p001.webp", "p002.webp"):
        Image.new("RGB", (1600, 900), "white").save(pages_dir / name, "WEBP")

    meta = tmp_path / "databricks" / "pages"
    meta.mkdir(parents=True)
    (meta / f"{slug}.json").write_text(json.dumps({
        "slug": slug, "pdf": "Module 8 - Deep Learning.pdf", "page_count": 2,
        "pages": [
            {"page": 1, "kind": "build", "group": 1, "text": "first stage"},
            {"page": 2, "kind": "slide", "group": 1, "text": "finished slide"},
        ],
    }))

    notes = tmp_path / "databricks" / "notes"
    notes.mkdir(parents=True)
    (notes / f"{slug}.md").write_text("## Page 2\n\nA plain note body.\n")

    (tmp_path / "decks" / slug / "index.html").write_text(
        "<title>AI Cyber Bootcamp 2026 &mdash; Module 8: Deep Learning</title>\n"
        '<section><div class="page-stack">'
        '<img class="page" src="pages/p001.webp" alt="first stage">'
        '<img class="page fragment" src="pages/p002.webp" alt="finished slide">'
        '</div><aside class="notes"><p>A plain note body.</p></aside></section>\n')
    return tmp_path, slug


def test_a_clean_deck_has_no_failures_and_no_warnings(deck):
    root, slug = deck
    assert check_deck(root, slug) == ([], [])


def test_a_final_slide_with_no_note_fails(deck):
    root, slug = deck
    (root / "databricks" / "notes" / f"{slug}.md").write_text("")
    failures, _ = check_deck(root, slug)
    assert any("page 2" in f and "no note" in f for f in failures)


def test_unresolved_warns_during_authoring_and_fails_at_ship(deck):
    root, slug = deck
    (root / "databricks" / "notes" / f"{slug}.md").write_text(
        f"## Page 2\n\n{UNRESOLVED}\n")
    failures, warnings = check_deck(root, slug)
    assert failures == [] and any(UNRESOLVED in w for w in warnings)
    failures, _ = check_deck(root, slug, ship=True)
    assert any(UNRESOLVED in f for f in failures)


def test_the_prose_check_runs_on_the_notes(deck):
    root, slug = deck
    (root / "databricks" / "notes" / f"{slug}.md").write_text(
        "## Page 2\n\nThe fix for that's not different scales.\n")
    failures, _ = check_deck(root, slug)
    assert any("contracted verb" in f for f in failures)


def test_a_section_count_that_disagrees_with_the_grouping_fails(deck):
    root, slug = deck
    index = root / "decks" / slug / "index.html"
    index.write_text(index.read_text() + "<section></section>\n")
    failures, _ = check_deck(root, slug)
    assert any("section" in f for f in failures)


def test_a_missing_page_image_fails(deck):
    root, slug = deck
    (root / "decks" / slug / "pages" / "p002.webp").unlink()
    failures, _ = check_deck(root, slug)
    assert any("p002.webp" in f for f in failures)


def test_a_page_image_of_the_wrong_size_fails(deck):
    root, slug = deck
    path = root / "decks" / slug / "pages" / "p002.webp"
    Image.new("RGB", (1280, 720), "white").save(path, "WEBP")
    failures, _ = check_deck(root, slug)
    assert any("1280x720" in f for f in failures)


def test_a_wrong_title_fails(deck):
    root, slug = deck
    index = root / "decks" / slug / "index.html"
    index.write_text(index.read_text().replace("AI Cyber Bootcamp 2026", "Untitled"))
    failures, _ = check_deck(root, slug)
    assert any("title" in f for f in failures)


def test_unsure_pages_are_reported_as_warnings(deck):
    """An unsure page ends its group, so the deck becomes two slides."""
    root, slug = deck
    path = root / "databricks" / "pages" / f"{slug}.json"
    path.write_text(path.read_text().replace('"kind": "build"', '"kind": "unsure"'))
    (root / "decks" / slug / "index.html").write_text(
        "<title>AI Cyber Bootcamp 2026 &mdash; Module 8: Deep Learning</title>\n"
        '<section><div class="page-stack">'
        '<img class="page" src="pages/p001.webp" alt="first stage">'
        '</div><aside class="notes"><p>A note.</p></aside></section>\n'
        '<section><div class="page-stack">'
        '<img class="page" src="pages/p002.webp" alt="finished slide">'
        '</div><aside class="notes"><p>Another note.</p></aside></section>\n')
    (root / "databricks" / "notes" / f"{slug}.md").write_text(
        "## Page 1\n\nA note.\n\n## Page 2\n\nAnother note.\n")
    failures, warnings = check_deck(root, slug)
    assert failures == []
    assert any("unsure" in w for w in warnings)


def test_unresolved_rows_carry_the_slide_text(deck):
    root, slug = deck
    (root / "databricks" / "notes" / f"{slug}.md").write_text(
        f"## Page 2\n\n{UNRESOLVED}\n")
    assert unresolved_rows(root, [slug]) == [(slug, 2, "finished slide")]


def test_the_exit_code_is_the_failure_count(deck):
    root, slug = deck
    (root / "databricks" / "notes" / f"{slug}.md").write_text("")
    assert main(["--root", str(root), "--deck", slug]) == 1
    (root / "databricks" / "notes" / f"{slug}.md").write_text(
        "## Page 2\n\nA plain note body.\n")
    assert main(["--root", str(root), "--deck", slug]) == 0
