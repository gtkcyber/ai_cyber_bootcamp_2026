"""The unresolved report is a handoff artifact: it goes to a person, so its
columns have to be greppable and its text has to be the slide's own words."""

import json

import pytest
from PIL import Image

from build_decks import UNRESOLVED
from check_decks import main, unresolved_rows


@pytest.fixture
def two_decks(tmp_path):
    for slug, page_text in (("02-a", "first deck slide words"),
                            ("03-b", "second deck slide words")):
        pages = tmp_path / "decks" / slug / "pages"
        pages.mkdir(parents=True)
        Image.new("RGB", (1600, 900), "white").save(pages / "p001.webp", "WEBP")
        meta = tmp_path / "databricks" / "pages"
        meta.mkdir(parents=True, exist_ok=True)
        (meta / f"{slug}.json").write_text(json.dumps({
            "slug": slug, "pdf": "x.pdf", "page_count": 1,
            "pages": [{"page": 1, "kind": "slide", "group": 1,
                       "text": page_text}]}))
        notes = tmp_path / "databricks" / "notes"
        notes.mkdir(parents=True, exist_ok=True)
        (notes / f"{slug}.md").write_text(f"## Page 1\n\n{UNRESOLVED}\n")
    return tmp_path


def test_every_deck_is_reported_in_slug_order(two_decks):
    rows = unresolved_rows(two_decks, ["02-a", "03-b"])
    assert [row[0] for row in rows] == ["02-a", "03-b"]


def test_a_resolved_note_does_not_appear(two_decks):
    (two_decks / "databricks" / "notes" / "02-a.md").write_text(
        "## Page 1\n\nA real note.\n")
    assert unresolved_rows(two_decks, ["02-a", "03-b"]) == [
        ("03-b", 1, "second deck slide words")]


def test_the_report_prints_and_exits_zero(two_decks, capsys):
    assert main(["--root", str(two_decks), "--unresolved"]) == 0
    out = capsys.readouterr().out
    assert "02-a\tp001\tfirst deck slide words" in out
    assert "03-b\tp001\tsecond deck slide words" in out
