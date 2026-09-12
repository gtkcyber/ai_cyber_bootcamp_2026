"""Notes move from text-classified pages to manifest pages, one slide per old page."""

import json

import pytest

from build_decks import group_ids
from rekey_notes import finished_pages, rekey, rekey_deck, write_notes

MANIFEST = {
    "slug": "08-deep-learning", "source": "x.key", "pdf": "x.pdf", "page_count": 6,
    "pages": [
        {"page": 1, "slide": 1, "stage": 0, "stages": 1},
        {"page": 2, "slide": 2, "stage": 0, "stages": 3},
        {"page": 3, "slide": 2, "stage": 1, "stages": 3},
        {"page": 4, "slide": 2, "stage": 2, "stages": 3},
        {"page": 5, "slide": 3, "stage": 0, "stages": 1},
        {"page": 6, "slide": 4, "stage": 0, "stages": 1},
    ],
    "media": [],
}


def _pages(kinds):
    return [{"page": n, "kind": k, "group": g, "text": ""}
            for n, (k, g) in enumerate(zip(kinds, group_ids(kinds)), start=1)]


def test_finished_pages_are_the_last_stage_of_each_slide():
    assert finished_pages(MANIFEST) == {1: 1, 2: 4, 3: 5, 4: 6}


def test_a_note_follows_its_slide_to_the_finished_page():
    moved, copied = rekey(_pages(["slide"] * 4), {1: "one", 2: "two", 3: "three", 4: "four"}, MANIFEST)
    assert moved == {1: "one", 4: "two", 5: "three", 6: "four"}
    assert copied == []


def test_slides_the_classifier_had_merged_each_get_the_note():
    moved, copied = rekey(_pages(["slide", "build", "slide", "slide"]), {1: "one", 3: "shared", 4: "four"}, MANIFEST)
    assert moved == {1: "one", 4: "shared", 5: "shared", 6: "four"}
    assert copied == [(2, 4)]


def test_a_slide_without_a_note_stays_without_one():
    moved, _ = rekey(_pages(["slide"] * 4), {1: "one"}, MANIFEST)
    assert moved == {1: "one"}


def test_write_notes_is_the_notes_file_format(tmp_path):
    write_notes(tmp_path / "n.md", {4: "later", 1: "first\n"})
    assert (tmp_path / "n.md").read_text() == "## Page 1\n\nfirst\n\n## Page 4\n\nlater\n"


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "databricks" / "pages").mkdir(parents=True)
    (tmp_path / "databricks" / "notes").mkdir()
    (tmp_path / "manifests").mkdir()
    (tmp_path / "databricks" / "pages" / "08-deep-learning.json").write_text(json.dumps(
        {"slug": "08-deep-learning", "pdf": "x.pdf", "page_count": 4, "manifest": False,
         "pages": _pages(["slide", "build", "slide", "slide"])}))
    (tmp_path / "databricks" / "notes" / "08-deep-learning.md").write_text(
        "## Page 1\n\none\n\n## Page 3\n\nshared\n\n## Page 4\n\nfour\n")
    (tmp_path / "manifests" / "08-deep-learning.json").write_text(json.dumps(MANIFEST))
    return tmp_path


def test_rekey_deck_rewrites_the_notes_file_and_reports(repo):
    result = rekey_deck(repo, "08-deep-learning", repo / "manifests")
    assert result["notes"] == 4 and result["copied"] == [(2, 4)] and result["orphans"] == []
    assert (repo / "databricks" / "notes" / "08-deep-learning.md").read_text() == \
        "## Page 1\n\none\n\n## Page 4\n\nshared\n\n## Page 5\n\nshared\n\n## Page 6\n\nfour\n"


def test_rekey_deck_refuses_a_classification_that_is_already_from_a_manifest(repo):
    path = repo / "databricks" / "pages" / "08-deep-learning.json"
    payload = json.loads(path.read_text())
    payload["manifest"] = True
    path.write_text(json.dumps(payload))
    with pytest.raises(SystemExit):
        rekey_deck(repo, "08-deep-learning", repo / "manifests")


def test_rekey_deck_refuses_when_old_pages_are_not_one_per_slide(repo):
    path = repo / "databricks" / "pages" / "08-deep-learning.json"
    payload = json.loads(path.read_text())
    payload["pages"] = payload["pages"][:3]
    path.write_text(json.dumps(payload))
    with pytest.raises(SystemExit):
        rekey_deck(repo, "08-deep-learning", repo / "manifests")
