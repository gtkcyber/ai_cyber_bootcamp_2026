"""The command line: one deck or all of them, end to end on a synthetic PDF."""

import pymupdf
import pytest

from build_decks import build_deck, main, pdf_for


@pytest.fixture
def repo(tmp_path):
    """A repo-shaped tree with one three-page PDF whose pages 1-2 build."""
    (tmp_path / "slides").mkdir()
    doc = pymupdf.open()
    for body in ("alpha beta gamma delta",
                 "alpha beta gamma delta epsilon",
                 "wholly different words on this page entirely"):
        page = doc.new_page(width=1920, height=1080)
        page.insert_text((100, 200), body, fontsize=40)
    doc.save(tmp_path / "slides" / "Module 8 - Deep Learning.pdf")
    doc.close()
    return tmp_path


def test_pdf_for_finds_the_export_behind_a_slug(repo):
    assert pdf_for(repo, "08-deep-learning").name == "Module 8 - Deep Learning.pdf"


def test_an_unknown_slug_is_an_error(repo):
    with pytest.raises(ValueError):
        pdf_for(repo, "99-nope")


def test_build_deck_writes_pages_json_html_and_reports_counts(repo):
    result = build_deck(repo, pdf_for(repo, "08-deep-learning"))
    assert result["slug"] == "08-deep-learning"
    assert result["pdf_pages"] == 3
    assert result["final_slides"] == 2
    assert result["fragments"] == 1
    assert (repo / "databricks" / "pages" / "08-deep-learning.json").is_file()
    assert (repo / "decks" / "08-deep-learning" / "index.html").is_file()
    assert (repo / "decks" / "08-deep-learning" / "pages" / "p003.webp").is_file()


def test_a_second_build_keeps_a_hand_edited_classification(repo):
    build_deck(repo, pdf_for(repo, "08-deep-learning"))
    path = repo / "databricks" / "pages" / "08-deep-learning.json"
    path.write_text(path.read_text().replace('"kind": "build"', '"kind": "slide"'))
    result = build_deck(repo, pdf_for(repo, "08-deep-learning"))
    assert result["final_slides"] == 3
    assert result["fragments"] == 0


def test_deck_flag_builds_one_deck(repo):
    assert main(["--root", str(repo), "--deck", "08-deep-learning"]) == 0
    assert (repo / "decks" / "08-deep-learning" / "index.html").is_file()


def test_all_flag_builds_every_export(repo):
    assert main(["--root", str(repo), "--all"]) == 0


def test_neither_flag_is_a_usage_error(repo):
    with pytest.raises(SystemExit):
        main(["--root", str(repo)])
