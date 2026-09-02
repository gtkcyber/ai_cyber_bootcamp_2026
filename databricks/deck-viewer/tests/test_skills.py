import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from tutor.files import LocalFiles, MissingFile  # noqa: E402
from tutor.skills import MAX_MATERIAL_CHARS, CourseMaterial, SkillLibrary  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


# LocalFiles' base is the fixtures directory itself, and every path below is
# relative to it -- the same shape the deployed app uses, where the backend has
# no base and the paths are absolute workspace or volume paths.


@pytest.fixture
def library():
    return SkillLibrary.load(LocalFiles(FIXTURES), "/skills")


@pytest.fixture
def material():
    return CourseMaterial(
        files=LocalFiles(FIXTURES),
        labs_path="/labs",
        answers_path="/answers",
        decks_path="/decks",
        deck_files=LocalFiles(FIXTURES),
    )


# --- the skill library ---------------------------------------------------

def test_index_carries_name_description_and_kind(library):
    entries = library.index()
    assert {e["name"] for e in entries} == {"ds-evaluate", "course-module-04", "metric-selection"}
    assert all(set(e) == {"kind", "name", "description"} for e in entries)


def test_index_omits_the_path(library):
    assert all("path" not in e for e in library.index())


def test_load_skill_returns_the_body_without_frontmatter(library):
    body = library.load_skill("ds-evaluate")
    assert body.startswith("# ds-evaluate")
    assert "---" not in body.splitlines()[0]
    assert "PR-AUC over ROC-AUC" in body


def test_load_skill_on_an_unknown_name_names_the_close_ones(library):
    with pytest.raises(MissingFile) as e:
        library.load_skill("ds-evaluation")
    assert "ds-evaluate" in str(e.value)


def test_index_omits_a_reference_that_belongs_to_one_skill(library):
    names = {e["name"] for e in library.index()}
    assert "metric-selection" in names
    assert "ds-evaluate.metric-cost-and-slices" not in names


def test_read_reference_loads_an_unlisted_reference(library):
    """The model meets the name inside the skill that cites it, not in the index."""
    assert "false positive" in library.read_reference("ds-evaluate.metric-cost-and-slices")


def test_read_reference_returns_the_file(library):
    assert "Match the metric" in library.read_reference("metric-selection")


def test_read_reference_refuses_a_skill_name(library):
    with pytest.raises(MissingFile):
        library.read_reference("ds-evaluate")


def test_a_name_with_a_slash_is_refused(library):
    with pytest.raises(MissingFile):
        library.load_skill("../../etc/passwd")


def test_bodies_are_capped(library, monkeypatch):
    big = "x" * (MAX_MATERIAL_CHARS + 5_000)
    monkeypatch.setattr(library, "_read", lambda path: big)
    out = library.load_skill("ds-evaluate")
    assert len(out) <= MAX_MATERIAL_CHARS + 200
    assert "truncated" in out.lower()


def test_load_raises_when_the_index_is_missing(tmp_path):
    with pytest.raises(MissingFile):
        SkillLibrary.load(LocalFiles(tmp_path), "/skills")


# --- deck notes ----------------------------------------------------------

def test_deck_notes_are_returned_with_page_numbers(material):
    notes = material.read_deck_notes("04-supervised-machine-learning")
    assert notes[0][0] == 1 and "DGA problem" in notes[0][1]
    assert notes[1][0] == 2


def test_a_page_without_notes_is_omitted(material):
    assert [n for n, _ in material.read_deck_notes("04-supervised-machine-learning")] == [1, 2]


def test_note_text_is_whitespace_normalised(material):
    _, text = material.read_deck_notes("04-supervised-machine-learning")[1]
    assert "\n" not in text
    assert "leaks is the commonest" in text


def test_note_for_slide_finds_the_pinned_page(material):
    assert "leaks" in material.note_for_slide("04-supervised-machine-learning", 2)


def test_note_for_a_slide_with_no_note_is_none(material):
    assert material.note_for_slide("04-supervised-machine-learning", 3) is None


def test_render_deck_notes_labels_each_page(material):
    rendered = material.render_deck_notes("04-supervised-machine-learning")
    assert "Slide 1" in rendered and "Slide 2" in rendered
    assert len(rendered) <= MAX_MATERIAL_CHARS + 200


def test_notes_fall_back_to_section_order_without_data_page(material, tmp_path):
    html = ('<div class="slides">'
            '<section><aside class="notes">first</aside></section>'
            '<section><aside class="notes">second</aside></section></div>')
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "index.html").write_text(html, encoding="utf-8")
    m = CourseMaterial(files=LocalFiles(tmp_path), labs_path="/l", answers_path="/a",
                       decks_path="/", deck_files=LocalFiles(tmp_path))
    assert m.read_deck_notes("x") == [(1, "first"), (2, "second")]


def test_an_unknown_deck_raises(material):
    with pytest.raises(MissingFile):
        material.read_deck_notes("99-not-a-deck")


# --- labs ----------------------------------------------------------------

def test_read_lab_by_worksheet_number(material):
    text = material.read_lab("4.2")
    assert "# Worksheet 4.2" in text
    assert "GridSearchCV" in text


def test_read_lab_by_full_filename(material):
    assert material.read_lab("Worksheet_4.2_Tuning_Your_Classifier.ipynb")


def test_read_lab_is_case_insensitive_on_the_filename(material):
    assert material.read_lab("worksheet_4.2_tuning_your_classifier.ipynb")


def test_read_lab_labels_markdown_and_code_cells(material):
    text = material.read_lab("4.2")
    assert "[markdown]" in text and "[code]" in text


def test_read_lab_excludes_cell_outputs(material):
    assert "noise that must not be included" not in material.read_lab("4.2")


def test_read_lab_caps_at_max_material_chars(material, monkeypatch):
    monkeypatch.setattr(material, "_read_notebook_json",
                        lambda path: {"cells": [{"cell_type": "code", "source": ["y = 1\n"] * 40_000}]})
    text = material.read_lab("4.2")
    assert len(text) <= MAX_MATERIAL_CHARS + 200
    assert "truncated" in text.lower()


def test_read_lab_refuses_a_traversal(material):
    with pytest.raises(MissingFile):
        material.read_lab("../../../etc/passwd")


def test_read_lab_on_an_unknown_worksheet_lists_what_exists(material):
    with pytest.raises(MissingFile) as e:
        material.read_lab("99.9")
    assert "4.2" in str(e.value)


def test_answers_come_from_the_answers_path(material, monkeypatch):
    seen = []
    monkeypatch.setattr(material, "_list", lambda path: seen.append(path) or
                        ["Worksheet_4.2_Tuning_Your_Classifier-Answers.ipynb"])
    monkeypatch.setattr(material, "_read_notebook_json",
                        lambda path: {"cells": [{"cell_type": "code", "source": ["answer\n"]}]})
    assert "answer" in material.read_lab("4.2", answers=True)
    assert seen == ["/answers"]
