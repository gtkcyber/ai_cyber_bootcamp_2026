"""Notes source: one '## Page N' section per final slide."""

import pytest

from build_decks import UNRESOLVED, load_notes, note_html, notes_path


def _write(root, slug, text):
    path = notes_path(root, slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_a_missing_notes_file_is_an_empty_mapping(tmp_path):
    assert load_notes(tmp_path, "00-x") == {}


def test_each_heading_owns_the_text_under_it(tmp_path):
    _write(tmp_path, "00-x", "## Page 3\n\nFirst note.\n\n## Page 7\n\nSecond note.\n")
    assert load_notes(tmp_path, "00-x") == {3: "First note.", 7: "Second note."}


def test_unresolved_is_kept_as_the_literal_body(tmp_path):
    _write(tmp_path, "00-x", f"## Page 3\n\n{UNRESOLVED}\n")
    assert load_notes(tmp_path, "00-x")[3] == UNRESOLVED


def test_a_repeated_page_heading_is_an_error(tmp_path):
    _write(tmp_path, "00-x", "## Page 3\n\nOne.\n\n## Page 3\n\nTwo.\n")
    with pytest.raises(ValueError, match="two"):
        load_notes(tmp_path, "00-x")


def test_a_heading_with_no_body_loads_as_empty(tmp_path):
    _write(tmp_path, "00-x", "## Page 3\n\n## Page 4\n\nReal note.\n")
    assert load_notes(tmp_path, "00-x")[3] == ""


def test_paragraphs_become_p_elements():
    assert note_html("One.\n\nTwo.") == "<p>One.</p>\n<p>Two.</p>"


def test_a_wrapped_paragraph_joins_onto_one_line():
    assert note_html("One\nsentence.") == "<p>One sentence.</p>"


def test_a_run_of_dash_lines_becomes_a_list():
    assert note_html("- First\n- Second") == "<ul><li>First</li><li>Second</li></ul>"


def test_backticks_become_code_spans():
    assert note_html("Call `fit()` first.") == "<p>Call <code>fit()</code> first.</p>"


def test_html_in_a_note_is_escaped():
    assert note_html("a < b & c") == "<p>a &lt; b &amp; c</p>"


def test_an_empty_body_renders_nothing():
    assert note_html("") == ""
    assert note_html("   \n  ") == ""
