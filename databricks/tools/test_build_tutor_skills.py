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
    for heading in ("## Artifact", "## Pairings", "## Gates", "## Edges", "## Audit mode"):
        assert heading not in out, f"{heading} survived in {name}"


@pytest.mark.parametrize("name", READ_SUBSKILLS)
def test_the_selection_tree_survives_with_its_steps(name):
    """Choosing a method for a problem is the question a student asks; only the
    dispatch phrasing wrapped around it is machinery."""
    body = split_frontmatter(_src(name))[1]
    if "## Selection tree" not in body:
        pytest.skip(f"{name} has no selection tree")
    after = strip_body(body, is_router=False).split("## Selection tree", 1)[1].lstrip("\n")
    assert after and not after.startswith("#")


@pytest.mark.parametrize("name", READ_SUBSKILLS)
def test_knowledge_sections_survive_with_bodies(name):
    out = strip_body(split_frontmatter(_src(name))[1], is_router=False)
    assert "## Subfields" in out
    # The whole census of substantive sections, not just the four most common:
    # ds-evaluate has no Selection tree at all and carries its method knowledge
    # under Production considerations.
    kept = [h for h in ("## Selection tree", "## Family-specific pitfalls and evaluation",
                        "## Deltas", "## Standards catalog",
                        "## Production considerations", "## Worked compositions") if h in out]
    assert kept, f"{name} kept no method-selection or pitfalls section"
    for heading in kept:
        after = out.split(heading, 1)[1].lstrip("\n")
        assert after and not after.startswith("#"), f"{heading} in {name} is an empty shell"


ALL_SUBSKILLS = sorted(d.name for d in (SRC / "subskills").iterdir()
                       if (d / "SKILL.md").is_file())


@pytest.mark.parametrize("name", ALL_SUBSKILLS)
def test_strip_keeps_between_thirty_and_ninety_percent_of_the_lines(name):
    """Guards both directions: the strip must not gut a skill, and must not be
    a no-op. Gates, Edges and Audit mode are three sections of every file, so
    the floor sits lower than it did when only Artifact and Pairings went."""
    body = split_frontmatter(_src(name))[1]
    before = len([ln for ln in body.splitlines() if ln.strip()])
    after = len([ln for ln in strip_body(body, is_router=False).splitlines() if ln.strip()])
    assert 0.30 <= after / before <= 0.90, f"{name}: kept {after}/{before}"


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
    assert set(KEEP_REFERENCES) <= {e["name"] for e in refs}
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
    """Only listed entries ride in the system prompt, so only they are counted."""
    entries = [e for e in build_data_science(SRC, tmp_path) if e["listed"]]
    total = sum(len(e["name"]) + len(e["description"]) for e in entries)
    assert total < 20_000, f"index is {total} bytes; trim DESCRIPTION_MAX_CHARS"


# --- references ----------------------------------------------------------

def _pointers(text):
    return set(re.findall(r"references/([A-Za-z0-9._-]+)\.md", text))


def test_every_reference_pointer_in_a_generated_skill_resolves(tmp_path):
    """A skill that cites a reference the tree does not carry is a dead end."""
    entries = build_data_science(SRC, tmp_path)
    names = {e["name"] for e in entries if e["kind"] == "reference"}
    dangling = set()
    for path in tmp_path.rglob("*.md"):
        for pointer in _pointers(path.read_text(encoding="utf-8")):
            if pointer not in names or not (tmp_path / "references" / f"{pointer}.md").is_file():
                dangling.add((path.name, pointer))
    assert dangling == set()


def test_a_per_subskill_reference_is_namespaced_by_its_skill(tmp_path):
    entries = build_data_science(SRC, tmp_path)
    by_name = {e["name"]: e for e in entries}
    assert "ds-evaluate.metric-cost-and-slices" in by_name
    assert (tmp_path / "references" / "ds-evaluate.metric-cost-and-slices.md").is_file()


def test_the_same_reference_name_under_two_skills_stays_two_documents(tmp_path):
    """ds-stats and ds-uncertainty both own a subfields.md."""
    names = {e["name"] for e in build_data_science(SRC, tmp_path)}
    assert {"ds-stats.subfields", "ds-uncertainty.subfields"} <= names


def test_a_reference_cited_only_by_another_reference_is_copied_too(tmp_path):
    """metric-selection.md cites ds-evaluate's metric-cost-and-slices."""
    build_data_science(SRC, tmp_path)
    text = (tmp_path / "references" / "metric-selection.md").read_text(encoding="utf-8")
    assert "ds-evaluate.metric-cost-and-slices" in text


def test_only_the_general_references_are_listed_in_the_prompt(tmp_path):
    entries = build_data_science(SRC, tmp_path)
    listed = {e["name"] for e in entries if e["kind"] == "reference" and e["listed"]}
    assert listed == set(KEEP_REFERENCES)
    assert all(e["listed"] for e in entries if e["kind"] == "skill")


def test_the_source_tree_is_not_modified(tmp_path):
    before = {p: p.stat().st_mtime_ns for p in SRC.rglob("*.md")}
    build_data_science(SRC, tmp_path)
    after = {p: p.stat().st_mtime_ns for p in SRC.rglob("*.md")}
    assert before == after


# --- the course half ------------------------------------------------------

from build_tutor_skills import MODULES, build_course_modules, main  # noqa: E402


def test_sixteen_modules_numbered_zero_through_fifteen():
    assert [m["number"] for m in MODULES] == list(range(16))


def test_every_module_has_a_title_slug_and_concepts():
    for m in MODULES:
        assert m["title"] and m["deck"] and m["concepts"]
        assert m["deck"].startswith(f"{m['number']:02d}-")


def test_only_modules_zero_fourteen_and_fifteen_have_no_worksheets():
    assert {m["number"] for m in MODULES if not m["worksheets"]} == {0, 14, 15}


def test_worksheet_filenames_exist_in_the_repo():
    notebooks = Path(__file__).resolve().parents[2] / "notebooks"
    for m in MODULES:
        for w in m["worksheets"]:
            assert (notebooks / w).is_file(), f"module {m['number']}: {w} not in notebooks/"


def test_data_files_exist_in_the_repo():
    data = Path(__file__).resolve().parents[2] / "data"
    for m in MODULES:
        for f in m["data"]:
            if f.endswith("/"):
                assert (data / f.rstrip("/")).is_dir(), f"module {m['number']}: {f}"
            else:
                assert (data / f).is_file(), f"module {m['number']}: {f}"


def test_build_course_modules_writes_sixteen_skills(tmp_path):
    entries = build_course_modules(tmp_path)
    assert len(entries) == 16
    assert {e["name"] for e in entries} == {f"course-module-{n:02d}" for n in range(16)}
    for e in entries:
        assert (tmp_path / e["path"]).is_file()


def test_a_module_skill_names_its_deck_worksheets_and_data(tmp_path):
    build_course_modules(tmp_path)
    text = (tmp_path / "course-module-04" / "SKILL.md").read_text(encoding="utf-8")
    assert "Supervised Machine Learning" in text
    assert "Worksheet_4.2_Tuning_Your_Classifier.ipynb" in text
    assert "dga_features_final_df.csv" in text
    assert "04-supervised-machine-learning" in text


def test_a_module_without_a_lab_says_so(tmp_path):
    build_course_modules(tmp_path)
    text = (tmp_path / "course-module-14" / "SKILL.md").read_text(encoding="utf-8")
    assert "no lab" in text.lower()


def test_module_descriptions_are_indexable(tmp_path):
    for e in build_course_modules(tmp_path):
        assert 40 < len(e["description"]) <= 320


def test_main_writes_index_json_covering_every_skill(tmp_path):
    assert main(["--dest", str(tmp_path)]) == 0
    index = json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))
    names = {e["name"] for e in index}
    assert "data-science" in names
    assert "ds-domain-cyber" in names
    assert "course-module-09" in names
    assert len([e for e in index if e["kind"] == "skill"]) == 38 + 16
    assert set(KEEP_REFERENCES) <= names
    assert len([e for e in index if e["listed"]]) == 38 + 16 + len(KEEP_REFERENCES)
    for e in index:
        assert (tmp_path / e["path"]).is_file()


def test_main_replaces_a_stale_tree(tmp_path):
    (tmp_path / "ds-gone").mkdir(parents=True)
    (tmp_path / "ds-gone" / "SKILL.md").write_text("stale", encoding="utf-8")
    main(["--dest", str(tmp_path)])
    assert not (tmp_path / "ds-gone").exists()


# --- the finished tree ---------------------------------------------------

# Vocabulary that means an agent suite talking to itself, and nothing a student
# ever asked about. Checked against every generated skill rather than a sample:
# the strip is a line pass over prose written for another audience, and one
# skill's phrasing is no evidence about another's.
ORCHESTRATION_WORDS = (
    "run-record", "ledger", "dispatch", "router", "loop-back", "re_entrant",
    "re-entrant", "Re-run scope", "\u2192 artifact:", "SKILL.md \u00a7", "Precondition",
    "Abort to the", "## Gates", "## Edges", "## Audit mode", "tiers.md",
    "manifest.json",
)

GENERATED_SKILLS = (
    ["data-science"] + ALL_SUBSKILLS
    + [f"course-module-{m['number']:02d}" for m in MODULES]
)


@pytest.fixture(scope="session")
def generated(tmp_path_factory):
    """One full build, shared by every check that reads the finished tree."""
    dest = tmp_path_factory.mktemp("tutor-skills")
    assert main(["--dest", str(dest)]) == 0
    return dest


@pytest.mark.parametrize("name", GENERATED_SKILLS)
def test_no_orchestration_vocabulary_survives(generated, name):
    body = (generated / name / "SKILL.md").read_text(encoding="utf-8")
    # A reference's filename is not a mention: ds-clean's assertion-suite-and-
    # ledger names a document, it does not tell the tutor to keep a ledger.
    body = re.sub(r"references/[\w.-]+\.md", "", body)
    for word in ORCHESTRATION_WORDS:
        assert word.lower() not in body.lower(), f"{word!r} survived in {name}"


def test_every_generated_skill_keeps_a_body(generated):
    for name in GENERATED_SKILLS:
        body = split_frontmatter((generated / name / "SKILL.md").read_text(encoding="utf-8"))[1]
        assert len([ln for ln in body.splitlines() if ln.strip()]) > 10, name


# The sections the strip keeps, named here rather than imported: a citation
# lost out of one of these is a citation lost, whatever the drop list says.
KNOWLEDGE_SECTIONS = (
    "## Subfields", "## Selection tree", "## Family-specific pitfalls and evaluation",
    "## Deltas", "## Standards catalog", "## Production considerations",
    "## Worked compositions",
)

_URL_RE = re.compile(r"https?://[^\s`)\]\"']+")


def _urls_in_knowledge_sections(body):
    urls = set()
    for heading in KNOWLEDGE_SECTIONS:
        if heading in body:
            urls |= set(_URL_RE.findall(body.split(heading, 1)[1].split("\n## ", 1)[0]))
    return urls


@pytest.mark.parametrize("name", ALL_SUBSKILLS)
def test_every_citation_url_in_a_kept_section_survives(generated, name):
    """A citation is the one thing a student can follow out of the course."""
    wanted = _urls_in_knowledge_sections(split_frontmatter(_src(name))[1])
    got = set(_URL_RE.findall((generated / name / "SKILL.md").read_text(encoding="utf-8")))
    assert wanted - got == set()


def test_the_fermi_estimate_definition_survives_with_its_citation(generated):
    """It is general pedagogy a student can use, not suite machinery, and it sat
    in the same wrapped unit as a line about tier floors."""
    body = (generated / "ds-verify" / "SKILL.md").read_text(encoding="utf-8")
    assert "https://en.wikipedia.org/wiki/Fermi_problem" in body
    assert "order-of-magnitude bound" in body
