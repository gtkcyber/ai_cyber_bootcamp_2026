"""Page rendering: fixed size, fixed names, byte-identical on a rerun.

The decks are committed to git, so a rebuild that produces different bytes
for unchanged input would show up as a diff on every page of every deck.
"""

import pymupdf
import pytest
from PIL import Image

from build_decks import PAGE_HEIGHT, PAGE_WIDTH, render_pages


@pytest.fixture
def two_page_pdf(tmp_path):
    """A 1920x1080 two-page PDF, the geometry every course export uses."""
    doc = pymupdf.open()
    for label in ("first", "second"):
        page = doc.new_page(width=1920, height=1080)
        page.insert_text((100, 200), label, fontsize=96)
    path = tmp_path / "sample.pdf"
    doc.save(path)
    doc.close()
    return path


def test_writes_one_webp_per_page_with_padded_names(two_page_pdf, tmp_path):
    written = render_pages(two_page_pdf, tmp_path / "pages")
    assert [p.name for p in written] == ["p001.webp", "p002.webp"]
    assert all(p.exists() for p in written)


def test_every_page_is_exactly_the_canvas_size(two_page_pdf, tmp_path):
    for path in render_pages(two_page_pdf, tmp_path / "pages"):
        with Image.open(path) as image:
            assert image.size == (PAGE_WIDTH, PAGE_HEIGHT)
            assert image.format == "WEBP"


def test_rerendering_produces_identical_bytes(two_page_pdf, tmp_path):
    first = [p.read_bytes() for p in render_pages(two_page_pdf, tmp_path / "a")]
    second = [p.read_bytes() for p in render_pages(two_page_pdf, tmp_path / "b")]
    assert first == second


def test_the_output_directory_is_created(two_page_pdf, tmp_path):
    target = tmp_path / "deep" / "nested" / "pages"
    render_pages(two_page_pdf, target)
    assert target.is_dir()
