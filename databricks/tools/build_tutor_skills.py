#!/usr/bin/env python3
"""Generate databricks/tutor-skills/ — the tutor's whole knowledge base.

Two sources, one output tree:

  1. claude-skills/skills/data-science (READ-ONLY, a sibling project) — the
     router, its 37 subskills and 6 of its 11 top-level references, with the
     agent-orchestration mechanics stripped out: run-record preconditions,
     ledger field names, the dispatch table, loop-back edges, re-entrancy
     flags, tier floors, and every line telling an agent to invoke another
     skill. What survives is the data-science knowledge itself: subfield
     triggers and canonical methods, selection trees, family pitfalls, domain
     deltas, standards catalogs, production considerations.

  2. The MODULES table in this file — one course-module-NN skill per bootcamp
     module, written by hand from the repo's notebooks and slide titles.

The derivative is generated, never hand-edited: editing tutor-skills/ directly
puts it out of step with the source suite, and the next run silently reverts
the edit. Change this script, or change the source, and re-run.

    python3 databricks/tools/build_tutor_skills.py

Run from the course repo root. Writes databricks/tutor-skills/ and its
index.json, replacing whatever was there.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import textwrap
from pathlib import Path

DEFAULT_SRC = Path("/home/curtis/claude_projects/claude-skills/skills/data-science")
DEFAULT_DEST = Path(__file__).resolve().parents[1] / "tutor-skills"

# The index rides in every system prompt; 38 + 16 descriptions at this cap is
# well under the prompt budget in tutor/prompt.py.
DESCRIPTION_MAX_CHARS = 320

# References that are data-science knowledge, kept. The other five
# (concept-ownership, dispatch-table, ledger-spec, loop-backs, tiers) are
# agent-orchestration machinery with no tutor value and are not copied.
KEEP_REFERENCES = (
    "doctrine-leakage",
    "doctrine-repro-provenance",
    "doctrine-scale-cost",
    "encoding-chooser",
    "imputation-tree",
    "metric-selection",
)


# The five top-level references that are agent-orchestration machinery. They are
# never copied, and every citation to one is expected to have gone with the line
# that carried it -- one surviving means DROP_LINE_RES has a gap, which is a
# build failure rather than something to paper over.
DROP_REFERENCES = ("concept-ownership", "dispatch-table", "ledger-spec", "loop-backs", "tiers")


class DanglingReferenceError(Exception):
    """A body cites a reference the build cannot resolve, or must not copy."""


class LeakageError(Exception):
    """A cleaned description still contains agent-orchestration vocabulary.

    Raised rather than shipped: a tutor whose skill index tells a student to
    "invoke the router" is worse than a build that fails loudly.
    """


# --- description cleaning ------------------------------------------------

# The 37 subskills open with this byte-identical sentence.
_INTERNAL_PREFIX = "Internal — invoked via the data-science router."

# Sentences that exist only to steer an agent. Matched against whole sentences
# after whitespace normalisation, so a rule can never eat half a thought.
_DROP_SENTENCE_RES = (
    re.compile(r"^Do not invoke\b", re.I),
    # Re-entrancy is a statement about how the agent suite calls itself. It
    # opens a sentence in some descriptions and sits mid-sentence in others
    # ("Fixed-position cross-reference, not re-entrant: ..."), so the whole
    # sentence goes wherever the word appears.
    re.compile(r"\bre-entrant\b", re.I),
    re.compile(r"^Reference implementation for the [\w-]+ layer\.?$", re.I),
    re.compile(r"\brun-record\b", re.I),
    re.compile(r"\babort(s|ed)? back\b", re.I),
    re.compile(r"\bloop-backs?\b", re.I),
    re.compile(r"\bdispatch\b", re.I),
    re.compile(r"\bledger\b", re.I),
    re.compile(r"\blifecycle-positioned\b", re.I),
)

# Machinery phrases inside a sentence that is otherwise the subject matter the
# index exists to carry. Applied BEFORE the sentence filter, so a sentence that
# is only machinery at its edges survives with the edges gone, while one that
# is machinery through and through still fails the filter after them.
_DESCRIPTION_SCRUB_RES = (
    # The router's own description opens by naming itself.
    (re.compile(r"^Router for\b"), "Guidance for"),
    (re.compile(r"\s+and composes the relevant internal sub-skills"), ""),
    # "The router's method-composition hook: ..." -- the hook is a real idea,
    # whose owner is not.
    (re.compile(r"\brouter's\s+", re.I), ""),
    # "Opens every dispatch: turns a question into a task card — ..."
    (re.compile(r"^Opens every dispatch:\s*", re.I), ""),
    # "Turns ledger findings into the audience-tiered report" -- to a student
    # they are just the findings.
    (re.compile(r"\bledger\s+findings\b", re.I), "findings"),
    (re.compile(r"\s*\(serving wrapper:\s*`[^`]+`\)"), ""),
    (re.compile(r";\s*sources the [^.]*\."), "."),
)

# Nothing matching this may survive into a description.
BANNED_WORDS_RE = re.compile(
    r"\b(invoke[sd]?|invoking|abort(s|ed|ing)?|run-record|ledger|dispatch(es|ed)?|"
    r"re-entrant|re_entrant|router|misroute|loop-back)\b",
    re.I,
)


def _sentences(text: str) -> list[str]:
    """Split on sentence-final punctuation followed by a space and a capital."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(`])", text) if s.strip()]


def clean_description(text: str) -> str:
    text = " ".join(text.split())
    if text.startswith(_INTERNAL_PREFIX):
        text = text[len(_INTERNAL_PREFIX):].lstrip()
    for rx, replacement in _DESCRIPTION_SCRUB_RES:
        text = rx.sub(replacement, text)
    kept = [s for s in _sentences(text)
            if not any(rx.search(s) for rx in _DROP_SENTENCE_RES)]
    out = " ".join(" ".join(kept).split())
    if out:
        out = out[0].upper() + out[1:]
    if not out:
        raise LeakageError(f"nothing survived cleaning: {text!r}")
    if BANNED_WORDS_RE.search(out):
        raise LeakageError(f"description still carries orchestration vocabulary: {out!r}")
    if len(out) > DESCRIPTION_MAX_CHARS:
        cut = out[:DESCRIPTION_MAX_CHARS].rsplit(" ", 1)[0]
        out = cut.rstrip(",;:") + "…"
    return out


# --- body stripping ------------------------------------------------------

# Whole sections that are pure machinery. `Artifact` is literally the ledger
# schema pointer; `Pairings` is the cross-skill composition list. The router's
# sections 2-4 are tier selection, dispatch and reference load order — its
# section 1 (the three classification axes) is a genuine taxonomy and stays.
DROP_HEADINGS_SUBSKILL = ("## Artifact", "## Pairings")
DROP_HEADINGS_ROUTER = ("## 2. Select tier", "## 3. Dispatch", "## 4. Reference load order")

# The two precondition forms, matched on whitespace-normalised text so the
# varying line-wrap inside Form A does not matter.
_PRECONDITION_RES = (
    re.compile(
        r"^>\s*Abort to the router .*?instruct the caller to invoke `data-science` first\.\s*$",
        re.I | re.S),
    re.compile(
        r"^\*\*Precondition\*\*:.*?do not run standalone\.\s*$",
        re.I | re.S),
)

# Lines that carry orchestration inside an otherwise-keepable section. Every
# pattern here was read off a real line in the source, not guessed.
DROP_LINE_RES = tuple(re.compile(p, re.I) for p in (
    r"^\s*Dispatch fields\b",
    r"\bdispatch-table(\.md)?\b",
    r"\bLedger section\b",
    r"\bledger-spec\.md\b",
    r"\bloop-backs\.md\b",
    r"\bconcept-ownership\.md\b",
    r"\bBACKLOG\.md\b",
    r"\blint_dangling\w*\b",
    r"\brun-record\b",
    r"\bthe router\b",
    r"\bmisroute\b",
    r"\bRe-run scope:",
    r"\bre_entrant\s*:",
    r"\bcomposed-alongside\s*:",
    r"\bload order\s*:\s*\d+",
    r"→\s*artifact:",
    r"^\s*Reciprocal \(`ds-[\w-]+` names `ds-[\w-]+` back\)\.\s*$",
    r"\bgate-executor rule\b",
    r"\bowner:\s*ds-[\w-]+",
    r"^\s*Invoke\b",
    r"\btier floor\b",
    r"^\s*participation\s*:",
    r"\bSKILL\.md §\d",
    # A cross-reference to a section this script deletes would dangle.
    r"`##\s*(Pairings|Artifact)`",
))

# Machinery that sits INSIDE a sentence worth keeping. The domain skills carry
# their whole knowledge in `## Deltas` bullets, every one of which ends in a
# citation naming the skill that owns the concept; the `## Worked compositions`
# steps end in the ledger field the step writes. Dropping those lines would
# take the knowledge with them, so the citation is cut out of the sentence and
# the sentence stays.
INLINE_SCRUB_RES = (
    (re.compile(r"\s*\(owner:\s*ds-[^)]*\)"), ""),
    (re.compile(r"\s*→\s*artifact:\s*`[^`]*`"), ""),
    (re.compile(r"\s*\(`ds-[\w-]+`'s [^)]*\)"), ""),
)

_BULLET_RE = re.compile(r"^(\s*)((?:[-*+]|\d+\.)\s+)")
_WRAP_WIDTH = 76


def _is_machinery(text: str) -> bool:
    return any(rx.search(text) for rx in DROP_LINE_RES)


def _scrub_inline(text: str) -> str:
    for rx, replacement in INLINE_SCRUB_RES:
        text = rx.sub(replacement, text)
    return text


def _drop_precondition(body: str) -> str:
    """Remove the precondition block, which is always the first content after the H1."""
    lines = body.splitlines()
    out, i = [], 0
    # keep the H1 and the blank line under it
    while i < len(lines) and not lines[i].startswith("# "):
        out.append(lines[i])
        i += 1
    if i < len(lines):
        out.append(lines[i])
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    # gather the candidate block: consecutive non-blank lines
    block_start = i
    while i < len(lines) and lines[i].strip():
        i += 1
    block = " ".join(" ".join(lines[block_start:i]).split())
    block = re.sub(r"^>\s*", "", block)
    block = re.sub(r"\s*>\s*", " ", block)
    if any(rx.match(block) for rx in _PRECONDITION_RES) or (
        "abort to the router" in block.lower() or "**precondition**" in block.lower()
    ):
        out.append("")
        out.extend(lines[i:])
    else:
        out.append("")
        out.extend(lines[block_start:])
    return "\n".join(out)


def _drop_sections(body: str, headings: tuple[str, ...]) -> str:
    """Drop each named `##` section up to the next `##` heading."""
    out, skipping = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            skipping = any(line.strip() == h for h in headings)
        if not skipping:
            out.append(line)
    return "\n".join(out)


def _rewrite(lines: list[str], indent: str, marker: str) -> list[str]:
    """Scrub inline machinery and drop machinery sentences from one wrapped unit.

    The suite wraps prose at roughly 72 columns, so a machinery sentence
    routinely straddles two lines and deleting one of them would leave the
    other a fragment. The unit is joined, judged whole sentence by whole
    sentence, and re-wrapped -- but only if something actually changed, so a
    unit that loses nothing keeps its original wrapping byte for byte.
    """
    joined = " ".join(ln.strip() for ln in lines)
    if marker:
        joined = joined[len(marker.strip()):].lstrip()
    scrubbed = _scrub_inline(joined)
    sentences = _sentences(scrubbed)
    kept = [s for s in sentences if not _is_machinery(s)]
    body = " ".join(kept).strip()
    if not body:
        return []
    if scrubbed == joined and len(kept) == len(sentences):
        return lines
    return textwrap.wrap(body, width=_WRAP_WIDTH,
                         initial_indent=indent + marker,
                         subsequent_indent=indent + " " * len(marker),
                         break_long_words=False, break_on_hyphens=False)


def _drop_block(block: list[str]) -> list[str]:
    """A run of consecutive prose lines: a list, a paragraph, or a lead-in plus a list."""
    first_bullet = next((i for i, ln in enumerate(block) if _BULLET_RE.match(ln)), None)
    if first_bullet is None:
        indent = block[0][:len(block[0]) - len(block[0].lstrip())]
        return _rewrite(block, indent, "")

    out: list[str] = []
    if first_bullet:
        lead = block[:first_bullet]
        indent = lead[0][:len(lead[0]) - len(lead[0].lstrip())]
        out += _rewrite(lead, indent, "")

    item: list[str] = []
    for line in block[first_bullet:]:
        if _BULLET_RE.match(line) and item:
            out += _rewrite_item(item)
            item = []
        item.append(line)
    if item:
        out += _rewrite_item(item)
    return out


def _rewrite_item(item: list[str]) -> list[str]:
    """One list item, its wrapped continuation lines included, as a single unit."""
    m = _BULLET_RE.match(item[0])
    return _rewrite(item, m.group(1), m.group(2))


def _drop_lines(body: str) -> str:
    """Remove machinery from the body, judging each construct as a whole."""
    lines = body.splitlines()
    out: list[str] = []
    in_fence = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        standalone = (in_fence or not line.strip() or line.startswith("#")
                      or line.lstrip().startswith(("|", ">")))
        if standalone:
            # Code, blank lines, headings, table rows and blockquotes are each
            # judged on their own line: none of them wraps a sentence.
            if not in_fence and line.strip() and _is_machinery(line):
                i += 1
                continue
            out.append(line)
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].strip() and not lines[j].startswith("#") \
                and not lines[j].lstrip().startswith(("```", "|", ">")):
            j += 1
        out.extend(_drop_block(lines[i:j]))
        i = j
    return "\n".join(out)


def _drop_empty_sections(body: str) -> str:
    """Remove a heading whose whole body was stripped away."""
    lines = body.splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#"):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or lines[j].startswith("#"):
                # the next thing is another heading or the end: this one is empty
                if not (line.startswith("# ") and not line.startswith("## ")):
                    i = j
                    continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _tidy(body: str) -> str:
    body = re.sub(r"[ \t]+$", "", body, flags=re.M)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def strip_body(body: str, *, is_router: bool) -> str:
    headings = DROP_HEADINGS_ROUTER if is_router else DROP_HEADINGS_SUBSKILL
    body = _drop_precondition(body)
    body = _drop_sections(body, headings)
    body = _drop_lines(body)
    body = _drop_empty_sections(body)
    return _tidy(body)


# --- references ----------------------------------------------------------

# `references/foo.md`, or the owner-qualified `ds-data-models/references/foo.md`
# the suite uses when one skill cites another's reference.
_REFERENCE_CITATION_RE = re.compile(r"(?:([a-z][\w-]*)/)?references/([A-Za-z0-9._-]+)\.md")


class _ReferenceLibrary:
    """Resolve every cited reference to one indexed name, and copy what is cited.

    The suite keeps eleven references at the top level and 73 more inside the
    subskills that own them, and two skills can own a file of the same name
    (`subfields.md` sits under both ds-stats and ds-uncertainty). So a
    per-subskill reference is indexed as `<skill>.<stem>`, a top-level one as
    `<stem>`, and every citation in a generated body is rewritten to the name it
    resolved to -- which is exactly the name `read_reference` takes. Copying
    only the six general references, as this script first did, left the other
    sixty-odd pointers dead on arrival.

    Only those six ride in the system prompt (`listed`). The rest are leaves of
    one skill, met by name inside the body that cites them; listing all of them
    would cost more prompt than the skills themselves.
    """

    def __init__(self, src: Path):
        self.src = src
        self.sources: dict[str, Path] = {}

    def _candidates(self, owner: str, qualifier: str | None, stem: str):
        subskills = self.src / "subskills"
        if qualifier:
            yield f"{qualifier}.{stem}", subskills / qualifier / "references" / f"{stem}.md"
            return
        if owner:
            yield f"{owner}.{stem}", subskills / owner / "references" / f"{stem}.md"
        yield stem, self.src / "references" / f"{stem}.md"
        # A top-level reference cites a subskill's leaf by its bare name, which
        # is only unambiguous when exactly one subskill owns that name.
        elsewhere = sorted(subskills.glob(f"*/references/{stem}.md"))
        if len(elsewhere) == 1:
            yield f"{elsewhere[0].parent.parent.name}.{stem}", elsewhere[0]

    def rewrite(self, text: str, owner: str) -> str:
        """Point every citation in `text` at an indexed name, queueing the file."""
        def replace(match: re.Match) -> str:
            qualifier, stem = match.group(1), match.group(2)
            if stem in DROP_REFERENCES:
                raise DanglingReferenceError(
                    f"{owner or 'a reference'} still cites {stem!r}, which is machinery "
                    "this build drops -- the line carrying it should have gone too")
            for name, path in self._candidates(owner, qualifier, stem):
                if path.is_file():
                    self.sources.setdefault(name, path)
                    return f"references/{name}.md"
            raise DanglingReferenceError(
                f"{owner or 'a reference'} cites {match.group(0)!r}, which the source "
                "suite does not have under that name")
        return _REFERENCE_CITATION_RE.sub(replace, text)

    def emit(self, dest: Path) -> list[dict]:
        """Write every queued reference, and everything they cite in turn."""
        for name in KEEP_REFERENCES:
            self.sources.setdefault(name, self.src / "references" / f"{name}.md")
        out_dir = dest / "references"
        out_dir.mkdir(parents=True, exist_ok=True)
        entries: list[dict] = []
        written: set[str] = set()
        while True:
            pending = sorted(set(self.sources) - written)
            if not pending:
                return entries
            for name in pending:
                written.add(name)
                path = self.sources[name]
                owner = (path.parent.parent.name
                         if path.parent.parent.parent.name == "subskills" else "")
                text = self.rewrite(_tidy(_drop_lines(path.read_text(encoding="utf-8"))), owner)
                (out_dir / f"{name}.md").write_text(text, encoding="utf-8")
                first = next((ln.strip() for ln in text.splitlines()
                              if ln.strip() and not ln.startswith("#")), name)
                entries.append({
                    "kind": "reference", "name": name,
                    "description": first[:DESCRIPTION_MAX_CHARS],
                    "path": f"references/{name}.md",
                    "listed": name in KEEP_REFERENCES,
                })


# --- frontmatter I/O -----------------------------------------------------

def split_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the `name`/`description` frontmatter without a YAML dependency.

    The suite uses exactly two keys and folded (`>-`) descriptions; a hand
    parser keeps the app's requirements.txt free of PyYAML, which the app
    would otherwise carry only for this.

    It also reads back what `render_skill` writes -- a double-quoted scalar --
    so a generated skill round-trips through this parser unchanged.
    """
    if not text.startswith("---"):
        raise ValueError("no frontmatter")
    _, fm, body = text.split("---", 2)
    meta, key = {}, None
    for raw in fm.splitlines():
        if not raw.strip():
            continue
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", raw)
        if m and not raw.startswith((" ", "\t")):
            key, value = m.group(1), m.group(2).strip()
            meta[key] = "" if value in (">-", ">", "|", "|-") else _unquote(value)
        elif key is not None:
            meta[key] = (meta[key] + " " + raw.strip()).strip()
    return meta, body.lstrip("\n")


def _unquote(value: str) -> str:
    """Undo render_skill's quoting: a double-quoted scalar with \\" and \\\\ escapes."""
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def render_skill(name: str, description: str, body: str) -> str:
    """Emit frontmatter with a single-line, double-quoted description.

    Quoting sidesteps every YAML special case a description can contain — a
    leading `#`, a `: ` pair, a leading `>` — with one escape rule.
    """
    escaped = description.replace("\\", "\\\\").replace('"', '\\"')
    return f'---\nname: {name}\ndescription: "{escaped}"\n---\n\n{body.strip()}\n'


# --- the data-science half ----------------------------------------------

def build_data_science(src: Path, dest: Path) -> list[dict]:
    """Write the stripped router, subskills and every cited reference."""
    entries: list[dict] = []
    references = _ReferenceLibrary(src)

    def emit_skill(name: str, text: str, *, is_router: bool) -> None:
        meta, body = split_frontmatter(text)
        description = clean_description(meta["description"])
        out_body = references.rewrite(strip_body(body, is_router=is_router), name)
        rel = f"{name}/SKILL.md"
        path = dest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_skill(name, description, out_body), encoding="utf-8")
        entries.append({"kind": "skill", "name": name, "description": description,
                        "path": rel, "listed": True})

    emit_skill("data-science", (src / "SKILL.md").read_text(encoding="utf-8"), is_router=True)

    for skill_dir in sorted((src / "subskills").iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if skill_md.is_file():
            emit_skill(skill_dir.name, skill_md.read_text(encoding="utf-8"), is_router=False)

    return entries + references.emit(dest)


# --- the course half -----------------------------------------------------

# Hand-written from the repo: titles from slides/"Module N - Title.pdf",
# worksheets from notebooks/, data files from what those notebooks load,
# concepts from what the worksheets actually do. Modules 0 and 14 have decks
# but no lab; the Final Project is a local-only capstone (spec "Out" list).
#
# `deck` is the deck folder the decks plan produces. If those slugs land
# differently, this column is the single place to change.
MODULES = (
    {
        "number": 0, "title": "Introduction", "deck": "00-introduction",
        "worksheets": (), "data": (), "libraries": (),
        "concepts": (
            "What the bootcamp covers and how it is laid out: five days from pandas through "
            "classical machine learning to LLM agents, every lab a security problem. How the "
            "worksheets, the answer notebooks and the shared course data fit together, and what "
            "a student is expected to be able to do by the end."
        ),
    },
    {
        "number": 1, "title": "Exploratory Data Analysis", "deck": "01-exploratory-data-analysis",
        "worksheets": ("Worksheet_1.1_Vectorized_Data_Structures.ipynb",),
        "data": ("dailybots.csv", "hackers-access.httpd"),
        "libraries": ("pandas", "numpy"),
        "concepts": (
            "Pandas Series and DataFrames as vectorized structures: why a vectorized operation "
            "beats a Python loop over rows, boolean masking and .loc/.iloc indexing, groupby and "
            "aggregation, and reading semi-structured security telemetry — a botnet-activity CSV "
            "and a raw Apache access log — into a frame you can ask questions of."
        ),
    },
    {
        "number": 2, "title": "Data Visualization", "deck": "02-data-visualization",
        "worksheets": ("Worksheet_2.1_Data_Visualization.ipynb",),
        "data": ("dailybots.csv",),
        "libraries": ("matplotlib", "seaborn", "streamlit"),
        "concepts": (
            "Choosing a chart for the question: distributions, comparisons over time, and "
            "relationships between two variables, plus the traps that make a security chart lie "
            "(unlabelled axes, a truncated y-axis, an aggregation that hides the outlier you were "
            "looking for). Worksheet 2.2 is a Streamlit script, not a notebook, and stays a "
            "local-only exercise on Databricks."
        ),
    },
    {
        "number": 3, "title": "Feature Engineering", "deck": "03-feature-engineering",
        "worksheets": ("Worksheet_3.1_Feature_Engineering.ipynb",),
        "data": ("dga_data_small.csv", "d_common_en_words.pickle", "google-10000-english.txt",
                 "dga_features_final_df.csv", "dga_features_final_df_domain.csv",
                 "our_data_dga_features_final_df.csv"),
        "libraries": ("pandas", "sklearn"),
        "concepts": (
            "Turning raw domain names into features a classifier can use: length, Shannon entropy, "
            "vowel and digit ratios, n-gram frequency against an English corpus, and dictionary-word "
            "membership. Why a feature has to be computable at scoring time, and why a feature that "
            "encodes the label leaks. The frame this worksheet writes is the input to Module 4."
        ),
    },
    {
        "number": 4, "title": "Supervised Machine Learning", "deck": "04-supervised-machine-learning",
        "worksheets": ("Worksheet_4.1_DGA_Detection_using_Supervised_Learning.ipynb",
                       "Worksheet_4.2_Tuning_Your_Classifier.ipynb",
                       "Worksheet_4.3_Automate_It_All.ipynb"),
        "data": ("our_data_dga_features_final_df.csv", "dga_features_final_df.csv",
                 "dga_decision_tree.pkl", "dga_model.sav"),
        "libraries": ("sklearn", "lime", "shap", "tpot"),
        "concepts": (
            "Training and judging a DGA classifier: train/test splits, decision trees and random "
            "forests, cross-validation, and hyperparameter search in 4.2. Which metric to read under "
            "class imbalance and what a confusion matrix costs a SOC in false positives. 4.3 runs "
            "TPOT for automated pipeline search and explains a fitted model with LIME and SHAP."
        ),
    },
    {
        "number": 5, "title": "Unsupervised Learning", "deck": "05-unsupervised-learning",
        "worksheets": ("Worksheet_5.1_Clustering.ipynb",),
        "data": ("dga-full.csv", "dga_features_final_df_domain.csv"),
        "libraries": ("sklearn", "scipy"),
        "concepts": (
            "Clustering the same domain features without labels: k-means, hierarchical clustering and "
            "reading a dendrogram, choosing k by elbow and silhouette, and how feature scaling changes "
            "every distance in the problem. Interpreting a cluster is the hard part — a tight cluster "
            "is only useful once you can say what its members have in common."
        ),
    },
    {
        "number": 6, "title": "Anomaly Detection", "deck": "06-anomaly-detection",
        "worksheets": ("Worksheet_6.1_Anomaly_Detection.ipynb",),
        "data": ("cpu-train-a.csv", "cpu-train-b.csv", "cpu-test-a.csv", "cpu-test-b.csv",
                 "cpu-full-a.csv", "cpu-full-b.csv"),
        "libraries": ("statsmodels", "pmdarima", "prophet"),
        "concepts": (
            "Anomalies in a CPU-utilisation time series: seasonal decomposition, forecasting with "
            "ARIMA through pmdarima's auto-fit and with Prophet, and flagging a point by the size of "
            "its residual against the forecast. Why the base rate makes anomaly detection an alerting "
            "problem rather than a modelling one, and how a threshold trades recall for analyst time."
        ),
    },
    {
        "number": 7, "title": "Attacking Machine Learning Models",
        "deck": "07-attacking-machine-learning-models",
        "worksheets": ("Worksheet_7.1_Attacking_AI.ipynb",
                       "Worksheet_7.2_FSGM_Attack_on_Image_Classifier.ipynb"),
        "data": ("dga_decision_tree.pkl", "dga_features_final_df.csv"),
        "libraries": ("sklearn", "torch"),
        "concepts": (
            "Attacking the models the earlier modules built. 7.1 evades the saved DGA decision tree by "
            "moving a domain across the boundary in feature space. 7.2 runs a fast gradient sign method "
            "attack on an image classifier, showing how a perturbation invisible to a person flips the "
            "prediction. The lesson is the threat model: a deployed model is an attack surface."
        ),
    },
    {
        "number": 8, "title": "Deep Learning", "deck": "08-deep-learning",
        "worksheets": ("Worksheet_8.1_Deep_Learning_CNN_Fingerprints.ipynb",
                       "Worksheet_8.2_Deep_Learning_RNN_URL.ipynb"),
        "data": ("fingerprints/", "url_data_small_deep_learning.csv",
                 "url_data_mega_deep_learning.csv.zip"),
        "libraries": ("tensorflow", "keras", "torch", "sklearn"),
        "concepts": (
            "Two architectures against two shapes of data: a convolutional network over fingerprint "
            "images, and a recurrent network over URL character sequences. Layers, activations, loss "
            "and optimiser; batch size and epochs; and reading a training curve for overfitting. Why a "
            "sequence model can learn from a URL what hand-built features in Module 3 had to be told."
        ),
    },
    {
        "number": 9, "title": "Artificial Intelligence Introduction and Theory",
        "deck": "09-artificial-intelligence-introduction-and-theory",
        "worksheets": ("Worksheet_9.1_Classification_with_Embeddings.ipynb",
                       "Worksheet_9.2_Unsupervised_Learning_with_Embeddings.ipynb",
                       "Worksheet_9.3_PyTorch_in_20_Minutes.ipynb",
                       "Worksheet_9.4_Tokenizers_and_Embeddings.ipynb",
                       "Worksheet_9.5_Attention_and_Your_First_GPT.ipynb",
                       "Worksheet_9.6_Fine_Tuning_and_Poisoning.ipynb"),
        "data": ("Modified_SQL_Dataset.csv", "enriched_sql_injection_dataset_1000.csv",
                 "clean_email.csv", "tiny_corpus.txt", "cyber_corpus.txt", "bpe_merges.json"),
        "libraries": ("sentence_transformers", "torch", "sklearn"),
        "concepts": (
            "The path from embeddings to a transformer. 9.1 and 9.2 classify and cluster SQL-injection "
            "payloads with sentence embeddings. 9.3 is PyTorch mechanics: tensors, autograd, a training "
            "loop. 9.4 builds a byte-pair tokenizer. 9.5 implements attention and trains a small GPT on "
            "a cyber corpus. 9.6 fine-tunes it and then poisons the fine-tuning data to show what a "
            "corrupted training set does to a model that looks healthy."
        ),
    },
    {
        "number": 10, "title": "Prompt Engineering", "deck": "10-prompt-engineering",
        "worksheets": ("Worksheet_10.1_Programmatic_LLM_Interaction.ipynb",
                       "Worksheet_10.2_Classification_with_LLMs.ipynb"),
        "data": ("cli_commands.txt", "cpu-train-b.csv", "cpu-test-b.csv", "vehicles/"),
        "libraries": ("openai",),
        "concepts": (
            "Calling an LLM from code rather than a chat box: system versus user messages, temperature "
            "and max tokens, few-shot examples, asking for structured output you can parse, and passing "
            "an image. 10.2 uses the model as a classifier over security text and compares it with the "
            "trained classifiers from Module 4. On Databricks both worksheets go through the "
            "OpenAI-compatible client against the workspace serving endpoint, not an Anthropic key."
        ),
    },
    {
        "number": 11, "title": "AI Components", "deck": "11-ai-components",
        "worksheets": ("Worksheet_11.1_AI_RAG_CVEs.ipynb",
                       "Worksheet_11.2_Building_Agent_Tools.ipynb"),
        "data": ("nvd_vulnerabilities_with_os.csv",),
        "libraries": ("langchain", "langchain_community"),
        "concepts": (
            "The pieces an LLM application is assembled from. 11.1 builds retrieval-augmented generation "
            "over an NVD vulnerability export: chunking, embedding, a vector store, and a prompt that "
            "cites what it retrieved. 11.2 writes tools an agent can call — a schema, a docstring the "
            "model actually reads, and a return value it can act on."
        ),
    },
    {
        "number": 12, "title": "Model Context Protocol", "deck": "12-model-context-protocol",
        "worksheets": ("Worksheet_12.1_Building_an_MCP_Server.ipynb",),
        "data": (),
        "libraries": ("mcp", "fastmcp", "langchain_mcp_adapters"),
        "concepts": (
            "Model Context Protocol as the interface between a model and the tools it can reach: what a "
            "server exposes (tools, resources, prompts), how a client discovers them, and the stdio "
            "transport the worksheet's server runs over. Why a protocol beats a bespoke tool wrapper "
            "once more than one client needs the same capability."
        ),
    },
    {
        "number": 13, "title": "AI Agents", "deck": "13-ai-agents",
        "worksheets": ("Worksheet_13.1_Single_Email_Classifier.ipynb",
                       "Worksheet_13.2_Tool_Calling_Agent.ipynb",
                       "Worksheet_13.3_Conditional_Routing.ipynb",
                       "Worksheet_13.4_human_in_the_loop.ipynb",
                       "Worksheet_13.5_multi_agent_supervisor.ipynb"),
        "data": (),
        "libraries": ("langgraph", "langchain", "langgraph_supervisor"),
        "concepts": (
            "Agents as state graphs in LangGraph, built up over five worksheets: a single-node email "
            "classifier, an agent that calls tools in a loop, conditional routing on the state, an "
            "interrupt that puts a human in the loop before an action commits, and a supervisor "
            "delegating to several specialist agents. Where each pattern earns its complexity, and "
            "where a plain function call would have done."
        ),
    },
    {
        "number": 14, "title": "Red Teaming AI", "deck": "14-red-teaming-ai",
        "worksheets": (), "data": (), "libraries": (),
        "concepts": (
            "Testing an AI system the way an attacker would: prompt injection through content the model "
            "reads, jailbreaks against the system prompt, exfiltration through an agent's tools, and "
            "supply-chain risk in models and datasets. Discussion module with no lab in the repo; the "
            "Final Project is where the technique gets used."
        ),
    },
    {
        "number": 15, "title": "Final Project", "deck": "15-final-project",
        "worksheets": (), "data": (),
        "libraries": ("openai", "requests"),
        "concepts": (
            "The capstone: build and evaluate an agent that probes OWASP Juice Shop. The scaffold lives "
            "in final_project/ — an agent package with HTTP and recon tools, an eval harness and a "
            "scoring script, a design-document template, a write-up template and a rubric. It runs "
            "locally against a Docker Compose stack, not on Databricks, because it needs a live target."
        ),
    },
)


_COURSE_SKILL = """# {name}

Module {number} of AI Cyber Bootcamp 2026: {title}.

## What this module teaches

{concepts}

## Deck

`{deck}` — read a page's speaker notes with the deck-notes tool.

## Labs

{labs}

## Data

{data}

## Libraries

{libraries}
"""


def _bullets(items, empty: str) -> str:
    return "\n".join(f"- `{i}`" for i in items) if items else empty


def build_course_modules(dest: Path) -> list[dict]:
    entries = []
    for m in MODULES:
        name = f"course-module-{m['number']:02d}"
        labs = _bullets(
            m["worksheets"],
            "This module has no lab notebook in the repo — it is deck and discussion only."
            if m["number"] != 15 else
            "No worksheet. The capstone scaffold is `final_project/`, run locally.",
        )
        body = _COURSE_SKILL.format(
            name=name, number=m["number"], title=m["title"], concepts=m["concepts"],
            deck=m["deck"], labs=labs,
            data=_bullets(m["data"], "No data files of its own."),
            libraries=_bullets(m["libraries"], "No libraries beyond the course baseline."),
        )
        description = (
            f"Module {m['number']} of AI Cyber Bootcamp 2026, {m['title']}: "
            + " ".join(m["concepts"].split())
        )
        if len(description) > DESCRIPTION_MAX_CHARS:
            description = description[:DESCRIPTION_MAX_CHARS].rsplit(" ", 1)[0].rstrip(",;:") + "…"
        rel = f"{name}/SKILL.md"
        (dest / name).mkdir(parents=True, exist_ok=True)
        (dest / rel).write_text(render_skill(name, description, body), encoding="utf-8")
        entries.append({"kind": "skill", "name": name, "description": description,
                        "path": rel, "listed": True})
    return entries


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC,
                        help="the claude-skills data-science suite (read-only)")
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST,
                        help="output tree; replaced wholesale on every run")
    args = parser.parse_args(argv)

    if args.dest.exists():
        shutil.rmtree(args.dest)
    args.dest.mkdir(parents=True)

    entries = build_data_science(args.src, args.dest) + build_course_modules(args.dest)
    entries.sort(key=lambda e: (e["kind"], e["name"]))
    (args.dest / "index.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    skills = sum(1 for e in entries if e["kind"] == "skill")
    refs = len(entries) - skills
    listed = [e for e in entries if e["listed"]]
    index_bytes = sum(len(e["name"]) + len(e["description"]) for e in listed)
    print(f"wrote {skills} skills and {refs} references to {args.dest}")
    print(f"prompt index: {len(listed)} entries, {index_bytes} bytes of names and descriptions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
