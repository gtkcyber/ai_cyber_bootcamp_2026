import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_tutor_skills import (  # noqa: E402
    BANNED_WORDS_RE,
    KEEP_REFERENCES,
    LeakageError,
    build_data_science,
    clean_description,
    render_skill,
    split_frontmatter,
    strip_body,
)

SRC = Path("/home/curtis/claude_projects/claude-skills/skills/data-science")
READ_SUBSKILLS = ["ds-supervised", "ds-evaluate", "ds-domain-cyber"]


def _src(name):
    return (SRC / "subskills" / name / "SKILL.md").read_text(encoding="utf-8")


# --- frontmatter ---------------------------------------------------------

def test_split_frontmatter_reads_name_and_description():
    meta, body = split_frontmatter(_src("ds-supervised"))
    assert meta["name"] == "ds-supervised"
    assert meta["description"].startswith("Internal")
    assert body.lstrip().startswith("#")


def test_folded_description_is_joined_to_one_line():
    meta, _ = split_frontmatter(_src("ds-evaluate"))
    assert "\n" not in meta["description"]


# --- description cleaning ------------------------------------------------

@pytest.mark.parametrize("name", READ_SUBSKILLS)
def test_clean_description_drops_the_internal_prefix(name):
    meta, _ = split_frontmatter(_src(name))
    out = clean_description(meta["description"])
    assert not out.startswith("Internal")
    assert "invoked via the data-science router" not in out


@pytest.mark.parametrize("name", READ_SUBSKILLS)
def test_clean_description_has_no_banned_word(name):
    meta, _ = split_frontmatter(_src(name))
    assert not BANNED_WORDS_RE.search(clean_description(meta["description"]))


@pytest.mark.parametrize("name", READ_SUBSKILLS)
def test_clean_description_keeps_the_subject_matter(name):
    meta, _ = split_frontmatter(_src(name))
    out = clean_description(meta["description"])
    assert len(out) > 60, "the strip ate the whole description"


def test_clean_description_drops_the_not_re_entrant_sentence():
    out = clean_description(
        "Internal — invoked via the data-science router. Classification and regression. "
        "Not re-entrant; sources the evaluate→features loop-backs."
    )
    assert out == "Classification and regression."


def test_clean_description_raises_on_residual_leakage():
    with pytest.raises(LeakageError):
        clean_description("Writes the run-record for the caller in a way no rule catches.")


def test_router_description_loses_its_do_not_invoke_tail():
    meta, _ = split_frontmatter((SRC / "SKILL.md").read_text(encoding="utf-8"))
    out = clean_description(meta["description"])
    assert "Do not invoke" not in out and "abort" not in out
    assert "data science" in out.lower()


# --- body stripping ------------------------------------------------------

@pytest.mark.parametrize("name", READ_SUBSKILLS)
def test_precondition_block_is_gone(name):
    out = strip_body(split_frontmatter(_src(name))[1], is_router=False)
    assert "Precondition" not in out
    assert "Abort to the router" not in out


@pytest.mark.parametrize("name", READ_SUBSKILLS)
def test_dropped_sections_are_gone(name):
    out = strip_body(split_frontmatter(_src(name))[1], is_router=False)
    assert "## Artifact" not in out
    assert "## Pairings" not in out


@pytest.mark.parametrize("name", READ_SUBSKILLS)
def test_no_orchestration_vocabulary_survives(name):
    out = strip_body(split_frontmatter(_src(name))[1], is_router=False)
    for word in ("run-record", "ledger", "dispatch-table", "the router",
                 "loop-backs.md", "Re-run scope", "→ artifact:", "re_entrant"):
        assert word not in out, f"{word!r} survived in {name}"


@pytest.mark.parametrize("name", READ_SUBSKILLS)
def test_knowledge_sections_survive_with_bodies(name):
    out = strip_body(split_frontmatter(_src(name))[1], is_router=False)
    assert "## Subfields" in out
    assert "## Edges" in out
    # The whole census of substantive sections, not just the four most common:
    # ds-evaluate carries its method knowledge under Audit mode and Production
    # considerations and has no Selection tree at all.
    kept = [h for h in ("## Selection tree", "## Family-specific pitfalls and evaluation",
                        "## Deltas", "## Standards catalog", "## Audit mode",
                        "## Production considerations", "## Worked compositions") if h in out]
    assert kept, f"{name} kept no method-selection or pitfalls section"
    for heading in kept:
        after = out.split(heading, 1)[1].lstrip("\n")
        assert after and not after.startswith("#"), f"{heading} in {name} is an empty shell"


@pytest.mark.parametrize("name", READ_SUBSKILLS)
def test_strip_keeps_between_forty_and_ninety_percent_of_the_lines(name):
    body = split_frontmatter(_src(name))[1]
    before = len([ln for ln in body.splitlines() if ln.strip()])
    after = len([ln for ln in strip_body(body, is_router=False).splitlines() if ln.strip()])
    assert 0.40 <= after / before <= 0.90, f"{name}: kept {after}/{before}"


def test_strip_leaves_no_run_of_three_blank_lines():
    out = strip_body(split_frontmatter(_src("ds-evaluate"))[1], is_router=False)
    assert "\n\n\n" not in out


def test_router_body_keeps_the_classification_axes_and_drops_the_rest():
    out = strip_body(split_frontmatter((SRC / "SKILL.md").read_text(encoding="utf-8"))[1],
                     is_router=True)
    assert "## 1. Classify: three axes" in out
    for heading in ("## 2. Select tier", "## 3. Dispatch", "## 4. Reference load order"):
        assert heading not in out


# --- rendering and the whole build --------------------------------------

def test_render_skill_round_trips_through_split_frontmatter():
    text = render_skill("ds-x", "A description: with a colon, and a #hash.", "# ds-x\n\nBody.\n")
    meta, body = split_frontmatter(text)
    assert meta["name"] == "ds-x"
    assert meta["description"] == "A description: with a colon, and a #hash."
    assert body.strip() == "# ds-x\n\nBody."


def test_build_data_science_writes_router_37_subskills_and_kept_references(tmp_path):
    entries = build_data_science(SRC, tmp_path)
    skills = [e for e in entries if e["kind"] == "skill"]
    refs = [e for e in entries if e["kind"] == "reference"]
    assert len(skills) == 38, "router + 37 subskills"
    assert {e["name"] for e in refs} == set(KEEP_REFERENCES)
    assert (tmp_path / "data-science" / "SKILL.md").is_file()
    assert (tmp_path / "ds-domain-cyber" / "SKILL.md").is_file()
    for e in entries:
        assert (tmp_path / e["path"]).is_file()


def test_dropped_references_are_not_written(tmp_path):
    build_data_science(SRC, tmp_path)
    for dropped in ("dispatch-table", "ledger-spec", "loop-backs", "tiers", "concept-ownership"):
        assert not (tmp_path / "references" / f"{dropped}.md").exists()


def test_no_generated_file_mentions_a_run_record(tmp_path):
    build_data_science(SRC, tmp_path)
    offenders = [p.name for p in tmp_path.rglob("*.md")
                 if re.search(r"run-record|ledger-spec|dispatch-table", p.read_text(encoding="utf-8"))]
    assert offenders == []


def test_the_index_of_descriptions_fits_a_prompt(tmp_path):
    entries = build_data_science(SRC, tmp_path)
    total = sum(len(e["name"]) + len(e["description"]) for e in entries)
    assert total < 20_000, f"index is {total} bytes; trim DESCRIPTION_MAX_CHARS"


def test_the_source_tree_is_not_modified(tmp_path):
    before = {p: p.stat().st_mtime_ns for p in SRC.rglob("*.md")}
    build_data_science(SRC, tmp_path)
    after = {p: p.stat().st_mtime_ns for p in SRC.rglob("*.md")}
    assert before == after
