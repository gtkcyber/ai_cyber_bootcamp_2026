"""The environment itself: the three libraries the deck tools need."""


def test_pdf_and_image_libraries_are_importable():
    import pymupdf
    from PIL import Image

    assert pymupdf.__version__.startswith("1.")
    assert hasattr(Image, "frombytes")


def test_pymupdf_cannot_write_webp():
    """Why Pillow is a dependency and not an optional extra.

    If a future PyMuPDF learns WebP this test fails and the render step can
    lose the Pillow round-trip.
    """
    import pymupdf
    import pytest

    pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 4, 4))
    with pytest.raises(ValueError):
        pixmap.tobytes("webp")
