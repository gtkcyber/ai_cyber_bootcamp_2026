"""Build-stage classification.

The rule and its thresholds come from measuring the real exports: see the
"What the PDFs actually are" section of the decks plan. The short version is
that Keynote did not export position-stable build stages, so the only durable
signal is that every word of the earlier page survives on the later one and
the later one says more.
"""

import json

import pymupdf
import pytest

from build_decks import (classify_pages, final_pages, group_ids, load_pages,
                         pages_path, save_pages)


def _pdf(tmp_path, page_texts, name="sample.pdf"):
    """One 1920x1080 page per string.

    The words are wrapped six to a line: insert_text does not wrap, and a line
    that runs off the page edge is clipped, so a 26-word page written as one
    line extracts as 15 words and every token count in these tests would be
    wrong.
    """
    doc = pymupdf.open()
    for body in page_texts:
        page = doc.new_page(width=1920, height=1080)
        words = body.split()
        lines = [" ".join(words[i:i + 6]) for i in range(0, len(words), 6)]
        page.insert_text((100, 200), lines, fontsize=40)
    path = tmp_path / name
    doc.save(path)
    doc.close()
    return path


def test_a_page_whose_words_all_survive_and_grow_a_little_is_a_build(tmp_path):
    pdf = _pdf(tmp_path, [
        "series value counts default binning",
        "series value counts default binning with bins five",
    ])
    assert [p["kind"] for p in classify_pages(pdf)] == ["build", "slide"]


def test_an_unrelated_next_page_is_a_new_slide(tmp_path):
    pdf = _pdf(tmp_path, [
        "series value counts default binning",
        "correlation between two datasets entirely different words here",
    ])
    assert [p["kind"] for p in classify_pages(pdf)] == ["slide", "slide"]


def test_a_title_card_swallowed_by_a_full_slide_is_unsure(tmp_path):
    """Module 8's 'Convolutional Neural Networks' page into its content page.

    Section break or build stage is not decidable from the PDF, so a human
    rules on it.
    """
    pdf = _pdf(tmp_path, [
        "convolutional neural networks",
        "convolutional neural networks handling high dimensional image inputs "
        "with filters pooling and a fully connected classifier at the end of "
        "the pipeline which reduces parameters enormously",
    ])
    assert classify_pages(pdf)[0]["kind"] == "unsure"


def test_a_partly_reflowed_stage_is_unsure(tmp_path):
    """Containment lands between the two thresholds when the author reflowed."""
    pdf = _pdf(tmp_path, [
        "alpha beta gamma delta epsilon zeta eta theta iota kappa",
        "alpha beta gamma delta epsilon zeta eta theta lambda mu nu xi",
    ])
    assert classify_pages(pdf)[0]["kind"] == "unsure"


def test_a_shrinking_page_is_never_a_build(tmp_path):
    pdf = _pdf(tmp_path, [
        "alpha beta gamma delta epsilon zeta eta theta",
        "alpha beta gamma",
    ])
    assert classify_pages(pdf)[0]["kind"] == "slide"


def test_deck_wide_chrome_does_not_make_two_slides_look_alike(tmp_path):
    """'GTK Cyber' is on every page of fifteen decks. Counting it as content
    would make every short page look like a stage of the next one."""
    pdf = _pdf(tmp_path, [
        "GTK Cyber",
        "GTK Cyber loading a dataframe from a table",
        "GTK Cyber plotting a histogram of one column",
        "GTK Cyber merging two frames on a shared key",
    ])
    assert [p["kind"] for p in classify_pages(pdf)] == ["slide"] * 4


def test_chrome_needs_four_pages_before_it_is_chrome(tmp_path):
    """On a two-page deck, 80% of pages is both pages, so every shared word
    would be stripped as furniture and a real build would look unrelated."""
    pdf = _pdf(tmp_path, [
        "series value counts default binning",
        "series value counts default binning with bins five",
    ])
    assert classify_pages(pdf)[0]["kind"] == "build"


def test_the_last_page_is_always_a_slide(tmp_path):
    pdf = _pdf(tmp_path, ["one two three four", "one two three four five"])
    assert classify_pages(pdf)[-1]["kind"] == "slide"


def test_group_ids_join_a_build_to_the_page_after_it():
    assert group_ids(["build", "build", "slide", "slide"]) == [1, 1, 1, 2]


def test_an_unsure_page_ends_its_group():
    assert group_ids(["build", "unsure", "slide"]) == [1, 1, 2]


def test_final_pages_are_the_last_page_of_each_group():
    pages = [{"page": n, "group": g}
             for n, g in zip(range(1, 6), [1, 1, 1, 2, 3])]
    assert final_pages(pages) == [3, 4, 5]


def test_save_pages_writes_once_and_never_again(tmp_path):
    pages = [{"page": 1, "kind": "slide", "group": 1, "text": "one"}]
    path, created = save_pages(tmp_path, "00-x", "Module 0 - X.pdf", pages)
    assert created and path == pages_path(tmp_path, "00-x")

    edited = json.loads(path.read_text())
    edited["pages"][0]["kind"] = "build"
    path.write_text(json.dumps(edited))

    _, created_again = save_pages(tmp_path, "00-x", "Module 0 - X.pdf", pages)
    assert not created_again
    assert json.loads(path.read_text())["pages"][0]["kind"] == "build"


def test_load_pages_recomputes_group_from_kind(tmp_path):
    """A human flips a kind and will not renumber the groups by hand."""
    pages = [
        {"page": 1, "kind": "build", "group": 99, "text": "a"},
        {"page": 2, "kind": "slide", "group": 99, "text": "b"},
        {"page": 3, "kind": "slide", "group": 99, "text": "c"},
    ]
    save_pages(tmp_path, "00-x", "Module 0 - X.pdf", pages)
    loaded = load_pages(tmp_path, "00-x")
    assert [p["group"] for p in loaded["pages"]] == [1, 1, 2]
