"""The shared deck runtime. These four files are copies; the test exists to
catch a recopy that silently reverts the canvas edits."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ASSETS = REPO_ROOT / "decks" / "assets"


def test_every_asset_is_present():
    for name in ("course.css", "deck.js",
                 "reveal-a11y/helper.css", "reveal-a11y/helper.js"):
        assert (ASSETS / name).is_file(), name


def test_the_canvas_is_sixteen_hundred_by_nine_hundred():
    source = (ASSETS / "deck.js").read_text()
    assert "var canvas = { w: 1600, h: 900 };" in source
    assert "width: 1600," in source
    assert "height: 900," in source
    assert "margin: 0," in source
    assert "960" not in source and "700," not in source


def test_the_global_is_still_coursedeck():
    source = (ASSETS / "deck.js").read_text()
    assert "window.CourseDeck = (function ()" in source
    assert "return { start: start, audit: audit, runGuard: runGuard };" in source


def test_the_stack_is_styled_for_both_the_deck_and_reading_mode():
    css = (ASSETS / "course.css").read_text()
    assert ".reveal .slides section .page-stack" in css
    assert "#reading .page-stack" in css
    assert ".page-stack .page" in css
    assert ".unresolved" in css
