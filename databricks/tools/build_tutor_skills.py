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
    """Write the stripped router, subskills and kept references. Returns index entries."""
    entries: list[dict] = []

    def emit_skill(name: str, text: str, *, is_router: bool) -> None:
        meta, body = split_frontmatter(text)
        description = clean_description(meta["description"])
        out_body = strip_body(body, is_router=is_router)
        rel = f"{name}/SKILL.md"
        path = dest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_skill(name, description, out_body), encoding="utf-8")
        entries.append({"kind": "skill", "name": name, "description": description, "path": rel})

    emit_skill("data-science", (src / "SKILL.md").read_text(encoding="utf-8"), is_router=True)

    for skill_dir in sorted((src / "subskills").iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if skill_md.is_file():
            emit_skill(skill_dir.name, skill_md.read_text(encoding="utf-8"), is_router=False)

    ref_dir = dest / "references"
    ref_dir.mkdir(parents=True, exist_ok=True)
    for name in KEEP_REFERENCES:
        text = (src / "references" / f"{name}.md").read_text(encoding="utf-8")
        text = _tidy(_drop_lines(text))
        (ref_dir / f"{name}.md").write_text(text, encoding="utf-8")
        first = next((ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")), name)
        entries.append({
            "kind": "reference", "name": name,
            "description": first[:DESCRIPTION_MAX_CHARS],
            "path": f"references/{name}.md",
        })

    return entries
